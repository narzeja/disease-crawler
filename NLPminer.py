import db as DB
import FeatureExtractor as FE
import time
import sys

class NLPtextminer(object):
    
    def __init__(self):
        """
        
        """
        
        self.db = DB.db()
        self.fe = FE.FeatureExtractor(tagger='braubt', retrain=False)
    
    def runExtractor(self):
        """
        
        """
        
        patres = self.db.c.execute("select patres from disease_info").fetchall()
        patres = [s[0] for s in patres]
        
        # Hacked test to see if the tables have been made
        try: db.c.execute("SELECT patres FROM nlp_weighted")
        except: print "No tables found. Run 'buildtabels()' first"; return None
        
        counter=0
        t1 = time.time()
        for pat in patres:
            dbcurs = self.db.c.execute("SELECT Q.patres, G.data \
                                        FROM query Q, googled_info_cleansed G \
                                        WHERE G.query=Q.query \
                                          AND Q.patres = ?", [pat])
            dbfetch = dbcurs.fetchall()
            paragraphs = " ".join(" ".join([s[1] for s in dbfetch]).split("::"))
            feats = self.fe.feature_extractor(paragraphs)
            
            # Insert non-weighted symptoms into the database
            for freq,symptom in feast[1]
                try:
                    self.db.c.execute("INSERT INTO nlp_nonweighted VALUES (?,?,?)",
                                        [patres,freq,symptom])
                except:
                    self.db.execute("UPDATE nlp_nonweighted \
                                     SET patres=?, freq=?, symptom=? \
                                     WHERE patres=?",
                                     [patres,freq,symptom,patres])
            
            # Insert weighted symptoms into the database
            for freq,symptom in feast[2]
                try:
                    self.db.c.execute("INSERT INTO nlp_weighted VALUES (?,?,?)",
                                        [patres,freq,symptom])
                except:
                    self.db.execute("UPDATE nlp_weighted \
                                     SET patres=?, freq=?, symptom=? \
                                     WHERE patres=?",
                                     [patres,freq,symptom,patres])
            
            counter +=1
            print "Diseases processed:",counter
        print "elapsed time: ", time.time() - t1
    
    def buildtables(self):
        """
        
        """
        
        self.db.c.execute("CREATE TABLE nlp_weighted ( \
                                patres INT, symptom TEXT, freq INT, \
                                PRIMARY KEY (patres,symptom), \
                                FOREIGN KEY (patres REFERENCES disease_info(patres))\
                            )")
        
        self.db.c.execute("CREATE TABLE nlp_nonweighted ( \
                                patres INT, symptom TEXT, freq INT, \
                                PRIMARY KEY (patres,symptom), \
                                FOREIGN KEY (patres REFERENCES disease_info(patres))\
                            )")


#    for code, data, patres in dbfetch:
#        print "-",

#    print "]"
#    tis = " ".join(" ".join([s[1] for s in dbfetch if s[0] == 'M61.1'].split("::"))
