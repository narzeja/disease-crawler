#!/usr/bin/python

"""Module for extracting symptom candidates from documents, and checking
if they are accepted as actual symptoms against our list of known symptoms
harvested by SymptomListCrawler.
NLP based.
"""

__author__ = 'Brian Soborg Mathiasen'
__version__= '1.0'
__modified__='16-02-2011'


import nltk
import SymptomListCrawler as SLC


class FeatureExtractor(object):

    def __init__ (self):
#        self.abstracts = abstracts
        self.symptomlistcrawler = SLC.SymptomListCrawler()
        self.documents = []

    def loadDocuments(self, documents = ["OrphanetData/abstract1.txt", "OrphanetData/abstract2.txt"]):
        self.documents = [self.preprocess(doc) for doc in documents]


    def preprocess(self, abstract):
        """ reads in an abstract text document (from file) and tags every
        token in the text with appropriate token tags.
        known tags here:
        http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
        """

        corpora = open(abstract).read()
        corpora = corpora.replace('\n', ' ')

        document = nltk.sent_tokenize(corpora)
        document = [nltk.word_tokenize(s) for s in document]
        document = [nltk.pos_tag(s) for s in document]

        return document


    def symptom_candidate_extractor(self, document, strict):
        """ extracts symptoms candidates from the POS-tagged sentence
        """
        #should catch "characterized by <listing>" and "characterised by <listing>"
#        grammar = """CHUNK: {<VBD|G><IN>(<JJ|VBG>*<NN><,|CC>)*(<JJ|VBG>*<NN>)}"""
        candidates = []

        if strict:
            grammar = """CANDIDATE: {<VBD><IN>(<SYMPTOM><,|CC>?)*}
                         SYMPTOM: {<JJ|VB(D|G)>*<NN>*}
                      """
        else:
            grammar = """SYMPTOM: {<JJ|VBG>*<NN>*}
                    """

        cp = nltk.RegexpParser(grammar)

        for sentence in document:
            result = cp.parse(sentence)
            previous = None
            for chunk in result:
                try:
                    if strict:
                        if chunk.node == 'CANDIDATE':
                            previous = 'CANDIDATE'
                        if (previous == 'CANDIDATE' or previous == 'SYMPTOM') and chunk.node == 'SYMPTOM':
                            candidates.append(chunk.leaves())
                            previous = 'SYMPTOM'
                    else:
                        if chunk.node == 'SYMPTOM':
                            candidates.append(chunk.leaves())
                except AttributeError:
                    continue
        return candidates


    def feature_extractor(self, document, strict=True):
        """ function to extract features from document, returns a list of
        features
        """
        symptom_candidates = self.symptom_candidate_extractor(self.documents[document], strict)
        results = []
        for tree in symptom_candidates:
            searchTerm = ""
            for candidate in tree:
                searchTerm += candidate[0] + " "
            results.append(searchTerm[:-1])
        return results


    def synonym_extractor(self, sentence):
        """ extracts synonyms from the sentence
        """
        # grammar should catch "also known as ...", "also called ..."
        #FIXME: STUB!
        return []

    def misc_extractor(self, sentence):
        """ extracts misc from the sentence, anything that can otherwise
        be useful, such as demographics, prevelance or other.
        """
        #FIXME: STUB!
        return []


