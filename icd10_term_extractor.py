import db as DB
import itertools
#import TextmineThis as TT
import TextmineThis_symptoms as TTS


def run(TFIDF,TermDoc,t_hash,d_hash,code):
    
    db = DB.db()
    tts = TTS.Textminer()
    
    #patres INT, code TEXT, category TEXT, keywords TEXT,
    icd10 = db.c.execute("select patres,code from icd_10").fetchall()
    relevant_patreses = [x[0] for x in icd10 if code in x[1]]
    
    # Get the symptoms extracted for the icd10 group
    symptoms = db.c.execute("select N.freq from nlp_nonweighted N").fetchall()
    symptoms = [x[0] for x in symptoms if x]
    symptom_list = list(itertools.chain(*[str(x).split() for x in symptoms]))
    symptom_list = [tts.stem(x) for x in symptom_list]
    symptom_list = set(symptom_list)
    
#    symptom_list=[]
#    for patres in relevant_patreses:
#        symptoms = db.c.execute("select N.freq \
#                                 from nlp_nonweighted N \
#                                 where N.patres=?",[patres]).fetchall()
#        symptoms = [x[0] for x in symptoms if x]
#        symptom_list.extend(symptoms)
#    # try splitting it...hacked version!
#    symptom_list = list(itertools.chain(*[x.split() for x in symptom_list]))
#    symptom_list = set(symptom_list)
    
    
    # Get the diseases belonging to the icd 10 category
    rows=[]
    for patres in relevant_patreses:
        try:
            rows.append(d_hash[patres])
        except: continue
#    rows = [d_hash[x] for x in relevant_patreses]
    
    submatrix_tfidf = TFIDF[rows,:]
    
    # Get the indices (aka. the term hashes) sorted by summed-tfidf score
    scores = sum(submatrix_tfidf[:]).tolist()[0]
    scores_tfidf = range(len(scores))
    scores_tfidf.sort(lambda x,y: cmp(scores[x],scores[y]))
    
    rev_term_hash = dict(zip(t_hash.values(),t_hash.keys()))
    sorted_tfidf_terms = [rev_term_hash[x] for x in scores_tfidf]
    
    # remove non-symptom candidates
    sorted_tfidf_terms_cleaned = ['*'+x for x in sorted_tfidf_terms if x not in symptom_list]
    
    return sorted_tfidf_terms, sorted_tfidf_terms_cleaned,symptom_list
    
#    submatrix_termDoc = TermDoc[rows,:]
    
#    return scores_tfidf
