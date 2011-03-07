# data base skalle

import sqlite3 as sql
import pod
import csv

class db(object):

    def __init__(self, destination='db.db'):
        print("connecting to database in path: ", destination)
        self.sqlserver = sql.connect(destination)

        print("Done")
        self.c = self.sqlserver.cursor()

    def createtables(self):
        
        ############### INITIAL TABLES ###############
        
        table = "disease_info"
        attributes = "(patres INT, abstract TEXT, disease_name TEXT," \
                        "author TEXT, PRIMARY KEY (patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "disease_synonyms"
        attributes = "(patres INT, synonym TEXT, PRIMARY KEY (synonym)," \
                        "FOREIGN KEY (patres) REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "orpha_pubmed_urls"
        attributes = "(patres INT, url TEXT, PRIMARY KEY (url),"\
                        "FOREIGN KEY (patres) REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "disease_symptoms"
        attributes = "(patres INT, symptom TEXT, PRIMARY KEY (patres,symptom)"\
                        "FOREIGN KEY (patres) REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "blacklisted_urls"
        attributes = "(url INT PRIMARY KEY)"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "missed_queries"
        attributes = "(query INT PRIMARY KEY,patres INT,"\
                        " FOREIGN KEY (patres) REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "icd_10"
        attributes = "(patres INT, code TEXT, category TEXT, keywords TEXT, "\
                        "PRIMARY KEY (patres,code),"\
                        "FOREIGN KEY (patres) REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "mim"
        attributes = "(patres INT, url TEXT, PRIMARY KEY (patres,url)"\
                        "FOREIGN KEY (patres) REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "query"
        attributes = "(patres INT, query TEXT, recall INT, blacklisted INT,"\
                        "PRIMARY KEY (patres)"\
                        "FOREIGN KEY (patres) REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "googled_info"
        attributes = "(query TEXT, url TEXT, data TEXT,"\
                        "PRIMARY KEY (query,url)"\
                        "FOREIGN KEY (query) REFERENCES query(query))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        ############### INITIAL VALUES ###############
        
        # TABLE: Disease info
        data = pod.parseOrphaDesc()
        key_list = []
        for row in data:
            if row[0]: r0 = row[0]
            if row[1]: r1 = row[1]
            if row[2]: r2 = row[2]
            if row[3]: r3 = row[3]
            try:
                self.c.execute("INSERT INTO disease_info VALUES (?,?,?,?)",
                                [r0,r1,r2,r3])
            except: continue
        print "Table initialized: disease_info"
        
        # TABLE: ICD 10
        path = "OrphanetData/icd10.csv"
        data = csv.reader(open(path, 'rb'), delimiter='\t')
        header_flag = True;
        for row in data:
            if header_flag: header_flag = False; continue
            if row[0]: r0 = row[0]
            if row[2]: r2 = row[2]
            try:
                self.c.execute("INSERT INTO icd_10 VALUES (?,?,?,?)",
                                [r0,r2,None,None])
            except: continue
        print "Table initialized: icd_10"
        
        # Table: PubMed urls
        path = "OrphanetData/pubmed.csv"
        data = csv.reader(open(path, 'rb'), delimiter='\t')
        header_flag = True;
        for row in data:
            if header_flag: header_flag = False; continue
            if row[1]: r1 = row[1]
            if row[4] and len(row[4])>6: r4 = row[4] # avoid 'neant' or other nulls
            try:
                self.c.execute("INSERT INTO orpha_pubmed_urls VALUES (?,?)",
                                [r1,r4])
            except: continue
        print "Table initialized: orpha_pubmed_urls"
        
        # Table: MIM codes
        path = "OrphanetData/mim.csv"
        data = csv.reader(open(path, 'rb'), delimiter='\t')
        header_flag = True;
        for row in data:
            if header_flag: header_flag = False; continue
            if row[1]: r1 = row[1]
            if row[3]: r3 = row[3]
            try:
                self.c.execute("INSERT INTO mim VALUES (?,?)",
                                [r1,r3])
            except: continue
        print "Table initialized: mim"
        
        # Table: Disease synonyms
        path = "OrphanetData/synonyms.csv"
        data = csv.reader(open(path, 'rb'), delimiter='\t')
        header_flag = True;
        for row in data:
            if header_flag: header_flag = False; continue
            if row[1]: r1 = row[1]
            if row[2]: r2 = row[2]
            try:
                self.c.execute("INSERT INTO disease_synonyms VALUES (?,?)",
                                [r1,r2])
            except: continue
        print "Table initialized: disease_synonyms"
    
        self.commit()
        self.close()

    def commit(self):
        self.sqlserver.commit()

    def close(self):
        self.c.close()


