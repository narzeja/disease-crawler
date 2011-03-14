"""

"""

import db as DB
import TextmineThis as TT

class EatTheRedPill(object):
    """There's not going back...
    
    """
    
    def __init__(self,database="db.db"):
        """
        
        """
        
        self.db = DB.db(database)
        self.miner = TT.Textminer()
        
        # Load relevant data
#        self.data = self.db.c.execute("SELECT Q.patres, G.data, D.disease_name "\
#                                 "FROM query Q, googled_info G, disease_info D "\
#                                 "WHERE Q.query = G.query AND Q.patres = D.patres")
#        self.data = self.data.fetchall()
        
        self.icd10 = self.db.c.execute("SELECT * from icd_10").fetchall()
    
    def becomeMessiah(self):
        """ Create the term-doc/tfidf...
        
        """
        
        # Merge the data from different websites and merge each paragraph in a 
        # given website.
        diseases_missing = []
        ready_data=[]
        patreses = self.db.c.execute("select patres from disease_info").fetchall()
        for patres in patreses:
            data = self.db.c.execute("SELECT Q.patres, G.data, D.disease_name "\
                                "FROM query Q, googled_info G, disease_info D "\
                                "WHERE Q.query = G.query AND Q.patres = D.patres "\
                                                        "AND Q.patres=?",[patres[0]])
            data = data.fetchall()
            if data:
                paragraphs = " ".join([x[1] for x in data])
            else: 
                diseases_missing.append(patres[0])
                continue
        
        TermDoc, t_hash, d_hash, n_hash = self.miner.createTermDoc(ready_data)
        TFIDF = self.miner.runTFIDF(TermDoc)
        
        return TFIDF
