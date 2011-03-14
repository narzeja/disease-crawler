"""

"""

import db as DB
import TextmineThis as TT

class eatTheRedPill(object):
    """There's not going back...
    
    """
    
    def __init__(self,database="db.db"):
        """
        
        """
        
        self.db = DB.db(database)
        self.miner = TT.Textminer()
        
        # Load relevant data
        self.data = self.db.c.execute("SELECT Q.patres, G.data, D.disease_name "\
                                 "FROM query Q, googled_info G, disease_info D "\
                                 "WHERE Q.query = G.query AND Q.patres = D.patres")
        self.data = self.data.fetchall()
        
        self.icd10 = self.db.c.execute("SELECT * from icd_10")
        self.icd10 = self.icd10.fetchall()
    
