import re
import TextmineThis

#Orphanet: path = "testdata1/orphanet.txt"
#BMJ: path = "testdata1/bmj.txt"

def runTest(path,termDoc,term_hash,doc_hash,name_hash):
    """
    
    """
    
    miner = TextmineThis.Textminer()
    tests = re.split('\n',open(path).read())
    
    for test in tests:
        if test: # avoid empty rows
            data = re.split('\t',test)
            orpha_num = data[0]
            query = data[2]
            
            results = miner.queryTheMatrix(termDoc,query,term_hash,doc_hash,name_hash)
            
            # Hack: Reverse the hash for name-to-doc-id lookup 
            # (no disease names should occur twice)
            rev_name_hash = dict(zip(name_hash.values(),name_hash.keys()))
            
            rank=0
            for r in results:
                rank+=1
                
                # get the doc-id by name lookup
                doc_id = rev_name_hash[r[0]]
                if doc_id == int(orpha_num): print rank,"\t",r[1],"\t",r[0]
                
