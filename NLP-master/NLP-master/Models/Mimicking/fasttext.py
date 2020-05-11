from gensim.models.keyedvectors import KeyedVectors
import numpy as np
import numba as nb
from numba import cuda, guvectorize, njit, float32
import math
import pycuda.autoinit
import pycuda.gpuarray as gpuarray
import skcuda.linalg as linalg

class WordEmbedding():
    def __init__(self, filepath, unknown_word = '</s>', limit=100):
        self.model =  KeyedVectors.load_word2vec_format(filepath, limit=limit)
        self.model.init_sims()
        self.lookup_table = np.asarray(self.model.wv.vectors_norm)#np.asarray([self.model[word] for word in self.model.wv.vocab.keys()])
        self.vocabulary = np.asarray(list(self.model.wv.vocab.keys()))
        self.unknown_word = unknown_word
        self.used_gpu = len(cuda.gpus) - 1
        linalg.init()

    def vectorize(self, sentences):
        embeddings = []
        for idx, sentence in enumerate(sentences):
            sentence_embedding = []
            for jdx, word in enumerate(sentence):
                try:
                    embedding = self.model.wv[word]
                except:
                    embedding = self.model.wv[self.unknown_word]

                   
                sentence_embedding.append(embedding)
        
            embeddings.append(np.asarray(sentence_embedding))

        return np.asarray(embeddings)

    
    def get_probabilities(self, batch):

        lookup_table_gpu = gpuarray.to_gpu(self.lookup_table)
        probs = []

        for i in range(batch.shape[0]):
            batch_gpu = gpuarray.to_gpu(batch[i])
            batch_T_gpu = linalg.transpose(batch_gpu)
            res_gpu = linalg.transpose(linalg.dot(lookup_table_gpu, batch_T_gpu))
            res = np.argmax(res_gpu.get(), axis=-1)
            probs.append(res)

        probs = np.expand_dims(np.asarray(probs), axis=-1)

        return probs

        
def load_fasttext(filepath, limit=1000):
    return WordEmbedding(filepath=filepath, limit=limit)
