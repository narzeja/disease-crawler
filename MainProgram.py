#!/usr/bin/python


import nltk
import SymptomListCrawler as SLC
import string
import pod
import GCrawler as GC
import FeatureExtractor as FE
import TextmineThis as TT
import db as datab

class MainProgram():

    def __init__ (self):
        print "Main: Initializing Google Search Engine"
        self.g = GC.GCrawler()

#        print "Main: Importing Orpha.net data"
#        self.data = pod.parseOrphaDesc() # SHOULD COLLECT FROM DATABASE INSTEAD
#        self.newdata = self.g._convert_pod(self.data)

#        print "Main: Importing Feature Extractor"
        self.fe = FE.FeatureExtractor()

#        print "Main: Constructing term document and related hashes"
#        self.tt = TT.Textminer()
#        self.termdoc, self.term_hash, self.doc_hash, self.name_hash = self.tt.createTermDoc(self.data)
#        print "Main: almost there..."
#        self.tfidf = self.tt.runTFIDF(self.termdoc)
#        print "Main: Done! Ready to rock!"
#        self.database = datab.db()

    def createTFIDF(self, termdoc):
#        self.tfidf = self.tt.runTFIDF(self.termdoc)
        pass

    def constructQuery(self, caseReport, strict=False):
        ''' novelty function to extract candidates usable in a search query
        '''
        return self.fe.feature_extractor(caseReport, strict)[0]

    def predict(self, query):
        #TODO: This program should pass the TF-IDF matrix a query and
        # recieve a disease prediction
#        results = self.tt.queryTheMatrix(self.termdoc,query,self.term_hash,self.doc_hash,self.name_hash)
        pass

    def expand(self, patres, additional="", threshold=0.8, strict=True, regoogle=False, loop=3):
        #TODO: This program should pass the model a query to expand the
        # knowledge, related to that particular query.

        # first harvest from google
        if regoogle:
            print "Eggspand: hold on, initializing search and harvest procedure"
            try:
                self.g.crawlGoogle(patres, additional, threshold)
            except KeyError:
                print "Disease with PatRes %s, not found" % patres

        # pull data from DB
        query = self.g.db_cursor.execute("SELECT query FROM query " \
                                         "WHERE patres = %s" %patres).fetchone()

        googled_info_data = self.g.db_cursor.execute("SELECT data FROM googled_info " \
                                                    "WHERE query = ?", query)
        data = googled_info_data.fetchall()
        alldata = " ".join([d[0] for d in data])

        raw, calc, weighted = self.fe.feature_extractor(alldata, strict, loop)
        return raw, calc, weighted


        # insert into refined_googled_info table



#        print "Eggspand: you requested knowledge of disease num %s: %s" % (num_of_disease, lots.keys()[0])
#        crack = ' '.join([' '.join(s) for s in lots[lots.keys()[0]]])
#        print "Eggspand: Initializing %s feature extraction, this might take a while. Have patience!" % "strict" if strict else "Non-strict"
#        raw, cands = self.fe.feature_extractor(crack, strict)
        # extract raw hits and candidates.
        # cand[0] is type  cand :: [(num, str)]
        #                        @str : a disease candidate (e.g. 'thickened blood' or 'sleep')
        #                        @num : number of occurences of 'str', also weighted by subterms of 'str'.
        #                               e.g. ['thickened blood', 'blood', 'cheese'] would be
        #                               [(2, 'thickened blood'), (1, 'blood'), (1, 'cheese')]
        # raw is a type raw :: [str]
#        return raw, cands



