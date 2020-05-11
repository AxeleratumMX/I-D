import tensorflow as tf
import numpy as np
import tokenization
import modeling
from extract_features import convert_examples_to_features, model_fn_builder, input_fn_builder, InputExample



class BertEmbedding():
    def __init__(
        self,
        vocab_file,
        bert_config_file,
        init_checkpoint,
        # Processing parameters
        max_seq_length=128,
        batch_size=32, 
        layer_indexes=[-1],
        concatenate_layers=False,
        # TPU parameters
        use_tpu=False,
        master=None, 
        num_tpu_cores=8, 
        # Use of one hot embeddings
        use_one_hot_embeddings=False,
        log_verbosity=tf.logging.INFO
    ):

        ''' Assign variables used in multiple methods '''
        self.layer_indexes = layer_indexes
        self.max_seq_length = max_seq_length
        self.concatenate_layers = concatenate_layers
        

        tf.logging.set_verbosity(log_verbosity)

        ''' Generate BERT configuration '''
        bert_config = modeling.BertConfig.from_json_file(bert_config_file)

        ''' Generates the run configuration '''
        is_per_host = tf.contrib.tpu.InputPipelineConfig.PER_HOST_V2
        run_config = tf.contrib.tpu.RunConfig(
            master=master,
            tpu_config=tf.contrib.tpu.TPUConfig(
                num_shards=num_tpu_cores,
                per_host_input_for_training=is_per_host
            )
        )

        ''' Generates the model function '''
        model_fn = model_fn_builder(
            bert_config=bert_config,
            init_checkpoint=init_checkpoint,
            layer_indexes=self.layer_indexes,
            use_tpu=use_tpu,
            use_one_hot_embeddings=use_one_hot_embeddings
        )

        ''' Instanciates estimator for running '''
        self.estimator = tf.contrib.tpu.TPUEstimator(
            use_tpu=use_tpu,
            model_fn=model_fn,
            config=run_config,
            predict_batch_size=batch_size
        )

        
        self.tokenizer = tokenization.FullTokenizer(vocab_file=vocab_file, do_lower_case=False)

    def __normalize_text(self, text):
        normalized = tokenization.convert_to_unicode(text)
        normalized = normalized.strip()
        return normalized

    def __convert_text_to_examples(self, text):
        unique_id = 0
        examples = []
        paragraphs = text.split('\n')
        for sentence in paragraphs:
            examples.append(InputExample(unique_id=unique_id, text_a=self.__normalize_text(sentence), text_b=None))
            unique_id += 1
        return examples

    def vectorize(self, text, log_verbosity=tf.logging.INFO):
        ''' Converts text to features '''
        features = convert_examples_to_features(
            examples=self.__convert_text_to_examples(text), 
            seq_length=self.max_seq_length, 
            tokenizer=self.tokenizer
        )

        
        tf.logging.set_verbosity(log_verbosity)

        ''' Inverse mapping from id to feature '''
        unique_id_to_feature = {}
        
        for feature in features:
            unique_id_to_feature[feature.unique_id] = feature

        ''' Generates the function for feeding inputs '''
        input_fn = input_fn_builder(features=features, seq_length=self.max_seq_length)


        ''' Predicts embeddings '''
        results = self.estimator.predict(input_fn, yield_single_examples=True) 


        ''' Under the assumption tha text contains multiple paragraphs, this array will contain them. Process paragraphs.  '''
        paragraphs = []

        for result in results:
            unique_id = int(result['unique_id'])
            feature = unique_id_to_feature[unique_id]
            
            all_features = []

            ''' Iterates tokens in paragraph. Process words. '''
            for (i, token) in enumerate(feature.tokens):

                all_layers = []
                
                ''' Iterates over all requested layer outputs. Process layers.'''
                for (j, layer_index) in enumerate(self.layer_indexes):
                    layer_output = result['layer_output_%d' % j]
                    layer_values = [round(float(x), 6) for x in layer_output[i:(i + 1)].flat]
                    if self.concatenate_layers:
                        all_layers += layer_values
                    else:
                        all_layers.append(layer_values)

                all_features.append(np.asarray(all_layers))
            paragraphs.append(np.asarray(all_features))
        return paragraphs


def load_model():
    return BertEmbedding(
        vocab_file='multi_cased_L-12_H-768_A-12/vocab.txt',
        bert_config_file='multi_cased_L-12_H-768_A-12/bert_config.json', 
        init_checkpoint='multi_cased_L-12_H-768_A-12/bert_model.ckpt',
        # Processing parameters
        max_seq_length=128,
        batch_size=32, 
        layer_indexes=[-1, -2, -3, -4],
        concatenate_layers=True,
        # TPU parameters
        use_tpu=False,
        master=None, 
        num_tpu_cores=8, 
        # Use of one hot embeddings
        use_one_hot_embeddings=False,
        log_verbosity=tf.logging.ERROR
    )

def vectorize(model, text):
    return model.vectorize(
        text, 
        log_verbosity=tf.logging.ERROR
    )