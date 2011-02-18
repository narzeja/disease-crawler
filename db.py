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

    def createtable(self, table='diseaseinfo', columns = "(patres int, disease_name text, abstract text, author text, symptoms text, misc text)"):
        """ creates a imple table consisting of the fields:
        @patres: integer
        @disease_name: str
        @abstract: str
        @author: str
        @symptoms: str
        @misc: str (misc data)
        """
        self.c.execute('create table ' + table + columns)

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


