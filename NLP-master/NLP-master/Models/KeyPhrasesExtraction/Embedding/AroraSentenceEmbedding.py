# Based in "A simple but though-to-beat baseline for sentence embeddings"
# https://openreview.net/pdf?id=SyK00v5xx

from gensim.models.keyedvectors import KeyedVectors
import re
import numpy as np


class Model():
    SENTENCE_TOKENIZER = r'\w+'

    def __init__(self, w2v_file='C:\\Users\\Uriel Corona\\Downloads\\wiki.es.vec', alpha=1, w2v_limit=25000, scale=1e+19):
        self.model = KeyedVectors.load_word2vec_format(w2v_file, limit=w2v_limit)
        self.model.init_sims()
        self.alpha = alpha
        self.w2v_embedding_size = 300
        self.scale = scale

    def sentence_to_vector(self, sentences):
        total_sentences = len(sentences)
        sentences_vectors = []


        for sentence in sentences:
            vector = np.zeros(self.w2v_embedding_size)
            words = re.findall(self.SENTENCE_TOKENIZER, sentence)
            for word in words:
                if word in self.model:
                        vector += ((self.alpha / (self.alpha + self.model.vocab[word].count)) * self.model[word])
                
            
            sentences_vectors.append( vector * (1 / total_sentences ))

        if total_sentences > 1:
            sentences_vectors = np.asarray(sentences_vectors)
            u, s, vh = np.linalg.svd(np.transpose(sentences_vectors))
            uut = np.dot(u[0], u[0])
        else:
            uut = 0
        

        sentences_embeddings = []

        for sentence_vector in sentences_vectors:
            sentences_embeddings.append({'feature_vector': (sentence_vector - uut * sentence_vector) * self.scale})

        return sentences_embeddings

