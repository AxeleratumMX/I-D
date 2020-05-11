from Mimicking.fasttext import load_fasttext
import os

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from SkipThought.skip_thought import load_skip_thought_model

from SkipThought.skip_thought_generator import SkipThoughtDataGenerator
from SkipThought.data_reader import WikiDataReader, FilesDataReader
from keras.models import load_model

from keras.utils import multi_gpu_model

from scipy import spatial

import tensorflow as tf
import numpy as np

from keras.callbacks import Callback, TensorBoard, ModelCheckpoint
import keras.backend as kb

from SkipThought.mixed_tensorboard import Metric, Plot, MixedTensorBoard


flags = tf.flags
FLAGS = flags.FLAGS


flags.DEFINE_boolean('training', True, 'True if training. False for testing.')
flags.DEFINE_integer('sentence_vector_size', 500, 'Define the vector size for sentene embeddings')
flags.DEFINE_integer('max_words_per_sentence', 20, 'Define the words per sentence')
flags.DEFINE_integer('batch_size', 64, 'Define the batch size. Must be multpiple of 64.')
flags.DEFINE_integer('epochs', 100, 'Number of epochs')
flags.DEFINE_string('save_path', 'SkipThought', 'Folder where logs and model checkpoints will be saved')
flags.DEFINE_string('w2v_path', './Mimicking/wiki.es.vec', 'Path of mimicking vectors')
flags.DEFINE_integer('w2v_limit', 100, 'Limit of loaded words')
flags.DEFINE_string('files_path', 'C:/Users/Uriel Corona/Downloads/Wiki', 'Path of wiki plain texts')
flags.DEFINE_string('validate_path', './SkipThought/validate', 'Path of validate path')
flags.DEFINE_integer('samples_validation', 20, 'After these batches of training will be validated')
flags.DEFINE_string('test_text', 'El volcán Popocatépetl ha registrado una explosión y una emisión de ceniza que se ha elevado a tres kilómetros', 'Text used for testing')
flags.DEFINE_integer('checkpoint', -1, 'Checkpoint file')

FILES_PATH = FLAGS.files_path

STM_VECTOR_SIZE = FLAGS.sentence_vector_size

STM_WORDS_PER_SENTENCE = FLAGS.max_words_per_sentence
# Must be multiple of 64
STM_BATCH_SIZE = FLAGS.batch_size
EPOCHS = FLAGS.epochs
MODEL_PATH = FLAGS.save_path + '/Model/model-%d.hdf5'
TB_LOG_PATH = FLAGS.save_path + '/Logs/'
W2V_PATH = FLAGS.w2v_path
W2V_LIMIT = FLAGS.w2v_limit
VALIDATE_FILES = FLAGS.validate_path

SAMPLES_VALIDATION = FLAGS.samples_validation

CHECKPOINT = FLAGS.checkpoint

test_text = FLAGS.test_text

PAD_CHAR = '</s>'


def test_text_prediciton(w2v_model, st_model, test_text):
    words = test_text.split()[:STM_WORDS_PER_SENTENCE]
    pad_words = ([PAD_CHAR] * (STM_WORDS_PER_SENTENCE - len(words))) + words

    embeddings = w2v_model.vectorize([pad_words])
    prev_probs, next_probs = st_model.predict([embeddings])
    prev_probs_indexes = np.reshape(np.argmax(prev_probs, axis=2), (STM_WORDS_PER_SENTENCE,))
    next_probs_indexes = np.reshape(np.argmax(next_probs, axis=2), (STM_WORDS_PER_SENTENCE,))
            
    next_msg = ''
    prev_msg = ''
    
    for prob_idx in prev_probs_indexes:
        prev_msg += ' ' + w2v_model.vocabulary[prob_idx]

    for prob_idx in next_probs_indexes:
        next_msg += ' ' + w2v_model.vocabulary[prob_idx]

    return prev_msg, next_msg
    

gpus = kb.tensorflow_backend._get_available_gpus()
if(len(gpus)):
    print('--------------------- GPUS AVAILABLE ---------------------')
    print('Available gpus...')
    print(gpus)



tf.logging.set_verbosity(tf.logging.ERROR)



print('Loading word embedding model...')
w2v_model = load_fasttext(filepath=W2V_PATH, limit=W2V_LIMIT)


if(FLAGS.training):

    print('------------------ TRAINING ---------------------')
    print('Loading skip thought model...')

    st_model = load_skip_thought_model(
        encode_size=STM_VECTOR_SIZE, 
        embedding_words_per_sentence=STM_WORDS_PER_SENTENCE,
        lookup_table=w2v_model.lookup_table
    )

    num_batches = max(1, len(gpus))

    if(len(gpus) > 2):
        print('Using multi-gpu processing (%d)...' % len(gpus))
        st_model = multi_gpu_model(st_model, gpus=len(gpus) - 1)


    print('Compiling skip thought model...')

    st_model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['sparse_categorical_crossentropy', 'accuracy']
        )

    st_model.summary()


    print('Loading skip thought model training generator...')


    train_reader = FilesDataReader(folder=FILES_PATH) 
    
    st_train_generator = SkipThoughtDataGenerator(
                data_reader=train_reader, 
                fn_vectorize=w2v_model.vectorize, 
                fn_gen_prob=w2v_model.get_probabilities,
                words_per_sentence=STM_WORDS_PER_SENTENCE, 
                pad_char=PAD_CHAR, 
                batch_size=STM_BATCH_SIZE * num_batches,
            )

              
    print('Loading skip thought model validation generator...')
    validate_reader = FilesDataReader(folder=VALIDATE_FILES)
    
    st_validate_generator = SkipThoughtDataGenerator(
                    data_reader=validate_reader,
                    fn_vectorize=w2v_model.vectorize, 
                    fn_gen_prob=w2v_model.get_probabilities,
                    words_per_sentence=STM_WORDS_PER_SENTENCE, 
                    pad_char=PAD_CHAR, 
                    batch_size=STM_BATCH_SIZE * num_batches
    )
    

    print('Generating tensorboard...')

    tensorboard = MixedTensorBoard(
        plots=
            [
                Plot(name='loss', metrics=[
                    Metric(name='loss', step_name='training'),
                    Metric(name='loss', step_name='validating')
                ]),
                Plot(name='previous probabilities loss', metrics=[
                    Metric(name='previous_probabilities_loss', step_name='training'),
                    Metric(name='previous_probabilities_loss', step_name='validating')
                ]),
                Plot(name='next probabilities loss', metrics=[                    
                    Metric(name='next_probabilities_loss', step_name='training'),
                    Metric(name='next_probabilities_loss', step_name='validating')
                ]), 
                Plot(name='previous probabilities accuracy', metrics=[
                    Metric(name='previous_probabilities_acc', step_name='training'),
                    Metric(name='previous_probabilities_acc', step_name='validating')
                ]),
                Plot(name='next probabilities accuracy', metrics=[
                    Metric(name='next_probabilities_acc', step_name='training'),
                    Metric(name='next_probabilities_acc', step_name='validating')
                ]),
                Plot(name='test text', metrics=[
                    Metric(name='test_text', step_name='validating')
                ])
            ], 
        log_dir=TB_LOG_PATH)

    last_checkpoint = 0

    
    if CHECKPOINT >= 0:
        last_checkpoint = CHECKPOINT
        st_model.load_weights(MODEL_PATH % last_checkpoint)
   
    for epoch in range(EPOCHS):
        print('********** Epoch %d' % epoch)
        while st_train_generator.has_more_data():
            x, y = st_train_generator.get_data()
            hist = st_model.fit(x=x, y=y)

            tensorboard.add_checkpoint(history=hist.history, step_name='training', global_step=last_checkpoint)
            
            if(last_checkpoint % SAMPLES_VALIDATION == 0):
                print('********** Checkpoint %d' % last_checkpoint)

                if not st_validate_generator.has_more_data():
                    st_validate_generator.restart_generation()

                
                x_val, y_val = st_validate_generator.get_data()

                metrics_vals = st_model.evaluate(x=x_val, y=y_val)

                hist_val = {}
                for idx, val in enumerate(metrics_vals):
                    hist_val[st_model.metrics_names[idx]] = [val]


                
                prev_msg, next_msg = test_text_prediciton(
                            w2v_model=w2v_model, 
                            st_model=st_model, 
                            test_text=test_text
                        )

                hist_val['test_text'] = [('[%s] %s [%s]' % (prev_msg, test_text, next_msg))]

                
                st_model.save_weights(MODEL_PATH % last_checkpoint)
                tensorboard.add_checkpoint(history=hist_val, step_name='validating', global_step=last_checkpoint)
            
            

            last_checkpoint += 1
            

        st_train_generator.restart_generation()

    st_train_generator.end_generation()
    st_validate_generator.end_generation()

    tensorboard.close_writers()

        
             
else:
    print('------------------ TESTING ---------------------')
    print('Loading skip thought model...')

    st_model = load_skip_thought_model(
        encode_size=STM_VECTOR_SIZE, 
        embedding_words_per_sentence=STM_WORDS_PER_SENTENCE,
        lookup_table=w2v_model.lookup_table
    )

    print('Loading skip thought model weights...')
    st_model.load_weights((FLAGS.save_path + '/Model/model-%d.hdf5') % CHECKPOINT)
    
    prev_msg, next_msg = test_text_prediciton(
                            w2v_model=w2v_model, 
                            st_model=st_model, 
                            test_text=test_text
                        )

    
    print('*******************************************************************')    
    print('Initial text: ', FLAGS.test_text)
    print('*******************************************************************')
    print('Previous text: ', prev_msg)
    print('*******************************************************************')
    print('Next text: ', next_msg)
    print('*******************************************************************')


