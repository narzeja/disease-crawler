"""

"""

import db as DB
import TextmineThis as TT
import TextmineThis_symptoms as TT_symptoms

class EatTheRedPill(object):
    """There's not going back...
    
    """
    
    def __init__(self,database="db.db"):
        """
        
        """
        
        self.db = DB.db(database)
        self.miner = TT.Textminer()
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
                                "FROM query Q, googled_info G, disease_info D "\
                                "WHERE Q.query = G.query AND Q.patres = D.patres "\
                                                        "AND Q.patres=?",[patres[0]])
            data = data.fetchall()
            if data:
                paragraphs = " ".join([x[1] for x in data])
                ready_data.append((data[0][0],paragraphs,data[0][2]))
            else: 
                diseases_missing.append(patres[0])
                continue
        
        TermDoc, self.t_hash, self.d_hash, self.n_hash = self.miner.createTermDoc(ready_data)
        TFIDF = self.miner.runTFIDF(TermDoc)
        
        return TFIDF, diseases_missing
    
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
            data = data.fetchall()
            
            if data:
                symptom_list = [(x[1],x[2]) for x in data if x]
                ready_data.append((data[0][0],symptom_list,data[0][3]))
            else: 
                diseases_missing.append(patres[0])
                continue
        
        TermDoc, self.t_hash, self.d_hash, self.n_hash = self.symptom_miner.createTermDoc(ready_data)
        
#        return TermDoc
        
        TFIDF = self.symptom_miner.runTFIDF(TermDoc)
        
        return TFIDF, diseases_missing
        
        
        
