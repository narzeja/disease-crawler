import re
import TextmineThis as TT
#import TextmineThis_symptoms as TTs
import TextmineThis_backup as TTb
import db as DB

#Orphanet: path = "testdata1/orphanet.txt"
#BMJ: path = "testdata1/bmj.txt"
class tester():
    
    def __init__(self):
        pass
        
    def initialize(self):
        self.db = DB.db()
#        self.data = self.db.c.execute("select patres,abstract,disease_name from disease_info")
#        self.data = self.data.fetchall()
        
        #self.miner = TextmineThis.Textminer()
        self.miner = TT.Textminer()
        
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
        print "random"
        
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
                    if doc_id == int(orpha_num): print rank,"\t",r[1],"\t",r[0].encode("utf-8")

    def getStats(self,path,term_hash,doc_hash,name_hash):
        """
        
        """
        
        tests = re.split('\n',open(path).read())
        
        for test in tests:
            if test:
                # avoid empty rows
                data = re.split('\t',test)
                orpha_num = data[0]
                query = data[2]
                name = data[1]
                
                data = self.db.c.execute("select G.data from googled_info_cleansed G, query Q where G.query=Q.query and Q.patres=?",[orpha_num]).fetchall()
                
                print name
                print "Based on",len(data),"websites"
                sanitizer=re.compile('[\W]')
                words_per_page=0
                for page in data:
                    words_per_page += len(sanitizer.sub(' ',page[0]).split())
                words_per_page = words_per_page /float(len(data))
                print "Words per page:",words_per_page
        
        print "BONUS stats:"
        patreses = self.db.c.execute("select D.patres from disease_info D").fetchall()
        
        missing=[]
        for patres in patreses:
            data = self.db.c.execute("select G.data,D.disease_name from googled_info_cleansed G, query Q, disease_info D where G.query=Q.query and Q.patres=D.patres and D.patres=?",[patres[0]])
            if len(data[0]==0): missing.append(data[1])
        print len(missing),"diseases was not expanded by the googling."
        
        disqualifier="does not characterize a disease but a group"
        disqualified = []
        for patres in patreses:
            data = self.db.c.execute("select D.disease_name,D.abstract from disease_info D where D.patres=?",[patres[0]])
            if disqualifier in data[1]: disqualified.append(data[0])
        print len(disqualified),"diseases characterized a group of diseases and had no orphanet abstract."






