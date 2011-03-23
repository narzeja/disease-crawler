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
        
        # Get the diseases belonging to the icd 10 category
        rows=[]
        for patres in relevant_patreses:
            try:
                rows.append(d_hash[patres])
            except: 
                missing_patreses.append(patres)
                continue
        
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
        print len(sorted_tfidf_terms_cleaned)
        icd_featurevectors[code] = sorted_tfidf_terms_cleaned
    
    return icd_featurevectors

def locate_term_category(term,icd_featurevectors):
    
    ranked_groups=[]
    for code,feature_vec in icd_featurevectors.items():
        if term in feature_vec:
            ranked_groups.append((feature_vec.index(term),code))
    
    return ranked_groups

def locate_entire_query(query,icd_featurevectors):
    
    ranked_terms = {}
    for term in query.split():
        if term:
            ranked_groups = locate_term_category(term,icd_featurevectors)
            ranked_terms[term] = sorted(ranked_groups)
    
    return ranked_terms

def top_three(query):
    ranked_terms = locate_entire_query(query)
    potentials={}
    for item in ranked_terms.items():
        for cand in item[1][:3]:
            if potentials.has_key(cand[1]): potentials[cand[1]] += 1
            else: potentials[cand[1]] = 1
    return potentials
