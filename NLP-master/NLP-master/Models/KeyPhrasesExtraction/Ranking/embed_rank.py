# Based in Simple Unsupervised keyphrases extraction using sentence embeddings
# https://aclweb.org/anthology/K18-1022

#from SentenceEmbedding import Model
from AroraSentenceEmbedding import Model
import spacy
import nltk
import numpy as np
import scipy
from idea_separator import IdeasExtractor




class EmbedRank():
    #model = Model(bert_config_file=PATH + '\\multi_cased_L-12_H-768_A-12\\bert_config.json',
    #   vocab_file=PATH + '\\multi_cased_L-12_H-768_A-12\\vocab.txt',
    #   init_checkpoint=PATH + '\\multi_cased_L-12_H-768_A-12\\bert_model.ckpt')

    def __init__(self, embedding_model=None):

        if not embedding_model:
            self.model = Model(alpha=0.001, w2v_limit=500000)
        else:
            self.model = embedding_model

        self.processor = spacy.load('es_core_news_md')
        self.ideas_extractor = IdeasExtractor(processor=self.processor)

    def extract_key_phrases(self, document, n_key_phrases=3):
        sentences_list = list(self.ideas_extractor.extract(document))

        title_embedding = self.model.sentence_to_vector([document])[0]['feature_vector']
        sentences_vectors = self.model.sentence_to_vector(sentences_list)

        sentence_embeddings = []

        for vector in sentences_vectors:
            sentence_embeddings.append(vector['feature_vector'])

        sentence_embeddings = np.asarray(sentence_embeddings)

        distances = []
        for sentence_embedding in sentence_embeddings:
            distances.append( scipy.spatial.distance.cosine(sentence_embedding, title_embedding) )

        distances = np.ma.fix_invalid(np.asarray(distances))
        indices = distances.argsort()[:n_key_phrases]

        result = np.asarray(sentences_list)[indices]

        return result







#document = '''Recuperan botellas de vino valuadas en 20 mdp en Iztapalapa
#Seguridad Satelital solicitó el apoyo de la Policía Federal, luego de que había perdido contacto con su unidad en Puebla y su último rastreo vía GPS indicaba que el camión se ubicaba en la Ciudad de México.
#Elementos de la División de Seguridad Regional de la Policía Federal localizaron y recuperaron en la alcaldía de Iztapalapa un tractocamión con reporte de robo, el que transportaba contenedores con vino importado con un valor aproximado de 20 millones de pesos. Te recomendamos: La magia de los Viñedos Don Leo, más allá del vino y la uva Personal de Seguridad Satelital solicitó el apoyo de la corporación, luego que había perdido contacto con la unidad en Puebla y el último rastreo vía GPS indicaba que el tractocamión se ubicaba en la Ciudad de México, modificando su ruta original. Con los datos proporcionados, agentes federales implementaron un operativo de búsqueda y localización en calles de la colonia Chinampac de Juárez, donde aseguraron el tráiler que había sido abandonado junto con su carga. La unidad y la mercancía quedaron a disposición del Ministerio Público del Fuero Común, donde se realizarán las investigaciones correspondientes para deslindar responsabilidades.
#'''

#n_key_phrases = 5

#kp_extractor = EmbedRank()
#result = kp_extractor.extract_key_phrases(document, n_key_phrases=n_key_phrases)
#print(result)