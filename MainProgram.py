#!/usr/bin/python



__author__ = 'Brian Soborg Mathiasen'
__version__= '1.0'
__modified__='16-02-2011'


import nltk
import SymptomListCrawler as SLC
import string
import pod
import GCrawler as GC
import FeatureExtractor as FE
import TextmineThis as TT


class MainProgram():

    def __init__ (self):
        print "Main: Initializing Google Search Engine"
        self.g = GC.GCrawler()

        print "Main: Importing Orpha.net data"
        self.data = pod.parseOrphaDesc()
        self.newdata = self.g._convert_pod(self.data)

        print "Main: Importing Feature Extractor"
        self.fe = FE.FeatureExtractor()

        print "Main: Constructing TF-IDF model and related hashes"
        self.tt = TT.Textminer()
        self.termdoc, self.term_hash, self.doc_hash, self.name_hash = self.tt.createTermDoc(self.data)
        print "Main: almost there..."
        self.tfidf = self.tt.runTFIDF(self.termdoc)
        print "Main: Done! Ready to rock!"



    def predict(self, query):
        #TODO: This program should pass the TF-IDF matrix a query and
        # recieve a disease prediction
        pass

    def expand(self, num_of_disease, extra="", strict=True):
        #TODO: This program should pass the model a query to expand the
        # knowledge, related to that particular query.

        # first harvest from google
        print "Eggspand: hold on, initializing search and harvest procedure"
        lots = self.g.crawlGoogle(self.newdata[num_of_disease:num_of_disease+1], extra)
        print "Eggspand: you requested knowledge of disease num %s: %s" % (num_of_disease, lots.keys()[0])
        crack = ' '.join([' '.join(s) for s in lots[lots.keys()[0]]])
        print "Eggspand: Initializing %s feature extraction, this might take a while. Have patience!" % "strict" if strict else "Non-strict"
        raw, cands = self.fe.feature_extractor(crack, strict)
        # extract raw hits and candidates.
        # cand[0] is type  cand :: [(num, str)]
        #                        @str : a disease candidate (e.g. 'thickened blood' or 'sleep')
        #                        @num : number of occurences of 'str', also weighted by subterms of 'str'.
        #                               e.g. ['thickened blood', 'blood', 'cheese'] would be
        #                               [(2, 'thickened blood'), (1, 'blood'), (1, 'cheese')]
        # raw is a type raw :: [str]

        return raw, cands



