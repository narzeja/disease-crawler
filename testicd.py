import db as DB
import FeatureExtractor as FE
import time
import sys

def test():
    database = DB.db()
    fe = FE.FeatureExtractor(tagger='braubt', retrain=False)

    patres = database.c.execute("select patres from disease_info").fetchall()
    patres = [s[0] for s in patres]

    ready_data = {}
    print "[",
    t1 = time.time()
    for pat in patres[337:341]:
        dbcurs = database.c.execute("select Q.patres, G.data from query Q, googled_info_cleansed G \
                                        where G.query=Q.query and Q.patres = ?", [pat])
        dbfetch = dbcurs.fetchall()
        paragraphs = " ".join(" ".join([s[1] for s in dbfetch]).split("::"))
        feats = fe.feature_extractor(paragraphs)
        ready_data[pat] = (feats[1], feats[2])
        print "-",
        sys.stdout.flush()

    print "]"
    print "elapsed time: ", time.time() - t1
    return ready_data


#    for code, data, patres in dbfetch:
#        print "-",

#    print "]"
#    tis = " ".join(" ".join([s[1] for s in dbfetch if s[0] == 'M61.1'].split("::"))
