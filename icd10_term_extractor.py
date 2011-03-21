import db as DB
#import TextmineThis as TT


def run(TFIDF,TermDoc,t_hash,d_hash,code):
    
    db = DB.db()
    
    #patres INT, code TEXT, category TEXT, keywords TEXT,
    icd10 = db.c.execute("select patres,code from icd_10").fetchall()
    relevant_patreses = [x[0] for x in icd10 if code in x[1]]
    
    # Get the diseases belonging to the icd 10 category
    rows = [d_hash[x] for x in relevant_patreses]
    submatrix_tfidf = TFIDF[rows,:]
    
    # Get the indices (aka. the term hashes) sorted by summed-tfidf score
    scores = sum(submatrix_tfidf[:]).tolist()[0]
    scores_tfidf = range(len(scores))
    scores_tfidf.sort(lambda x,y: cmp(scores[x],scores[y]))
    
    sorted_tfidf_terms = [t_hash[x] for x in scores_tfidf]
    
    return sorted_tfidf_terms
    
#    submatrix_termDoc = TermDoc[rows,:]
    
#    return scores_tfidf
