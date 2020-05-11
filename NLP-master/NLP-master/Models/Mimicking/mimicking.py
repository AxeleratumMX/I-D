from keras.models import Sequential
from keras.layers import Bidirectional
from keras.layers import LSTM
from keras.layers import TimeDistributed
from keras.layers import Dense
import keras.backend as kb
from gensim.models.keyedvectors import KeyedVectors
import numpy as np
from keras.models import load_model
from keras.callbacks import TensorBoard, ModelCheckpoint


# Modifiable constants
LSTM_HIDDEN_UNITS = 150
CHAR_VECTOR_WORD_SIZE = 20
VECTOR_WORD_SIZE = 300

EPOCHS = 200
INITIAL_EPOCH = 0
BATCH_SIZE = 32
VALIDATION_SPLIT = 0.1
MODEL_PATH = 'Model/run_1/model-{epoch:02d}.hdf5'
MODEL_RESTORE_PATH = 'Model/run_1/model-%d.hdf5'
TB_LOG_PATH = 'Logs/run_1'

# Non modifiable constants
DEFAULT_DICTIONARY = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e':5,'f':6,'g':7,'h':8,'i':9,'j':10,'k':11,'l':12,'m':13,'n':14,'ñ':15,'o':16,'p':17,'q':18,'r':19,'s':20,'t':21,'u':22,'v':23,'w':24,'x':25,'y':26,'z':27,'á':28,'é':29,'í':30,'ó':31,'ú':32,'1':33,'2':34,'3':35,'4':36,'5':37,'6':38,'7':39,'8':40,'9':41,'0':42}

# Important functions
def euclidean_distance_loss(y_true, y_pred):
    return kb.sqrt(kb.sum(kb.square(y_pred - y_true), axis=-1))

def word_to_vector_by_char(word, dictionary, size=20):
    extended_dictionary = dictionary
    # Unknown char
    extended_dictionary['UNK'] = len(extended_dictionary)
    # Pad char
    extended_dictionary['*'] = len(extended_dictionary)
    

    if(len(word) > size):
        vector = [extended_dictionary['*']] * size
    else: 
        vector = [extended_dictionary['*']] * (size - len(word))
        vector += [ extended_dictionary[character if character in extended_dictionary else 'UNK' ] for character in word.lower() ]
        
    return vector

# Printing available devices
if(len(kb.tensorflow_backend._get_available_gpus())):
    print('--------------------- GPUS AVAILABLE ---------------------')
    print(kb.tensorflow_backend._get_available_gpus())

# Loading data
print('Loading vectors...')
wordvectors_file_vec = 'wiki.es.vec'
wordvectors = KeyedVectors.load_word2vec_format(wordvectors_file_vec)
vocabulary = list(wordvectors.vocab.keys())
print('%d vectors loaded' % len(vocabulary))

# Generating data as expected
print('Generating data...')
X = np.asarray([[word_to_vector_by_char(key, DEFAULT_DICTIONARY, CHAR_VECTOR_WORD_SIZE)] for key in vocabulary])
Y = np.asarray([[wordvectors[key]] for key in vocabulary])
print('Generated data: X=%s Y=%s' % (X.shape, Y.shape))



if INITIAL_EPOCH > 0:
    print('Restoring model from %s...' % (MODEL_RESTORE_PATH % INITIAL_EPOCH))
    model = load_model((MODEL_RESTORE_PATH % INITIAL_EPOCH))
else:
    # Loading the model
    print('Generating model...')
    model = Sequential()
    model.add(Bidirectional(LSTM(LSTM_HIDDEN_UNITS, return_sequences=True), input_shape=(1, CHAR_VECTOR_WORD_SIZE), merge_mode='concat'))
    model.add(TimeDistributed(Dense(VECTOR_WORD_SIZE, activation='tanh')))

    print('Compiling model...')
    model.compile(loss=euclidean_distance_loss, optimizer='adam')

model.summary()


# Loading tensorboard dir
print('Generating callbacks...')
tensorboard = TensorBoard(TB_LOG_PATH)
checkpoint = ModelCheckpoint(MODEL_PATH, verbose=0, save_best_only=False)

# Training model
print('Training...')
history = model.fit(
    x=X, 
    y=Y,
    batch_size=BATCH_SIZE, 
    epochs=EPOCHS,
    verbose=1, 
    callbacks=[tensorboard, checkpoint],
    validation_split=VALIDATION_SPLIT,
    shuffle=True, 
    initial_epoch=INITIAL_EPOCH
)

            
