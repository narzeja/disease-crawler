import db as DB
#import TextmineThis as TT


def run(TFIDF,TermDoc,t_hash,d_hash,code):
    
    db = DB.db()
    
    #patres INT, code TEXT, category TEXT, keywords TEXT,
    icd10 = db.c.execute("select patres,code from icd_10").fetchall()
    relevant_patreses = [x[0] for x in icd10 if code in x[1]]
    
    # Get the diseases belonging to the icd 10 category
    rows=[]
    for patres in relevant_patreses:
        try:
            rows.append(d_hash[x])
        except:
            print "Disease not icd 10 coded,",patres
            continue
#    rows = [d_hash[x] for x in relevant_patreses ]
    print rows
    submatrix_tfidf = TFIDF[rows,:]
    
    # Get the indices (aka. the term hashes) sorted by summed-tfidf score
    scores = sum(submatrix_tfidf[:]).tolist()[0]
    scores_tfidf = range(len(scores))
    scores_tfidf.sort(lambda x,y: cmp(scores[x],scores[y]))
    
    rev_term_hash = dict(zip(t_hash.values(),t_hash.keys()))
    sorted_tfidf_terms = [rev_term_hash[x] for x in scores_tfidf]
    
    return sorted_tfidf_terms
    
#    submatrix_termDoc = TermDoc[rows,:]
    
#    return scores_tfidf
