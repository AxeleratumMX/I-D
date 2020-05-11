from bert_sentiments_service_utils import ReviewExample, DataProcessor
# import en_core_web_md as es_core_news_md
import es_core_news_md
import numpy as np
import re

OPINION_TAG = 'opinion'
POLARITY_TAG = 'polarity'
CONTEXT_TAG = 'context'
TARGET_TAG = 'target'
SENTENCE_ID_TAG = 'sentence_id'
REVIEW_ID_TAG = 'review_id'
ASPECT_TAG = 'aspect'





   

class Sentihood_NLI_B_Processor(DataProcessor):
    """Processor for the Sentihood data set."""

    SENTIMENTS = ['Positive', 'Negative', 'None']
    SENTIMENT_POLARITY_MAP = {'Positive': 'P', 'Negative': 'N', 'None': '-'}
    DEFAULT_TARGET_POS = ['NOUN', 'PROPN']
    ASPECTS = ['general', 'servicio', 'ambiente', 'precio', 'comida', 'ubicación']
    EMOJI_PATTERN = re.compile('[^\s\w]')



    def __init__(self):
        self.nlp_model = es_core_news_md.load()

    def get_labels(self):
        """See base class."""
        return ['0', '1']

    def convert_to_examples(self, reviews):
        sentences = self.extract_sentences_from_reviews(reviews, self.nlp_model)
        examples = self.convert_sentences_to_examples(sentences)
        return examples
    
    
    def convert_from_examples(self, examples):

        reviews = {}
        for example in examples:
            
            if example.review_id not in reviews:
                reviews[example.review_id] = {}
                reviews[example.review_id]['id'] = example.review_id
                reviews[example.review_id]['aspects'] = {}

            review = reviews[example.review_id]

            if example.aspect not in review['aspects']:
                review['aspects'][example.aspect] = {}
                review['aspects'][example.aspect]['name'] = example.aspect
                review['aspects'][example.aspect]['targets'] = {}

            aspect =  review['aspects'][example.aspect]

            if example.target not in aspect['targets']:
                aspect['targets'][example.target] = {}
                aspect['targets'][example.target]['name'] = example.target
                aspect['targets'][example.target]['opinions'] = {}

            target = aspect['targets'][example.target]

            if example.polarity not in target['opinions']:
                target['opinions'][example.polarity] = {}
                target['opinions'][example.polarity]['polarity'] = self.SENTIMENT_POLARITY_MAP[example.polarity]
                target['opinions'][example.polarity]['sentiment'] = ''
                target['opinions'][example.polarity]['probability'] = example.output[1].item()

        outputs = []

        for review_key in reviews:
            aspects = []
            
            for aspect_key in reviews[review_key]['aspects']:
            
                targets = []
                
                for target_key in reviews[review_key]['aspects'][aspect_key]['targets']:
                    opinions = []

                    for polarity_key in reviews[review_key]['aspects'][aspect_key]['targets'][target_key]['opinions']:
                        opinions.append(reviews[review_key]['aspects'][aspect_key]['targets'][target_key]['opinions'][polarity_key])

            
                    reviews[review_key]['aspects'][aspect_key]['targets'][target_key]['opinions'] = []
                    reviews[review_key]['aspects'][aspect_key]['targets'][target_key]['opinions'] += opinions

                    targets.append(reviews[review_key]['aspects'][aspect_key]['targets'][target_key])


                reviews[review_key]['aspects'][aspect_key]['targets'] = []            
                reviews[review_key]['aspects'][aspect_key]['targets'] += targets

                aspects.append(reviews[review_key]['aspects'][aspect_key])

            
            reviews[review_key]['aspects'] = []
            reviews[review_key]['aspects'] += aspects

            outputs.append(reviews[review_key])
        

        return outputs

    def extract_review_targets(self, review, nlp_model):
        review_ = self.EMOJI_PATTERN.sub(r'', review)
        tokens = nlp_model(review_)
        targets = [token.text for token in tokens if token.pos_ in self.DEFAULT_TARGET_POS]
        return targets  

    def extract_sentences_from_reviews(self, reviews, nlp_model):
        sentences = []

        sentence_id = 0 

        for review in reviews:
            targets = self.extract_review_targets(review.review, nlp_model)
            targets.append(review.context)
            review.targets = targets

            for aspect in self.ASPECTS:
                for target in targets:
                    for sentiment in self.SENTIMENTS:
                        sentence = {
                            SENTENCE_ID_TAG: sentence_id,
                            ASPECT_TAG: aspect,
                            REVIEW_ID_TAG: review.id,
                            POLARITY_TAG: sentiment,
                            CONTEXT_TAG: review.context,
                            TARGET_TAG: target,
                            OPINION_TAG: review.review,
                            }
                        sentence_id += 1
                        sentences.append(sentence)

        return sentences

    def convert_sentences_to_examples(self, sentences):

        result = []

        for sentence in sentences:
            result.append(self.convert_sentence_to_example(sentence))

        return result

    def convert_sentence_to_example(self, sentence):

        sentence_id = sentence[SENTENCE_ID_TAG]
        review_id = sentence[REVIEW_ID_TAG]
        
        polarity = sentence[POLARITY_TAG]
        context = sentence[CONTEXT_TAG]
        target = sentence[TARGET_TAG]
        aspect = sentence[ASPECT_TAG]
        opinion = context + '. ' + sentence[OPINION_TAG]

        question = '{} - {} - {} - {}'.format(polarity, context, target, aspect)

        return ReviewExample(review_id, polarity, context, target, aspect, sentence_id, question, opinion)


    



class Sentihood_NLI_M_Processor(DataProcessor):
    """Processor for the Sentihood data set."""

    SENTIMENTS = ['None', 'Positive', 'Negative']
    SENTIMENT_POLARITY_MAP = {'Positive': 'P', 'Negative': 'N', 'None': '-'}
    DEFAULT_TARGET_POS = ['NOUN', 'PROPN']
    ASPECTS = ['general', 'servicio', 'ambiente', 'precio', 'comida', 'ubicación']
    EMOJI_PATTERN = re.compile('[^\s\w]')

    def __init__(self):
        self.nlp_model = es_core_news_md.load()

    def get_labels(self):
        """See base class."""
        return ['None', 'Positive', 'Negative']

    def convert_to_examples(self, reviews):
        sentences = self.extract_sentences_from_reviews(reviews, self.nlp_model)
        examples = self.convert_sentences_to_examples(sentences)
        return examples
    
    
    def convert_from_examples(self, examples):

        reviews = {}
        for example in examples:
            
            if example.review_id not in reviews:
                reviews[example.review_id] = {}
                reviews[example.review_id]['id'] = example.review_id
                reviews[example.review_id]['targets'] = {}

            review = reviews[example.review_id]

            if example.target not in review['targets']:
                review['targets'][example.target] = {}
                review['targets'][example.target]['name'] = example.target
                review['targets'][example.target]['opinions'] = {}

            target = review['targets'][example.target]
            
            for sentiment_idx, sentiment in enumerate(self.SENTIMENTS):
                target['opinions'][sentiment] = {}
                target['opinions'][sentiment]['polarity'] = self.SENTIMENT_POLARITY_MAP[sentiment]
                target['opinions'][sentiment]['sentiment'] = ''
                target['opinions'][sentiment]['probability'] = example.output[sentiment_idx].item()
                
        outputs = []

        for review_key in reviews:
            
            targets = []
            
            for target_key in reviews[review_key]['targets']:
                opinions = []

                for polarity_key in reviews[review_key]['targets'][target_key]['opinions']:
                    opinions.append(reviews[review_key]['targets'][target_key]['opinions'][polarity_key])

        
                reviews[review_key]['targets'][target_key]['opinions'] = []
                reviews[review_key]['targets'][target_key]['opinions'] += opinions

                targets.append(reviews[review_key]['targets'][target_key])


            reviews[review_key]['targets'] = []            
            reviews[review_key]['targets'] += targets

            outputs.append(reviews[review_key])

        return outputs

    def extract_review_targets(self, review, nlp_model, context=None):
        review_ = self.EMOJI_PATTERN.sub(r'', review)
        tokens = nlp_model(review_)
        targets = [token.text for token in tokens if token.pos_ in self.DEFAULT_TARGET_POS]
        return targets  

    def extract_sentences_from_reviews(self, reviews, nlp_model):
        sentences = []

        sentence_id = 0 

        for review in reviews:
            targets = self.extract_review_targets(review.review, nlp_model)
            targets.append(review.context)
            review.targets = targets

            for target in targets:
                sentence = {
                    SENTENCE_ID_TAG: sentence_id,
                    REVIEW_ID_TAG: review.id,
                    CONTEXT_TAG: review.context,
                    TARGET_TAG: target,
                    OPINION_TAG: review.review,
                }
                sentence_id += 1
                sentences.append(sentence)

        return sentences

    def convert_sentences_to_examples(self, sentences):

        result = []

        for sentence in sentences:
            result.append(self.convert_sentence_to_example(sentence))

        return result

    def convert_sentence_to_example(self, sentence):

        sentence_id = sentence[SENTENCE_ID_TAG]
        review_id = sentence[REVIEW_ID_TAG]
        
        polarity = None
        context = sentence[CONTEXT_TAG]
        target = sentence[TARGET_TAG]
        aspect = None
        opinion = context + '. ' + sentence[OPINION_TAG]

        question = '{} - {}'.format(context, target)

        return ReviewExample(review_id, polarity, context, target, aspect, sentence_id, opinion, question)


    

    
