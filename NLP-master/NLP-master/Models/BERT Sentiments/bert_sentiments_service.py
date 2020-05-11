# coding=utf-8

"""BERT finetuning runner."""

from __future__ import absolute_import, division, print_function

import sys

import argparse
import collections
import logging
import logging.handlers
import os
import random

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.distributed import DistributedSampler
from torch.utils.data.sampler import RandomSampler, SequentialSampler

import tokenization
from modeling import BertConfig, BertForSequenceClassification
#from bert_sentiments_service_processor import Sentihood_NLI_B_Processor, Sentihood_NLI_M_Processor
from bert_sentiments_service_processor import Sentihood_NLI_B_Processor, Sentihood_NLI_M_Processor
from bert_sentiments_service_utils import Review, NonFeaturesGeneratedException, EmptyReviewsException, InputFeatures

from flask import Flask, request
from flask_restful import Resource, Api

LOGGER_NAME = 'bert_utils'
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def convert_examples_to_features(examples, max_seq_length, tokenizer):
    """Loads a data file into a list of `InputBatch`s."""

    logger.debug('Converting {} examples to features'.format(len(examples)))

    features = []
    for (ex_index, example) in enumerate(examples):
        tokens_a = tokenizer.tokenize(example.text_a)

        tokens_b = None
        if example.text_b:
            tokens_b = tokenizer.tokenize(example.text_b)

        if tokens_b:
            # Modifies `tokens_a` and `tokens_b` in place so that the total
            # length is less than the specified length.
            # Account for [CLS], [SEP], [SEP] with "- 3"
            _truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
        else:
            # Account for [CLS] and [SEP] with "- 2"
            if len(tokens_a) > max_seq_length - 2:
                tokens_a = tokens_a[0:(max_seq_length - 2)]

        # The convention in BERT is:
        # (a) For sequence pairs:
        #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
        #  type_ids: 0   0  0    0    0     0       0 0    1  1  1  1   1 1
        # (b) For single sequences:
        #  tokens:   [CLS] the dog is hairy . [SEP]
        #  type_ids: 0   0   0   0  0     0 0
        #
        # Where "type_ids" are used to indicate whether this is the first
        # sequence or the second sequence. The embedding vectors for `type=0` and
        # `type=1` were learned during pre-training and are added to the wordpiece
        # embedding vector (and position vector). This is not *strictly* necessary
        # since the [SEP] token unambigiously separates the sequences, but it makes
        # it easier for the model to learn the concept of sequences.
        #
        # For classification tasks, the first vector (corresponding to [CLS]) is
        # used as as the "sentence vector". Note that this only makes sense because
        # the entire model is fine-tuned.
        tokens = []
        segment_ids = []
        tokens.append("[CLS]")
        segment_ids.append(0)
        for token in tokens_a:
            tokens.append(token)
            segment_ids.append(0)
        tokens.append("[SEP]")
        segment_ids.append(0)

        if tokens_b:
            for token in tokens_b:
                tokens.append(token)
                segment_ids.append(1)
            tokens.append("[SEP]")
            segment_ids.append(1)

        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1] * len(input_ids)

        # Zero-pad up to the sequence length.
        while len(input_ids) < max_seq_length:
            input_ids.append(0)
            input_mask.append(0)
            segment_ids.append(0)

        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length

        features.append(
                InputFeatures(
                        input_ids=input_ids,
                        input_mask=input_mask,
                        segment_ids=segment_ids
                        ))
    return features


def _truncate_seq_pair(tokens_a, tokens_b, max_length):
    """Truncates a sequence pair in place to the maximum length."""

    # This is a simple heuristic which will always truncate the longer sequence
    # one token at a time. This makes more sense than truncating an equal percent
    # of tokens from each, since if one sequence is very short then each token
    # that's truncated likely contains more information than a longer sequence.
    while True:
        total_length = len(tokens_a) + len(tokens_b)
        if total_length <= max_length:
            break
        if len(tokens_a) > len(tokens_b):
            tokens_a.pop()
        else:
            tokens_b.pop()


class BertSentiments:
    def __init__(self, bert_config_file, init_checkpoint, vocab_file, max_seq_length, task_name, do_lower_case, seed, local_rank, no_cuda, batch_size):
        self.max_seq_length = max_seq_length
        self.batch_size = batch_size
        self.model, self.tokenizer, self.processor, self.device = self.load_model(bert_config_file, init_checkpoint, vocab_file, max_seq_length, task_name, do_lower_case, seed, local_rank, no_cuda)


    def load_model(self, bert_config_file, init_checkpoint, vocab_file, max_seq_length, task_name, do_lower_case, seed, local_rank, no_cuda):

        logger.info('Calling torch.cuda.current_device [PATCH]')

        torch.cuda.current_device()
                
        logger.info('[ Local rank: {} ] [ No cuda: {} ] [ Cuda available: {} ]'.format(local_rank, no_cuda, torch.cuda.is_available()))

        if local_rank == -1 or no_cuda:
            device = torch.device("cuda" if torch.cuda.is_available() and not no_cuda else "cpu")
            n_gpu = torch.cuda.device_count()
        else:
            device = torch.device("cuda", local_rank)
            n_gpu = 1
            # Initializes the distributed backend which will take care of sychronizing nodes/GPUs
            torch.distributed.init_process_group(backend='nccl')

        logger.info("[ Device: {} ] [ n_gpu: {} ] [ distributed inference: {} ]".format(device, n_gpu, bool(local_rank != -1)))

        logger.info("[ Using seed {} ]".format(seed))

        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        
        if n_gpu > 0:
            torch.cuda.manual_seed_all(seed)

        logger.info("Loading BERT config file from {}".format(bert_config_file))

        bert_config = BertConfig.from_json_file(bert_config_file)

        if max_seq_length > bert_config.max_position_embeddings:
            raise ValueError(
                "Cannot use sequence length {} because the BERT model was only trained up to sequence length {}".format(
                max_seq_length, bert_config.max_position_embeddings))

        
        # prepare dataloaders
        processors = {
            "sentihood_NLI_B": Sentihood_NLI_B_Processor,
            "sentihood_NLI_M": Sentihood_NLI_M_Processor,
        }

        logger.info("Infering for {} task".format(task_name))

        processor = processors[task_name]()
        label_list = processor.get_labels()

        logger.info("Creating tokenizer. [ Vocab file: {} ] [ Lower case: {} ]".format(vocab_file, do_lower_case))
        tokenizer = tokenization.FullTokenizer(vocab_file=vocab_file, do_lower_case=do_lower_case)

        # model and optimizer
        model = BertForSequenceClassification(bert_config, len(label_list))
        model.load_state_dict(torch.load(init_checkpoint, map_location='cpu'))
                
        model.to(device)

        if local_rank != -1:
            model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank],
                                                            output_device=local_rank)
        elif n_gpu > 1:
            model = torch.nn.DataParallel(model)

        return model, tokenizer, processor, device
    
    def predict(self, model, reviews, tokenizer, processor, device, max_seq_length):
        
        logger.debug('Received {} reviews'.format( len(reviews) ))

        model.eval()
        


        examples = processor.convert_to_examples(reviews)
        
        logger.debug('{} reviews converted to {} examples'.format( len(reviews), len(examples) ))

        features = convert_examples_to_features(examples, max_seq_length, tokenizer)

        if len(features) <= 0:
            raise NonFeaturesGeneratedException

        logger.info('Predicting. [ Reviews: {} ] [ Features: {}]'.format(len(reviews), len(features)))        

        all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
        all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
        all_segment_ids = torch.tensor([f.segment_ids for f in features], dtype=torch.long)

        logger.debug('Features converted to tensors')

        data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids)

        logger.debug('Dataset generated')

        dataloader = DataLoader(data, batch_size=self.batch_size, shuffle=False)

        logger.debug('Dataloader generated')

        outputs = None

        for input_ids, input_mask, segment_ids in dataloader:

            logger.debug('Starting with batch')

            input_ids = input_ids.to(device)
            input_mask = input_mask.to(device)
            segment_ids = segment_ids.to(device)

            logger.debug('Features to device completed')

            with torch.no_grad():
                logger.debug('Infering')
                logits = model(input_ids, segment_ids, input_mask)
                logger.debug('Softmaxing')
                logits = F.softmax(logits, dim=-1)
                logits = logits.detach().cpu().numpy()
                
                logger.debug('Concatenating to output')

                if outputs is None:
                    outputs = logits
                else:
                    outputs = np.concatenate([outputs, logits])

                logger.info('Concatenated to output. [ Shape: {} ]'.format(outputs.shape))

        logger.debug('Adding output to examples')
        for output_idx, output in enumerate(outputs):
            examples[output_idx].output = output

        logger.debug('Processing examples')
        return processor.convert_from_examples(examples)

    def infer(self, reviews):
        if len(reviews) <= 0:
            raise EmptyReviewsException

        return self.predict(self.model, reviews, self.tokenizer, self.processor, self.device, self.max_seq_length)


class BertSentimentsApi(Resource):

    ERROR_CODE = 400

    def __init__(self, bert_sentiments):
        self.bert_sentiments = bert_sentiments           

    def post(self):
        message = None

        if request.is_json:    
            try:        
                reviews = [ Review(review['id'], review['context'], review['review']) for review in request.json  ]
            except:
                message = 'The input is JSON but probably it does not have the correct format'

            try:
                return self.bert_sentiments.infer(reviews)
            except NonFeaturesGeneratedException:
                message = 'Any target was found'
            except EmptyReviewsException:
                message = 'The input was empty'
            except Exception as e:
                message = 'Something went wrong. {}'.format(e)

            


        else:
            message = 'Bad formed request. Possibly not JSON header contained.'

        logger.error(message)
        return message, self.ERROR_CODE

    def get(self):
        return 'Sentiments API working'


def run_api(bert_config_file, init_checkpoint, vocab_file, max_seq_length, task_name, do_lower_case, seed, local_rank, no_cuda, batch_size, host, port):
    
    app = Flask(__name__)
    api = Api(app)

    bert_sentiments = BertSentiments(
        bert_config_file, 
        init_checkpoint, 
        vocab_file, 
        max_seq_length, 
        task_name, 
        do_lower_case, 
        seed, 
        local_rank, 
        no_cuda,
        batch_size
    )

    api.add_resource(
        BertSentimentsApi, 
        '/sentiments/',
        resource_class_kwargs={ 'bert_sentiments': bert_sentiments }
    )

    app.run(host=host, port=port)
    
 




def main():
    parser = argparse.ArgumentParser()

    ## Required parameters
    parser.add_argument("--task_name",
                        default=None,
                        type=str,
                        required=True,
                        choices=["sentihood_NLI_B", "sentihood_NLI_M"],
                        help="The name of the task to run.")
    parser.add_argument("--vocab_file",
                        default=None,
                        type=str,
                        required=True,
                        help="The vocabulary file that the BERT model was trained on.")
    parser.add_argument("--bert_config_file",
                        default=None,
                        type=str,
                        required=True,
                        help="The config json file corresponding to the pre-trained BERT model. \n"
                             "This specifies the model architecture.")
    parser.add_argument("--init_checkpoint",
                        default=None,
                        type=str,
                        required=True,
                        help="Initial checkpoint (usually from a pre-trained BERT model).")
    
    parser.add_argument("--do_lower_case",
                        default=False,
                        action='store_true',
                        help="Whether to lower case the input text. True for uncased models, False for cased models.")
    parser.add_argument("--max_seq_length",
                        default=128,
                        type=int,
                        help="The maximum total input sequence length after WordPiece tokenization. \n"
                             "Sequences longer than this will be truncated, and sequences shorter \n"
                             "than this will be padded.")    
    parser.add_argument("--no_cuda",
                        default=False,
                        action='store_true',
                        help="Whether not to use CUDA when available")
    parser.add_argument("--batch_size",
                        default=16,
                        type=int,
                        help="Processing batch size")
    parser.add_argument("--local_rank",
                        type=int,
                        default=-1,
                        help="local_rank for distributed training on gpus")
    parser.add_argument('--seed', 
                        type=int, 
                        default=42,
                        help="random seed for initialization")
    parser.add_argument('--host', 
                        type=str, 
                        default='0.0.0.0',
                        help="host where the service will run")
    parser.add_argument('--port', 
                        type=int, 
                        default=5000,
                        help="port where the service will run")
    parser.add_argument('--log_file', 
                        type=str, 
                        default=None,
                        help="File where log")
    
    args = parser.parse_args()

    if args.log_file is not None:
        file_handler = logging.handlers.RotatingFileHandler(args.log_file, maxBytes=10000, backupCount=1)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)


    run_api(
        args.bert_config_file, 
        args.init_checkpoint, 
        args.vocab_file, 
        args.max_seq_length, 
        args.task_name, 
        args.do_lower_case, 
        args.seed, 
        args.local_rank, 
        args.no_cuda,
        args.batch_size,
        args.host,
        args.port
    )
    

if __name__ == "__main__":
    main()
