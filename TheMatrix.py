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
        self.miner = TT_backup.TextmineThis()
        self.symptom_miner = TT_symptoms.Textminer()
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
        for testcase in test_file[:-1]:
            r1,orpha_num = self._getscores(testcase,tfidf_uni,False)
            #r2,_         = self._getscores(testcase,tfidf_nlp,True)
            
            
            
            result = dict(r1)
            #for r in r2:
            #    if result.has_key(r[0]): result[r[0]] += r[1]
            #    else: result[r[0]] = r[1]
            
            results.append((orpha_num,result.items()))
        
        #########
        
        # Hack: Reverse the hash for name-to-doc-id lookup 
        # (no disease names should occur twice)
        rev_name_hash = dict(zip(self.n1_hash.values(),self.n1_hash.keys()))
        
        for result in results:
            rank=0
            orpha_num = result[0]
            for r in result[1]:
                rank+=1
                # get the doc-id by name lookup
                try:
                    doc_id = rev_name_hash[r[0]]
                except: continue
                
                if doc_id == int(orpha_num): print rank,"\t",r[1],"\t",r[0]
    
    def _getscores(self,testcase,termDoc,nlp):
        
        data = re.split('\t',testcase)
        
        orpha_num = data[0]
        query = data[2]
        
        if not nlp: results = self.miner.queryTheMatrix(termDoc, query, self.t1_hash, self.d1_hash, self.n1_hash)
        else: results = self.symptom_miner.queryTheMatrix(termDoc, query, self.t2_hash, self.d2_hash, self.n2_hash)
        
        return results, orpha_num
        
        
        
        
