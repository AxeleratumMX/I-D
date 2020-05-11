from keras.layers import Layer, Input, RNN, GRU, Lambda, Flatten, RepeatVector, Concatenate
from keras.models import Model
import keras.backend as K
import tensorflow as tf

''' Cell used inside RNN when decoding in Skip-thought model '''

class DecoderGRUCell(Layer):

    def __init__(self, units, encoder_size, activation=K.tanh, recurrent_activation=K.hard_sigmoid, **kwargs):
        self.units = units
        self.state_size = self.units
        self.embedding_size = self.units
        self.encoder_size = encoder_size
        self.activation = activation
        self.recurrent_activation = recurrent_activation
        super(DecoderGRUCell, self).__init__(**kwargs)

    def build(self, input_shape):

        self.W_r = self.add_weight(
            shape=(self.embedding_size, self.units),
            initializer='uniform',
            name='W_r_kernel'
        )

        self.U_r = self.add_weight(
            shape=(self.units, self.units),
            initializer='uniform',
            name='U_r_kernel'
        )

        self.C_r = self.add_weight(
            shape=(self.encoder_size, self.units),
            initializer='uniform',
            name='C_r_kernel'
        )

        self.W_z = self.add_weight(
            shape=(self.embedding_size, self.units),
            initializer='uniform',
            name='W_z_kernel'
        )

        self.U_z = self.add_weight(
            shape=(self.units, self.units),
            initializer='uniform',
            name='U_z_kernel'
        )

        self.C_z = self.add_weight(
            shape=(self.encoder_size, self.units),
            initializer='uniform',
            name='C_z_kernel'
        )

        self.W = self.add_weight(
            shape=(self.embedding_size, self.units),
            initializer='uniform',
            name='W_kernel'
        )

        self.U = self.add_weight(
            shape=(self.units, self.units),
            initializer='uniform',
            name='U_kernel'
        )

        self.C = self.add_weight(
            shape=(self.encoder_size, self.units),
            initializer='uniform',
            name='C_kernel'
        )

        self.built = True
        
    def call(self, all_inputs, states):
        encoder_output = all_inputs[:, :self.encoder_size]
        inputs = all_inputs[:, self.encoder_size:] 
        prev_output = states[0]
        
        r = self.recurrent_activation(
            K.dot(inputs, self.W_r) + 
            K.dot(prev_output, self.U_r) + 
            K.dot(encoder_output, self.C_r)
        )

        z = self.recurrent_activation(
            K.dot(inputs, self.W_z) + 
            K.dot(prev_output, self.U_z) + 
            K.dot(encoder_output, self.C_z)
        )
        
        h_ = self.activation(
            K.dot(inputs, self.W) + 
            K.dot(prev_output * r , self.U) + 
            K.dot(encoder_output, self.C)
        )

        h = (1 - z) * prev_output + z * h_

        return h, [h]



''' Loading the Skip-Thought vector model '''

def load_skip_thought_model(
    encode_size, 
    embedding_words_per_sentence,
    lookup_table
    ):

    word_embedding_size = lookup_table.shape[1]
    
    def __probabilities_calc(x):
        result = K.dot(lookup_table_k, K.permute_dimensions(x, [0,2,1]))
        result = K.permute_dimensions(result, [1, 2, 0])
        result = K.exp(result)    
        return result

            
    lookup_table_k = K.variable(value=lookup_table)

    inputs = Input(shape=(embedding_words_per_sentence, word_embedding_size), name='sentences')

    encoder = GRU(encode_size, use_bias=True, return_sequences=False, name='encoded_sentences')
    previous_decoder_cell = DecoderGRUCell(word_embedding_size, encoder_size=encode_size)
    next_decoder_cell = DecoderGRUCell(word_embedding_size, encoder_size=encode_size)
    repeater = RepeatVector(embedding_words_per_sentence, name='repeat_encode_sentences')
    joiner = Concatenate(name='concat_encode_w_inputs')
    previous_decoder = RNN(previous_decoder_cell, return_sequences=True, name='decoded_previous_sentences')
    next_decoder = RNN(next_decoder_cell, return_sequences=True, name='decoded_next_sentences')
    prev_prob_calculator = Lambda(__probabilities_calc, name='previous_probabilities')
    next_prob_calculator = Lambda(__probabilities_calc, name='next_probabilities')
    

    #prev_prob_calculator = Lambda(__probabilities_calc)
    #next_prob_calculator = Lambda(__probabilities_calc)


    encoded_sentence = encoder(inputs)
    repeated_encoded_sentence = repeater(encoded_sentence)
    concatenated_inputs = joiner([repeated_encoded_sentence, inputs])
    decoded_previous_words = previous_decoder(concatenated_inputs)
    decoded_next_words = next_decoder(concatenated_inputs)
    previous_probs = prev_prob_calculator(decoded_previous_words)
    next_probs = next_prob_calculator(decoded_next_words)
    
    model = Model(inputs=[inputs], outputs=[previous_probs, next_probs], name='skip_thought')

    
    return model
