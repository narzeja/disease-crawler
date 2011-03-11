#!/usr/bin/python

"""Module for extracting symptom candidates from documents, and checking
if they are accepted as actual symptoms against our list of known symptoms
harvested by SymptomListCrawler.
NLP based.

@USAGE:
instantiate the class

symptoms, non_symptoms = instance.feature_extractor(doc)
@doc is a path to a text file or a string

"""

__author__ = 'Brian Soborg Mathiasen'
__version__= '1.0'
__modified__='16-02-2011'


import nltk
import SymptomListCrawler as SLC
import string
from nltk.corpus import brown, treebank
import re
from cPickle import dump
from cPickle import load

class FeatureExtractor(object):

    def __init__ (self, n=1, onlypos=False, retrain=False):
#        self.abstracts = abstracts
        self.symptomlistcrawler = SLC.SymptomListCrawler()
        self.symptomlistcrawler.get_symptoms_filesystem()
        brown_tagged_sents = brown.tagged_sents(categories="news")
        backofftagger = nltk.data.load('taggers/maxent_treebank_pos_tagger/english.pickle')
        if not onlypos:
            if retrain:
                print "Training the NgramTagger, this will take a while"
                self.ntagger = nltk.NgramTagger(n, brown_tagged_sents, backoff=backofftagger)
                output = open('ngramtag.pkl', 'wb')
                dump(self.ntagger, output, -1)
                output.close()
            else:
                print "Reloading an old NgramTagger"
                input = open('ngramtag.pkl', 'rb')
                self.ntagger = load(input)
                input.close()
        else:
            self.ntagger = backofftagger
#    def loadDocuments(self):
#        self.documents = [self.preprocess(doc) for doc in documents]


    def preprocess(self, doc):
        """ reads in an abstract text document (from file) and tags every
        token in the text with appropriate token tags.
        known tags here:
        http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
        """
        try:
            corpora = open(doc).read()
        except IOError:
            corpora = doc

        def remove_html_tags(data):
            p = re.compile(r'<.*?>')
            return p.sub('', data)
        corpora = remove_html_tags(corpora)
        corpora = corpora.replace('\n', ' ')

        document = nltk.sent_tokenize(corpora)
        document = [nltk.word_tokenize(s) for s in document]
        document = [self.ntagger.tag(s) for s in document]
#        document = [nltk.pos_tag(s) for s in document]

        return document


    def _symptom_candidate_extractor(self, document, strict, loop):
        """ extracts symptoms candidates from the POS-tagged sentence
        """
        #should catch "characterized by <listing>" and "characterised by <listing>"
#        grammar = """CHUNK: {<VBD|G><IN>(<JJ|VBG>*<NN><,|CC>)*(<JJ|VBG>*<NN>)}"""
        candidates = []

        if strict:
            grammar = r"""CANDIDATE: {<VBD><IN>(<SYMPTOM><,|CC>?)*}
                         SYMPTOM: }<DT><NN>{
                                  {<JJ|VBG>*<NN>+}
                      """
        else:
            grammar = r"""SYMPTOM: }<DT><NN>{
                                   {<JJ>*<NN>+}
                    """

        cp = nltk.RegexpParser(grammar, loop=loop)

        for sentence in document:
            result = cp.parse(sentence)
            previous = None
            for chunk in result:
                try:
                    if strict:
                        if chunk.node == 'CANDIDATE':
                            previous = 'CANDIDATE'
                        elif (previous == 'CANDIDATE' or previous == 'SYMPTOM') and chunk.node == 'SYMPTOM':
                            candidates.append(chunk.leaves())
                            previous = 'SYMPTOM'
                        else:
                            previous = None
                    else:
                        if chunk.node == 'SYMPTOM':
                            candidates.append(chunk.leaves())
                except AttributeError:
                    continue
        return candidates

    def feature_extractor(self, doc, strict=False, loop=1):
        """ function to extract features from document, returns a list of
        features
        """

        document = self.preprocess(doc)
        symptom_candidates = self._symptom_candidate_extractor(document, strict, loop)
        results = []
        for tree in symptom_candidates:
            searchTerm = ""
            for candidate in tree:
                searchTerm += string.lower(candidate[0]) + " "
            results.append(searchTerm[:-1])
#        return self.validate_features(results)
        calc, weighted = self.calc_candidates(results)
        return results, calc, weighted

    def calc_candidates(self, list_of_candidates):
#        FIXME: Device a method to count words of phrases in a list,
#        such that any phrase in that list gets the count on the
#        occurance of that word
#       i.e.: ['hej ost', 'hej', 'tis', 'lis', 'ost'] gets to:
#       {'hej ost': 3,
#        'hej': 2,
#        'ost': 2,
#        'tis': 1,
#        'lis': 1}
        unique_words_in_list = list(set(list_of_candidates))

        dictionary = {}
        for word in list_of_candidates:
            dictionary[word] = 0
            for word2 in list_of_candidates:
                if word2 == word:
                    dictionary[word] += 1
                else:
                    word2split = word2.split(' ')
                    wordsplit = word.split(' ')
                    for w2s in word2split:
                        for ws in wordsplit:
                            if w2s == ws:
                                dictionary[word] +=1

#        return dictionary
#        uniquelist = []
#        for s in list_of_candidates:

#        dictionary_cand = {}
#        spam = [dictionary_cand.update({s:list_of_candidates.count(s)}) for s in list_of_candidates]
        sorted_set = sorted([(value,key) for (key,value) in dictionary.items()])

        hit, miss = self.validate_features(list_of_candidates)
        accepted_candidates = [(s, y) for (s, y) in sorted_set if s > 1]
        results = []
        for h in hit:
            sh = set(h.split(' '))
            for (num, ac) in accepted_candidates:
                ach = set(ac.split(' '))
                if sh.issubset(ach):
                    results.append((num, ac))

        return sorted_set, sorted(list(set(results)))

    def validate_features(self, list_of_candidates):
        validated = []
        failed = []
        for cand in list_of_candidates:
            if self.symptomlistcrawler.symptomExists(cand) or \
               self.symptomlistcrawler.getSymptomsContaining(cand):
                validated.append(cand)
#            elif self.symptomlistcrawler.symptomExistsOnline(cand):
#                validated.append(cand)
            else:
                failed.append(cand)
        return validated, failed


