
import nltk


def onewordtagging(document='OrphanetData/abstract1.txt'):
    """ reads in an abstract text document (from file) and tags every
    token in the text with appropriate token tags.
    tags here:
    http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    """

    corpora = open(document).read()
    corpora = corpora.replace('\n', ' ')

    sent = nltk.sent_tokenize(corpora)
    sent = [nltk.word.tokenize(s) for s in sent]
    sent = [nltk.pos_tag(s) for s in sent]

    return sent



def feature_extractor(document):
    """ function to extract features from document, returns a list of
    features
    """
    #FIXME: STUB!

    def symptom_extractor(sentence):
        """ extracts symptoms from the sentence
        """
        #FIXME: STUB!
        return []

    def synonym_extractor(sentence):
        """ extracts synonyms from the sentence
        """
        #FIXME: STUB!
        return []

    def misc_extractor(sentence):
        """ extracts misc from the sentence, anything that can otherwise
        be useful, such as demographics, prevelance or other.
        """
        #FIXME: STUB!
        return []

    return []



