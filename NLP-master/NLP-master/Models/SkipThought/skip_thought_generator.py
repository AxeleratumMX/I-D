import numpy as np
from numba import jit, jitclass
import random
from os import listdir
from os.path import isfile, join
import re
import math
import keras
import tensorflow as tf
import xml.etree.ElementTree as etree
import codecs
import csv
import time
import os
import json



class DataGenerator:

    def __init__(self, data_reader, batch_size):
        self.data_reader = data_reader
        self.batch_size = batch_size
        self.data_reader.open_stream()
        self.num_inputs = 0
        self.num_outputs = 0

        self.X = []
        self.Y = []

        self.more_data = True
        
    def has_more_data(self):
        return self.more_data

    
    def get_data(self):        
        
        iterate = len(self.X) == 0 and len(self.Y) == 0

        if not iterate:
            iterate = self.X[0].shape[0] < self.batch_size and self.Y[0].shape[0] < self.batch_size

        # While does not exists enough data loaded
        while(iterate):

            data = self.__load_data()

            # If cannot load more data return all you have
            if(data == None):
                self.more_data = False
                x_batch = self.X
                y_batch = self.Y
                
                self.X = []
                self.Y = []

                

                return x_batch, y_batch

            # If more data was loaded concatenate it
            
            x_new, y_new = self.preprocess_data(data)

            if x_new is not None and y_new is not None:
                # If X and Y have not been initializated
                if len(self.X) == 0 and len(self.Y) == 0:
                    self.X += x_new
                    self.Y += y_new

                    self.num_inputs = len(self.X)
                    self.num_outputs = len(self.Y)
                else:
                    self.X = [ np.concatenate([X_, x_new[it]], axis=0) for it, X_ in enumerate(self.X) ]
                    self.Y = [ np.concatenate([Y_, y_new[it]], axis=0) for it, Y_ in enumerate(self.Y) ]

                iterate = self.X[0].shape[0] < self.batch_size and self.Y[0].shape[0] < self.batch_size
        
        # Returns loaded data
        return self.__get_batch()


    def preprocess_data(self, data):
        raise Exception('DataGenerator.__preprocess_data not implemented yet')

    #@jit
    def __get_batch(self):
        x_batch = [ X_[0:self.batch_size] for X_ in self.X ]
        y_batch = [ Y_[0:self.batch_size] for Y_ in self.Y ]

        self.X = [ X_[self.batch_size:] for X_ in self.X ]    
        self.Y = [ Y_[self.batch_size:] for Y_ in self.Y ]

        return x_batch, y_batch

    def __load_data(self):
        if self.data_reader.has_more_data():
            return self.data_reader.read_data()
        else:
            return None
    
    def restart_generation(self):
        self.data_reader.close_stream()        
        self.data_reader.open_stream()

    def end_generation(self):
        self.data_reader.close_stream()

    


class SkipThoughtDataGenerator(DataGenerator):
    

    def __init__(self, data_reader, fn_vectorize, fn_gen_prob, word_embedding_size=300, 
                words_per_sentence=50, pad_char='*', batch_size=32, sentence_separator=r'[\.,;]+',
                word_separator=r'[\w]+'):

        DataGenerator.__init__(self, data_reader, batch_size)
        self.fn_vectorize = fn_vectorize
        self.fn_gen_prob = fn_gen_prob
        self.word_embedding_size = word_embedding_size
        self.words_per_sentence = words_per_sentence
        self.pad_char = pad_char
        self.word_separator = word_separator
        self.sentence_separator = sentence_separator
        self.ngram_size = 3

    
    def preprocess_data(self, data):

        normalized_sentences = []
        # Separates by sentences

        sentences = list(filter(None, re.split(self.sentence_separator, data.strip())))

        # Verifies total sentences
        
        if(len(sentences) >= self.ngram_size):
            
            for sentence in sentences:
                words = re.findall(self.word_separator, sentence.strip())

                # Verifies that exists at least one word   
                               
                if(len(words) > 0):
                    pad_length = self.words_per_sentence - len(words)
                    # If sentence had not enough values
                    if(pad_length > 0):
                        words = ([self.pad_char] * pad_length) + words
                    # If sentence had more values than allowed
                    elif(pad_length < 0):
                        words = words[0: self.words_per_sentence]
                    
                    normalized_sentences.append(words)

            # Verifies accepted sentences
            if(len(normalized_sentences) < self.ngram_size):
                return None, None

            normalized_sentences = np.asarray(normalized_sentences)

            
            num_sentences = normalized_sentences.shape[0]   
            embeddings = self.fn_vectorize(normalized_sentences)
            prev_probabilities = self.fn_gen_prob(embeddings[:num_sentences - 2])  
            next_probabilities = self.fn_gen_prob(embeddings[2:])   
            
            return [embeddings[1:num_sentences - 1]], [prev_probabilities, next_probabilities]

            
        else:
            return None, None

    
     
    # Generate (previous_sentence, sentence, next_sentence)
    def __sentence_words_embedding(self, sentences, fn_vectorize):

        embeddings = []
        for idx, sentence in enumerate(sentences):
            sentence_embedding = []
            for jdx, word in enumerate(sentence):
                sentence_embedding.append(fn_vectorize(word))
                
                
            embeddings.append(np.asarray(sentence_embedding))

        return np.asarray(embeddings)
    