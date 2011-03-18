import re
import TextmineThis
import TextmineThis_symptoms as TTs
import db as DB

#Orphanet: path = "testdata1/orphanet.txt"
#BMJ: path = "testdata1/bmj.txt"
class tester():
    
    def __init__(self):
        pass
        
    def initialize(self):
#        self.db = DB.db()
#        self.data = self.db.c.execute("select patres,abstract,disease_name from disease_info")
#        self.data = self.data.fetchall()
        
        #self.miner = TextmineThis.Textminer()
        self.miner = TTs.Textminer()
        
#        self.termDoc,self.term_hash,self.doc_hash,self.name_hash = self.miner.createTermDoc(self.data)
#        self.termDoc = self.miner.runTFIDF(self.termDoc)

    def runTest(self,path,termDoc,term_hash,doc_hash,name_hash):
        """
        
        """
        
        self.termDoc = termDoc
        self.term_hash = term_hash
        self.doc_hash = doc_hash
        self.name_hash = name_hash
        
        tests = re.split('\n',open(path).read())
        
        for test in tests:
            if test: # avoid empty rows
                self.data = re.split('\t',test)
                orpha_num = self.data[0]
                query = self.data[2]
                
                results = self.miner.queryTheMatrix(self.termDoc,query,self.term_hash,self.doc_hash,self.name_hash)
                
                # Hack: Reverse the hash for name-to-doc-id lookup 
                # (no disease names should occur twice)
                rev_name_hash = dict(zip(self.name_hash.values(),self.name_hash.keys()))
                
                rank=0
                for r in results:
                    rank+=1
                    
                    # get the doc-id by name lookup
                    doc_id = rev_name_hash[r[0]]
                    if doc_id == int(orpha_num): print rank,"\t",r[1],"\t",r[0]
    
