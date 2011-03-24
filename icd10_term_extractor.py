import db as DB
import itertools
#import TextmineThis as TT
import TextmineThis_symptoms as TTS


def run(TFIDF,TermDoc,t_hash,d_hash):
    
    db = DB.db()
    tts = TTS.Textminer()
    
    codes=["A","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","V","Z"]
    
    icd10 = db.c.execute("select patres,code from icd_10").fetchall()
    
    # Get all the symptoms extracted by NLP
    symptoms = db.c.execute("select N.freq from nlp_nonweighted N").fetchall()
    symptoms = [x[0] for x in symptoms if x]
    symptom_list = list(itertools.chain(*[str(x).split() for x in symptoms]))
    symptom_list = [tts.stem(x) for x in symptom_list]
    symptom_list = set(symptom_list)
    
    icd_featurevectors = {}
    missing_patreses=[]
    for code in codes:
        print "Grouping by",code
        # Get diseases belonging to the icd 10 group
        relevant_patreses = [x[0] for x in icd10 if code in x[1]]
        
        for x in icd10:
            if "I" in x: print x
        
        # Get the diseases belonging to the icd 10 category
        rows=[]
        for patres in relevant_patreses:
            try:
                rows.append(d_hash[patres])
            except: 
                missing_patreses.append(patres)
                continue
        
        print "Based on",len(rows),"diseases"
        
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

def locate_term_category(term,icd_featurevectors):
    
    ranked_groups=[]
    for code,feature_vec in icd_featurevectors.items():
        if term in feature_vec[0]:
            ranked_groups.append((feature_vec[0].index(term),code))
    
    return ranked_groups

def locate_entire_query(query,icd_featurevectors):
    
    ranked_terms = {}
    for term in query:
        if term:
            ranked_groups = locate_term_category(term,icd_featurevectors)
            ranked_terms[term] = sorted(ranked_groups)
    
    return ranked_terms

def top_two(query,icd_featurevectors):
    ranked_terms = locate_entire_query(query,icd_featurevectors)
    potentials=[]
    for item in ranked_terms.items():
        potentials.extend([x[1] for x in item[1][:2]])
    return set(potentials)

import TextmineThis as TT
import PreliminaryTests as PT
def gogo(query,orpha_num,icd_featurevectors,tfidf,t_hash,d_hash,n_hash):
    
    miner  = TT.Textminer()
    pt = PT.tester()
    pt.initialize()
    
    codes = top_two(miner.stem(query),icd_featurevectors)
    print codes
    
    rows=[]
    for code in codes:
        rows.extend(icd_featurevectors[code][1])
    rows = list(set(rows))
    sub_tfidf = miner.runTFIDF(tfidf[rows,:])
    
    print "Submatrix size:",sub_tfidf.shape
    
    results = miner.queryTheMatrix(sub_tfidf,query,t_hash,d_hash,n_hash)
    
    # Hack: Reverse the hash for name-to-doc-id lookup 
    # (no disease names should occur twice)
    rev_name_hash = dict(zip(n_hash.values(),n_hash.keys()))
    
    rank=0
    for r in results:
        rank+=1
        
        # get the doc-id by name lookup
        doc_id = rev_name_hash[r[0]]
        
        if doc_id == int(orpha_num): print rank,"\t",r[1],"\t",r[0]
