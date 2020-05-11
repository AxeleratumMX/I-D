import sys
from keras.models import Sequential
from keras.models import load_model as lm
from keras.layers import Bidirectional
from keras.layers import LSTM
from keras.layers import TimeDistributed
from keras.layers import Dense
import keras.backend as kb
from keras.callbacks import TensorBoard, ModelCheckpoint
from gensim.models.keyedvectors import KeyedVectors
import tensorflow as tf
import numpy as np
from numba import jit


# # Modifiable constants
# LSTM_HIDDEN_UNITS = 150
# CHAR_VECTOR_WORD_SIZE = 20
# VECTOR_WORD_SIZE = 300

# class w2v():
#     def __init__(
#     ):
#         self.wordvectors_file_vec = wordvectors_file_vec
#         self.DEFAULT_DICTIONARY = DEFAULT_DICTIONARY
#         self.limit = limit

#     def __word_to_vector_by_char(self, word, dictionary, size=20):
#         extended_dictionary = dictionary
#         # Unknown char
#         extended_dictionary['UNK'] = len(extended_dictionary)
#         # Pad char
#         extended_dictionary['*'] = len(extended_dictionary)
#         if(len(word) > size):
#             vector = [extended_dictionary['*']] * size
#         else:
#             vector = [extended_dictionary['*']] * (size - len(word))
#             vector += [extended_dictionary[character if character in extended_dictionary else 'UNK']
#                        for character in word.lower()]
#         return vector
    
#     def load_vectors(self):
#         # print('Loading vectors...')
#         wordvectors = KeyedVectors.load_word2vec_format(self.wordvectors_file_vec, limit=self.limit)
#         # vocabulary = list(wordvectors.vocab.keys())
#         # print('%d vectors loaded' % len(vocabulary))
#         return wordvectors

# class mimick():
#     def __init__(
#         self,
#         EPOCH=200,
#         MODEL_RESTORE_PATH='Results Yoshio/Model/run_1/model-%d.hdf5'
#     ):
#         self.EPOCH = EPOCH
#         self.MODEL_RESTORE_PATH = MODEL_RESTORE_PATH
        
#     def __euclidean_distance_loss(self, y_true, y_pred):
#         return kb.sqrt(kb.sum(kb.square(y_pred - y_true), axis=-1))
    
#     def __create_model(self):
#         model = Sequential()
#         model.add(Bidirectional(LSTM(LSTM_HIDDEN_UNITS, return_sequences=True),input_shape=(1, CHAR_VECTOR_WORD_SIZE), merge_mode='concat'))
#         model.add(TimeDistributed(Dense(VECTOR_WORD_SIZE, activation='tanh')))
#         return model

#     def load_model(self):
#         model = self.__create_model()
#         model = load_model(self.MODEL_RESTORE_PATH % EPOCH, custom_objects={'__euclidean_distance_loss': __euclidean_distance_loss})
    
#     def vectorize(self, text, log_verbosity=tf.logging.INFO):
#         ''' Converts text to features '''
#         features = convert_examples_to_features(
#             examples=self.__convert_text_to_examples(text),
#             seq_length=self.max_seq_length,
#             tokenizer=self.tokenizer
#         )


class w2v_mimick():
    def __init__(
        self,
        wordvectors_file_vec='wiki.es.vec',
        w2v_limit=None,
        best_epoch=200,
        mimick_weights_file='Results Yoshio/Model/run_1/model-%d.hdf5',
        LSTM_HIDDEN_UNITS=150,
        CHAR_VECTOR_WORD_SIZE=20,
        VECTOR_WORD_SIZE=300,
        DEFAULT_DICTIONARY = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e':5,'f':6,'g':7,'h':8,'i':9,'j':10,'k':11,'l':12,'m':13,'n':14,'ñ':15,'o':16,'p':17,'q':18,'r':19,'s':20,'t':21,'u':22,'v':23,'w':24,'x':25,'y':26,'z':27,'á':28,'é':29,'í':30,'ó':31,'ú':32,'1':33,'2':34,'3':35,'4':36,'5':37,'6':38,'7':39,'8':40,'9':41,'0':42}
    ):
        self.wordvectors_file_vec = wordvectors_file_vec
        self.w2v_limit = w2v_limit
        self.best_epoch = best_epoch
        self.mimick_weights_file = mimick_weights_file
        self.LSTM_HIDDEN_UNITS = LSTM_HIDDEN_UNITS
        self.CHAR_VECTOR_WORD_SIZE = CHAR_VECTOR_WORD_SIZE
        self.VECTOR_WORD_SIZE = VECTOR_WORD_SIZE
        self.DEFAULT_DICTIONARY = DEFAULT_DICTIONARY

        #self.graph = tf.get_default_graph() #tf.Graph()
        #self.session = tf.Session()
        
        self.wordvectors = self.__load_vectors()
        self.vocabulary = list(self.wordvectors.vocab.keys())
        self.vocabulary_size = len(self.vocabulary)
        self.model = self.__create_model()
        self.model = lm(self.mimick_weights_file % self.best_epoch, custom_objects={'euclidean_distance_loss':self.__euclidean_distance_loss})
        self.model._make_predict_function()
        #self.session.run(tf.global_variables_initializer())


    def __word_to_vector_by_char(self, word, dictionary, size=20):
        extended_dictionary = dictionary
        # Unknown char
        extended_dictionary['UNK'] = len(extended_dictionary)
        # Pad char
        extended_dictionary['*'] = len(extended_dictionary)
        if(len(word) > size):
            vector = [extended_dictionary['*']] * size
        else:
            vector = [extended_dictionary['*']] * (size - len(word))
            vector += [extended_dictionary[character if character in extended_dictionary else 'UNK']
                       for character in word.lower()]
        return vector[:size]

    def __load_vectors(self):
        wordvectors = KeyedVectors.load_word2vec_format(self.wordvectors_file_vec, limit=self.w2v_limit)
        return wordvectors

    # Important functions
    def __euclidean_distance_loss(self, y_true, y_pred):
        return kb.sqrt(kb.sum(kb.square(y_pred - y_true), axis=-1))

    def __create_model(self):
        #with self.graph.as_default():
        #    with self.session.as_default():        
        model = Sequential(name='mimicking_model')
        model.add(Bidirectional(LSTM(self.LSTM_HIDDEN_UNITS, return_sequences=True),input_shape=(1, self.CHAR_VECTOR_WORD_SIZE), merge_mode='concat', name='code_encode_mimicking'))
        model.add(TimeDistributed(Dense(self.VECTOR_WORD_SIZE, activation='tanh', name='mimick_output'), name='code_encode_join'))
        return model

    '''
    def vectorize(self, text):
        
        sentence = text
        embeddings = []
        for word in sentence.split(' '):
            wordVectors = []
            try:
                wordVectors = self.wordvectors[word]
                embeddings.append(wordVectors)
            except:
                charsVectors = []
                charsVectors = np.asarray(
                    [[self.__word_to_vector_by_char(word, self.DEFAULT_DICTIONARY, self.CHAR_VECTOR_WORD_SIZE)]])
                
                #with self.graph.as_default():
                #    with self.session.as_default():
                        
                wordVectors = self.model.predict(x=charsVectors)

                for wordVector in wordVectors[0]:
                    embeddings.append(wordVector)
        embeddings = np.asarray(embeddings)
        
        return embeddings


    def get_probabilities(self, word):
        try:
            index = self.vocabulary.index(word)
        except:
            word_embedding = self.vectorize(word)
            most_similar_word = self.wordvectors.similar_by_vector(word_embedding[0])[0][0]
            index = self.vocabulary.index(most_similar_word)

        # result = np.zeros((self.vocabulary_size,))
        # result[index] = 1
        
        return np.asarray([index])
        # return np.asarray(result)
    '''
    def vectorize(self, word):

        print('Searching word in vocabulary %s...' % word)
        if word in self.vocabulary:
            print('Most similar word...')
            most_similar_word = self.wordvectors.most_similar(word)[0][0]
            word_vector = self.wordvectors[most_similar_word]
        else:
            print('Converting to char array')
            charsVectors = np.asarray(
                    [[self.__word_to_vector_by_char(word, self.DEFAULT_DICTIONARY, self.CHAR_VECTOR_WORD_SIZE)]])
                   
            print('Predicting...')
            wordVectors = self.model.predict(x=charsVectors)
            print('Flattening...')
            word_vector = wordVectors[0].flatten()

        print('Vectorized...')
        return np.asarray(word_vector)


    def get_probabilities(self, vectorized_word):
        print('Similar by vector...')
        most_similar_word = self.wordvectors.similar_by_vector(vectorized_word)[0][0]
        print('Searching index...')
        index = self.vocabulary.index(most_similar_word)
        print('Probabilized %d...' % index)
        return np.asarray([index])
        
def load_w2v_mimicking_model(
    wordvectors_file_vec = 'wiki.es.vec',
    w2v_limit=100,
    best_epoch=200
    ):
    return w2v_mimick(
        wordvectors_file_vec=wordvectors_file_vec,
        w2v_limit=w2v_limit,
        best_epoch=best_epoch,
        mimick_weights_file='Mimicking/Results Yoshio/Model/run_1/model-%d.hdf5',
        LSTM_HIDDEN_UNITS=150,
        CHAR_VECTOR_WORD_SIZE=20,
        VECTOR_WORD_SIZE=300,
        DEFAULT_DICTIONARY={'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12, 'm': 13, 'n': 14, 'ñ': 15, 'o': 16, 'p': 17, 'q': 18, 'r': 19, 's': 20, 't': 21, 'u': 22, 'v': 23, 'w': 24, 'x': 25, 'y': 26, 'z': 27, 'á': 28, 'é': 29, 'í': 30, 'ó': 31, 'ú': 32, '1': 33, '2': 34, '3': 35, '4': 36, '5': 37, '6': 38, '7': 39, '8': 40, '9': 41, '0': 42}
    )


def vectorize(model, text):
    return model.vectorize(
        text
    )
