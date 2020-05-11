class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None):
        """Constructs a InputExample.

        Args:
            guid: Unique id for the example.
            text_a: string. The untokenized text of the first sequence. For single
            sequence tasks, only this sequence must be specified.
            text_b: (Optional) string. The untokenized text of the second sequence.
            Only must be specified for sequence pair tasks.
            label: (Optional) string. The label of the example. This should be
            specified for train and dev examples, but not for test examples.
        """
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.output = None


class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, input_ids, input_mask, segment_ids):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.output = None

class ReviewExample(InputExample):
    def __init__(self, review_id, polarity, context, target, aspect, guid, text_a, text_b=None):
        super(ReviewExample, self).__init__(guid, text_a, text_b)
        self.review_id = review_id
        self.polarity = polarity
        self.context = context
        self.target = target
        self.aspect = aspect
        self.output = None

        def __str__(self):
            return '{} {} {} {} {} {}'.format(self.review_id, self.polarity, self.context, self.target, self.aspect, self.output)

        __repr__ = __str__

class DataProcessor(object):
    """Base class for data converters for sequence classification data sets."""

    def get_labels(self):
        """Gets the list of labels for this data set."""
        raise NotImplementedError()

    def convert_reviews_to_examples(self, reviews):
        """Gets the list of labels for this data set."""
        raise NotImplementedError()

    def convert_examples_to_reviews(self, examples):
        """Gets the list of labels for this data set."""
        raise NotImplementedError()

class Review:
    def __init__(self, id, context, review):
        self.id = id
        self.context = context
        self.review = review

class EmptyReviewsException(Exception):
   pass

class NonFeaturesGeneratedException(Exception):
   pass
