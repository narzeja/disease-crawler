
import nltk


class 

def preprocess(document='OrphanetData/abstract1.txt'):
    """ reads in an abstract text document (from file) and tags every
    token in the text with appropriate token tags.
    tags here:
    http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    """

    corpora = open(document).read()
    corpora = corpora.replace('\n', ' ')

    sent = nltk.sent_tokenize(corpora)
    sent = [nltk.word_tokenize(s) for s in sent]
    sent = [nltk.pos_tag(s) for s in sent]

    return sent



def feature_extractor(document):
    """ function to extract features from document, returns a list of
    features
    """
    #FIXME: STUB!
    return []


def symptom_candidate_extractor(sentence):
    """ extracts symptoms candidates from the POS-tagged sentence
    """
    #should catch "characterized by <listing>" and "characterised by <listing>"
#    grammar = """CHUNK: {<VBD|G><IN>(<JJ|VBG>*<NN><,|CC>)*(<JJ|VBG>*<NN>)}"""
    grammar = """CANDIDATE: {(<JJ|VBG>*<NN><,|CC>)*(<JJ|VBG>*<NN>)}"""
    cp = nltk.RegexpParser(grammar)
    result = cp.parse(sentence)
    #extract hit
    candidates = []
    for subtree in result.subtrees():
        if subtree.node == 'CANDIDATE':
#            newgrammar = """SYMPTOM: {<JJ|VBG>*<NN>}"""
#            cp2 = nltk.RegexpParser(newgrammar)
#            newtree = cp2.parse(subtree)
            candidates.append(subtree)
    return candidates


def synonym_extractor(sentence):
    """ extracts synonyms from the sentence
    """
    # grammar should catch "also known as ...", "also called ..."
    #FIXME: STUB!
    return []

def misc_extractor(sentence):
    """ extracts misc from the sentence, anything that can otherwise
    be useful, such as demographics, prevelance or other.
    """
    #FIXME: STUB!
    return []


