"""

"""

import re
import db as DB
import TextmineThis as TT
#import TextmineThis_symptoms as TT_symptoms
import TextmineThis_backup as TT_backup

class EatTheRedPill(object):
    """There's not going back...
    
    """
    
    def __init__(self,database="db.db"):
        """
        
        """
        
        self.db = DB.db(database)
#        self.miner = TT.Textminer()
        self.miner = TT.Textminer()
#        self.symptom_miner = TT_symptoms.Textminer()
#        self.icd10 = self.db.c.execute("SELECT * from icd_10").fetchall()
    
    def becomeMessiah(self):
        """ Create the simple term-doc/tfidf...
        
        """
        
        # Merge the data from different websites and merge each paragraph in a 
        # given website.
        diseases_missing = []
        ready_data=[]
        patreses = self.db.c.execute("SELECT patres FROM disease_info").fetchall()
        for patres in patreses:
            data = self.db.c.execute("SELECT Q.patres, G.data, D.disease_name "\
                                "FROM query Q, googled_info_cleansed G, disease_info D "\
                                "WHERE Q.query = G.query AND Q.patres = D.patres "\
                                                        "AND Q.patres=?",[patres[0]])
            data = data.fetchall()
            if data:
                paragraphs = " ".join([x[1] for x in data])
                ready_data.append((data[0][0],paragraphs,data[0][2]))
            else: 
                diseases_missing.append(patres[0])
                continue
        
        TermDoc, self.t1_hash, self.d1_hash, self.n1_hash = self.miner.createTermDoc(ready_data)
        TFIDF = self.miner.runTFIDF(TermDoc)
        
        return TermDoc, TFIDF, diseases_missing
    
    def moveReallyFast(self):
        """ Creating the symptom-doc-matrix/tfidf...
        
        """
        
        diseases_missing = []
        ready_data=[]
        patreses = self.db.c.execute("SELECT patres FROM disease_info").fetchall()
        for patres in patreses:
            data = self.db.c.execute("SELECT N.patres, N.freq, N.symptom, D.disease_name \
                                    FROM nlp_nonweighted N, disease_info D \
                                    WHERE D.patres=N.patres \
                                        AND N.patres=?",[patres[0]])
#            data = self.db.c.execute("SELECT N.patres, N.freq, N.symptom, D.disease_name \
#                                    FROM nlp_weighted N, disease_info D \
#                                    WHERE D.patres=N.patres \
#                                        AND N.patres=?",[patres[0]])

            data = data.fetchall()
            
            if data:
                symptom_list = [(x[1],x[2]) for x in data if x]
                ready_data.append((data[0][0],symptom_list,data[0][3]))
            else: 
                diseases_missing.append(patres[0])
                continue
        
        self.symptTermDoc, self.t_hash, self.d_hash, self.n_hash = self.symptom_miner.createTermDoc(ready_data)
        TermDoc, self.t2_hash, self.d2_hash, self.n2_hash = self.symptom_miner.createTermDoc(ready_data)
        
        TFIDF = self.symptom_miner.runTFIDF(self.symptTermDoc)
        
        return TFIDF, diseases_missing
    
    
    
    def callTheMatrices(self):
        
        _,tfidf_uni,_ = self.becomeMessiah()
        tfidf_nlp,_ = self.moveReallyFast()
        
        return tfidf_uni, tfidf_nlp
    
    def setHashes(self,t1_hash, t2_hash, d1_hash, d2_hash, n1_hash, n2_hash):
        self.t1_hash = t1_hash; self.t2_hash = t2_hash; self.d1_hash = d1_hash; self.d2_hash = d2_hash; self.n1_hash = n1_hash; self.n2_hash = n2_hash
    
    
    def combineTheSizzle(self,path,tfidf_uni,tfidf_nlp):
        
#        r1 = self.pt.runTest(tfidf_uni,"testdata1/bmj.txt", self.t_hash, self.d_hash, self.n_hash)
        
#        r2 = self.pt.runTest(tfidf_nlp,"testdata1/bmj.txt", self.t_hash, self.d_hash, self.n_hash)
        
        test_file = re.split('\n',open(path).read())
        
        results=[]
        for testcase in test_file:
            if testcase: # avoid empty rows
                data = re.split('\t',testcase)
                orpha_num = data[0]
                query = data[2]
                
                r1 = self.miner.queryTheMatrix(tfidf_uni, query,self.t1_hash, self.d1_hash, self.n1_hash)
                r2 = self.miner.queryTheMatrix(tfidf_uni, query,self.t1_hash, self.d1_hash, self.n1_hash)
                
                # Note that this merger reverses the positions of the tuples...
                results = self._merge_scores(r1,r2) 
                
                # Hack: Reverse the hash for name-to-doc-id lookup 
                # (no disease names should occur twice)
                rev_name_hash = dict(zip(self.n1_hash.values(),self.n1_hash.keys()))
                
                rank=0
                for r in results:
                    rank+=1
                    # get the doc-id by name lookup
                    doc_id = rev_name_hash[r[0]]
                    if doc_id == int(orpha_num): print rank,"\t",r[1],"\t",r[0]
    
    
    def _merge_scores(self,r1,r2):
        """
        Simply adds and merges two tupled lists where the score is the first
        element and the enitity name the second element.
        """
        result = dict([(x[0],x[1]) for x in r1])
        for r in r2:
            if result.has_key(r[0]): result[r[0]]+=r[1]
            else: result[r[0]] = r[1]
        
        result = sorted(result.items(), key=lambda (k,v): (v,k), reverse=True)
        
        return result
    
    
    
    
