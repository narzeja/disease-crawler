# data base skalle

import sqlite3 as sql



class db(object):

    def __init__(self, destination=':memory:', load_old=None):
        if load_old:
            print("fetching old database from path: ", load_old)
            self.sqlserver = sql.connect(load_old)
        else:
            print("creating new database in path: ", destination)
            self.sqlserver = sql.connect(destination)

        print("Done")
        self.c = self.sqlserver.cursor()

    def createtables(self):
        
        table = "disease_info"
        attributes = "(patres INT, disease_name TEXT, abstract TEXT," \
                        "author TEXT, PRIMARY KEY (patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "disease_synonyms"
        attributes = "(patres INT, synonym TEXT, PRIMARY KEY (synonym)," \
                        "FOREIGN KEY (patres) REFERENCES disease_info(patres)"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "orpha_pubmed_urls"
        attributes = "(patres INT, url TEXT, PRIMARY KEY (url),"\
                        "FOREIGN KEY (patres) REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "disease symptoms"
        attributes = "(patres INT, symptom TEXT, PRIMARY KEY (patres,symptom)"\
                        "FOREIGN KEY (patres) REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "blacklisted_urls"
        attributes = "(url INT PRIMARY KEY)"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "icd_10"
        attributes = "(patres INT, code TEXT, category TEXT, keywords TEXT, "\
                        "PRIMARY KEY (patres,code),"\
                        "FOREIGN KEY patres REFERENCES disease_info(patres))"
        self.c.execute('CREATE TABLE '+ table + attributes)
        
        table = "mim"
        attributes = "(patres INT, url TEXT, )"
        self.c.execute('CREATE TABLE '+ table + attributes)

    def put(self, list_of_elm, table='diseaseinfo'):
        """ takes a list of type list_of_elm :: [(int, str, str, str, str, str)]
            and enters it into the table 'table'
        """
        for l in list_of_elm:
            self.c.execute('insert into '+table+' values(?,?,?,?,?,?)', l)

    def commit(self):
        self.sqlserver.commit()

    def close(self):
        self.c.close()


