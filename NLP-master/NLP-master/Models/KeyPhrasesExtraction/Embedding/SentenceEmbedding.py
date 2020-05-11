import tensorflow as tf
import modeling as modeling
import tokenization as tokenization
import os


class InputExample(object):
    def __init__(self, unique_id, text_a, text_b):
        self.unique_id = unique_id
        self.text_a = text_a
        self.text_b = text_b


class InputFeatures(object):
  """A single set of features of data."""

  def __init__(self, unique_id, tokens, input_ids, input_mask, input_type_ids):
    self.unique_id = unique_id
    self.tokens = tokens
    self.input_ids = input_ids
    self.input_mask = input_mask
    self.input_type_ids = input_type_ids


class Model:

    def __init__(self,
                 bert_config_file="multi_cased_L-12_H-768_A-12\\bert_config.json",
                 vocab_file="multi_cased_L-12_H-768_A-12\\vocab.txt",
                 do_lower_case=False,
                 TPU_address=None,
                 num_tpu_cores=8,
                 max_seq_length=128,
                 init_checkpoint="multi_cased_L-12_H-768_A-12\\bert_model.ckpt",
                 use_tpu=False,
                 use_one_hot_embeddings=True,
                 layer_indexes=[-1],
                 batch_size=8):

        self.bert_config_file = bert_config_file
        self.vocab_file = vocab_file
        self.do_lower_case = do_lower_case
        self.TPU_address = TPU_address
        self.num_tpu_cores = num_tpu_cores
        self.max_seq_length = max_seq_length
        self.init_checkpoint = init_checkpoint
        self.use_tpu = use_tpu
        self.use_one_hot_embeddings = use_one_hot_embeddings
        self.layer_indexes = layer_indexes
        self.batch_size = batch_size

        bert_config = modeling.BertConfig.from_json_file(bert_config_file)

        tokenizer = tokenization.FullTokenizer(vocab_file=vocab_file, do_lower_case=do_lower_case)

        run_config = tf.contrib.tpu.RunConfig(
            master=TPU_address,
            tpu_config=tf.contrib.tpu.TPUConfig(
                num_shards=num_tpu_cores,
                per_host_input_for_training=tf.contrib.tpu.InputPipelineConfig.PER_HOST_V2))

        model_fn = self.model_fn_builder(
            bert_config=bert_config,
            init_checkpoint=init_checkpoint,
            layer_indexes=layer_indexes,
            use_tpu=use_tpu,
            use_one_hot_embeddings=use_one_hot_embeddings)

        # If TPU is not available, this will fall back to normal Estimator on CPU or GPU.
        estimator = tf.contrib.tpu.TPUEstimator(
            use_tpu=use_tpu,
            model_fn=model_fn,
            config=run_config,
            predict_batch_size=batch_size)

        self.estimator = estimator
        self.tokenizer = tokenizer

    def read_sentences(self, paragraphs):
        """Build and assign id to input paragraphs"""
        return [InputExample(unique_id=i, text_a=x, text_b=None) for i, x in enumerate(paragraphs)]

    def convert_examples_to_features(self, examples, seq_length, tokenizer):
        """Loads a data file into a list of `InputBatch`s."""

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
                _truncate_seq_pair(tokens_a, tokens_b, seq_length - 3)
            else:
                # Account for [CLS] and [SEP] with "- 2"
                if len(tokens_a) > seq_length - 2:
                    tokens_a = tokens_a[0:(seq_length - 2)]

            # The convention in BERT is:
            # (a) For sequence pairs:
            #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
            #  type_ids: 0     0  0    0    0     0       0 0     1  1  1  1   1 1
            # (b) For single sequences:
            #  tokens:   [CLS] the dog is hairy . [SEP]
            #  type_ids: 0     0   0   0  0     0 0
            #
            # Where "type_ids" are used to indicate whether this is the first
            # sequence or the second sequence. The embedding vectors for `type=0` and
            # `type=1` were learned during pre-training and are added to the wordpiece
            # embedding vector (and position vector). This is not *strictly* necessary
            # since the [SEP] token unambiguously separates the sequences, but it makes
            # it easier for the model to learn the concept of sequences.
            #
            # For classification tasks, the first vector (corresponding to [CLS]) is
            # used as as the "sentence vector". Note that this only makes sense because
            # the entire model is fine-tuned.
            tokens = []
            input_type_ids = []
            tokens.append("[CLS]")
            input_type_ids.append(0)

            for token in tokens_a:
                tokens.append(token)
                input_type_ids.append(0)

            tokens.append("[SEP]")
            input_type_ids.append(0)

            if tokens_b:
                for token in tokens_b:
                    tokens.append(token)
                    input_type_ids.append(1)

            tokens.append("[SEP]")
            input_type_ids.append(1)

            input_ids = tokenizer.convert_tokens_to_ids(tokens)

            # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
            input_mask = [1] * len(input_ids)

            # Zero-pad up to the sequence length.
            while len(input_ids) < seq_length:
                input_ids.append(0)
                input_mask.append(0)
                input_type_ids.append(0)

            assert len(input_ids) == seq_length
            assert len(input_mask) == seq_length
            assert len(input_type_ids) == seq_length

            if ex_index < 5:
                tf.logging.info("*** Example ***")
                tf.logging.info("unique_id: %s" % example.unique_id)
                tf.logging.info("tokens: %s" % " ".join([tokenization.printable_text(x) for x in tokens]))
                tf.logging.info("input_ids: %s" % " ".join([str(x) for x in input_ids]))
                tf.logging.info("input_mask: %s" % " ".join([str(x) for x in input_mask]))
                tf.logging.info("input_type_ids: %s" % " ".join([str(x) for x in input_type_ids]))

            features.append(
                InputFeatures(
                    unique_id=example.unique_id,
                    tokens=tokens,
                    input_ids=input_ids,
                    input_mask=input_mask,
                    input_type_ids=input_type_ids))

        return features

    def input_fn_builder(self, features, seq_length):
        """Creates an `input_fn` closure to be passed to TPUEstimator."""

        all_unique_ids = []
        all_input_ids = []
        all_input_mask = []
        all_input_type_ids = []

        for feature in features:
            all_unique_ids.append(feature.unique_id)
            all_input_ids.append(feature.input_ids)
            all_input_mask.append(feature.input_mask)
            all_input_type_ids.append(feature.input_type_ids)

        def input_fn(params):
            """The actual input function."""
            batch_size = params["batch_size"]

            num_examples = len(features)

            # This is for demo purposes and does NOT scale to large data sets. We do
            # not use Dataset.from_generator() because that uses tf.py_func which is
            # not TPU compatible. The right way to load data is with TFRecordReader.
            d = tf.data.Dataset.from_tensor_slices({
                "unique_ids": tf.constant(all_unique_ids, shape=[num_examples], dtype=tf.int32),
                "input_ids": tf.constant(all_input_ids, shape=[num_examples, seq_length], dtype=tf.int32),
                "input_mask": tf.constant(all_input_mask, shape=[num_examples, seq_length], dtype=tf.int32),
                "input_type_ids": tf.constant(all_input_type_ids, shape=[num_examples, seq_length], dtype=tf.int32),
            })

            d = d.batch(batch_size=batch_size)  # , drop_remainder=False)
            return d

        return input_fn

    def model_fn_builder(self, bert_config, init_checkpoint, layer_indexes, use_tpu, use_one_hot_embeddings):
        """Returns `model_fn` closure for TPUEstimator."""

        def model_fn(features, labels, mode, params):  # pylint: disable=unused-argument
            """The `model_fn` for TPUEstimator."""

            unique_ids = features["unique_ids"]
            input_ids = features["input_ids"]
            input_mask = features["input_mask"]
            input_type_ids = features["input_type_ids"]

            model = modeling.BertModel(
                config=bert_config,
                is_training=False,
                input_ids=input_ids,
                input_mask=input_mask,
                token_type_ids=input_type_ids,
                use_one_hot_embeddings=use_one_hot_embeddings)

            if mode != tf.estimator.ModeKeys.PREDICT:
                raise ValueError("Only PREDICT modes are supported: %s" % (mode))

            tvars = tf.trainable_variables()
            scaffold_fn = None
            (assignment_map, initialized_variable_names) = modeling.get_assignment_map_from_checkpoint(tvars,
                                                                                                       init_checkpoint)

            if use_tpu:

                def tpu_scaffold():
                    tf.train.init_from_checkpoint(init_checkpoint, assignment_map)
                    return tf.train.Scaffold()

                scaffold_fn = tpu_scaffold
            else:
                tf.train.init_from_checkpoint(init_checkpoint, assignment_map)

            tf.logging.info("**** Trainable Variables ****")
            for var in tvars:
                init_string = ""
                if var.name in initialized_variable_names:
                    init_string = ", *INIT_FROM_CKPT*"
                tf.logging.info("  name = %s, shape = %s%s", var.name, var.shape, init_string)

            all_layers = model.get_all_encoder_layers()

            predictions = {"unique_id": unique_ids, }

            for (i, layer_index) in enumerate(layer_indexes):
                predictions["layer_output_%d" % i] = all_layers[layer_index]

            output_spec = tf.contrib.tpu.TPUEstimatorSpec(mode=mode, predictions=predictions, scaffold_fn=scaffold_fn)

            return output_spec

        return model_fn

    def sentence_to_vector(self, sentences):

        examples = self.read_sentences(sentences)

        features = self.convert_examples_to_features(examples=examples, seq_length=self.max_seq_length, tokenizer=self.tokenizer)

        unique_id_to_feature = {}
        for feature in features:
            unique_id_to_feature[feature.unique_id] = feature

        input_fn = self.input_fn_builder(features=features, seq_length=self.max_seq_length)

        embeddings = []
        for result in self.estimator.predict(input_fn, yield_single_examples=True):
            unique_id = int(result["unique_id"])
            feature = unique_id_to_feature[unique_id]

            for (i, token) in enumerate(feature.tokens):
                if token == "[CLS]":
                    for (j, layer_index) in enumerate(self.layer_indexes):
                        layer_output = result["layer_output_%d" % j]
                        values = [round(float(x), 6) for x in layer_output[i:(i + 1)].flat]

            embed_sentence = {'line_index': unique_id, 'feature_vector': values}
            embeddings.append(embed_sentence)

        return embeddings
