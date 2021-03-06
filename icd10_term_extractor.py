import re
import db as DB
import itertools
import TextmineThis as TT
import nltk
import TextmineThis_symptoms as TTS

class ICD10tester(object):
    """
    
    """
    
    def __init__(self):
        """
        
        """
        
        self.db = DB.db()
        self.miner = TT.Textminer()
        self.symptom_miner = TTS.Textminer()
        
    
    def getFeatures(self,TFIDF,TermDoc,t_hash,d_hash,sub_features):
        """
        
        """
        # ICD 10 category-codes
        if sub_features:
            codes=[]
            tmp = ["A","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","V","Z"]
            for code in tmp:
                codes.extend(map(lambda x: code+str(x),range(10)))
        else:
            codes = ["A","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","V","Z"]
        
        icd10 = self.db.c.execute("select patres,code from icd_10").fetchall()
        
        # Get all the symptoms extracted by NLP
        symptoms = self.db.c.execute("select N.freq from nlp_nonweighted N").fetchall()
        symptoms = [x[0] for x in symptoms if x]
        symptom_list = list(itertools.chain(*[str(x).split() for x in symptoms]))
        symptom_list = [self.symptom_miner.stem(x) for x in symptom_list]
        symptom_list = set(symptom_list)
        
        icd_featurevectors = {}
        missing_patreses=[]
        print "Grouping..."
        for code in codes:
#            print "Grouping by",code
            # Get diseases belonging to the icd 10 group
            relevant_patreses = [x[0] for x in icd10 if code in x[1]]
            
            # Get the diseases belonging to the icd 10 category
            rows=[]
            for patres in relevant_patreses:
                try:
                    rows.append(d_hash[patres])
                except: 
                    missing_patreses.append(patres)
                    continue
            
#            print "Based on",len(rows),"diseases\n"
            
            # Get the indices (aka. the term hashes) sorted by summed-tfidf score
            submatrix_tfidf = TFIDF[rows,:]
            if submatrix_tfidf[:].shape[0] > 0:
                scores = sum(submatrix_tfidf[:]).tolist()[0]
            else: continue
            scores_tfidf = range(len(scores))
            scores_tfidf.sort(lambda x,y: cmp(scores[x],scores[y]),reverse=True)
            
            # Reverse term hash (terms can be looked up by hash)
            rev_term_hash = dict(zip(t_hash.values(),t_hash.keys()))
            
            sorted_tfidf_terms = [rev_term_hash[x] for x in scores_tfidf]
            
            # remove non-symptom candidates
            sorted_tfidf_terms_cleaned = [x for x in sorted_tfidf_terms if x in symptom_list]
            
            icd_featurevectors[code] = (sorted_tfidf_terms_cleaned,rows)
        
        return icd_featurevectors
    
    
    def categorizeQuery(self,query,icd_featurevectors):
        """
        
        """
        # Number of candidate categories to be included from each term
        numcat = 3
        
        # Calculate the sorted list of icd 10 categories of each term
        ranked_terms = {}
        for term in query:
            if term:
                ranked_groups=[]
                for code,feature_vec in icd_featurevectors.items():
                    if term in feature_vec[0]:
                        ranked_groups.append((feature_vec[0].index(term),code))
                ranked_terms[term] = sorted(ranked_groups)
        
        # Get the icd 10 categories defining the reduced search-space
        potentials = []
        for item in ranked_terms.items():
            potentials.extend([x[1] for x in item[1][:numcat]])
        potentials = list(set(potentials))
        
        #########
#        popcat = [x[:2] for x in potentials]
#        popcat = nltk.FreqDist(popcat)
#        popcat = sorted(popcat.items(), key=lambda (k,v): (v,k), reverse=True)
#        popcat = [x[0] for x in popcat]
#        potentials = [x for x in potentials if x[0] in popcat[:5]]
#        print "Guessed categories:",popcat[:5]
        #########
        
        return potentials
    
    
    def runTests(self,path,icd_featurevectors,tfidf,termDoc,t_hash,d_hash,n_hash,icd_featurevectors_v2):
        """
        
        """
        
        tests = re.split('\n',open(path).read())
        
        for test in tests:
            if test: # avoid empty rows
                data = re.split('\t',test)
                orpha_num = data[0]
                query = data[2]
                
#                sanitizer=re.compile('[\W]')
#                query = sanitizer.sub(' ',query)
                
                codes = self.categorizeQuery(self.miner.stem(query),icd_featurevectors)
                print codes
                
                rows=[]
                for code in codes:
                    rows.extend(icd_featurevectors[code][1])
                rows = list(set(rows))
#                sub_tfidf = tfidf[rows,:]
#                sub_tfidf = miner.runTFIDF(tfidf[rows,:])
                sub_tfidf = self.miner.runTFIDF(termDoc[rows,:])
                
                
                # create hashes to the new submatrix
                dd_hash={}; c=0;
                rev_d_hash = dict(zip(d_hash.values(),d_hash.keys()))
                for row in rows:
                    dd_hash[rev_d_hash[row]] = c
                    c+=1
                
                print "Submatrix size:",sub_tfidf.shape
                
                ddd_hash = dd_hash
                
                ##############################
#                
#                icd_featurevectors_v2 = self.getFeatures(sub_tfidf,None,t_hash,dd_hash,True)
#                
##                tmp = {}
##                for code,content in icd_featurevectors_v2.items():
##                    if code[0] in codes: 
##                        tmp[code] = content
#                
#                codes = self.categorizeQuery(query,icd_featurevectors_v2)
#                
#                print codes
#                
#                rows=[]
#                for code in codes:
#                    rows.extend(icd_featurevectors_v2[code][1])
#                rows = list(set(rows))
#                sub_tfidf = sub_tfidf[rows,:]
#        #        sub_tfidf = miner.runTFIDF(tfidf[rows,:])
#                
#                
#                # create hashes to the new submatrix
#                ddd_hash={}; c=0;
#                rev_dd_hash = dict(zip(dd_hash.values(),dd_hash.keys()))
#                for row in rows:
#                    ddd_hash[rev_dd_hash[row]] = c
#                    c+=1
#                
#                print "SubSUBmatrix size:",sub_tfidf.shape
                
                ##############################
                
                results = self.miner.queryTheMatrix(sub_tfidf,query,t_hash,ddd_hash,n_hash)
                
                # Hack: Reverse the hash for name-to-doc-id lookup 
                # (no disease names should occur twice)
                rev_name_hash = dict(zip(n_hash.values(),n_hash.keys()))
                
                rank=0; disease_found=False;
                for r in results:
                    rank+=1
                    
                    # get the doc-id by name lookup
                    doc_id = rev_name_hash[r[0]]
                    
                    if doc_id == int(orpha_num): 
                        print rank,"\t",r[1],"\t",r[0],"\n"
                        disease_found = True
                if not disease_found: print "Disease not found!",n_hash[int(orpha_num)],"\n"
                else: continue
