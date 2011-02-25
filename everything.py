
import pod
import GCrawler as GC
import FeatureExtractor as FE

def everything(num, disease):
    g = GC.GCrawler()
    data = pod.parseOrphaDesc()
    fe = FE.FeatureExtractor()

    newdata = g._convert_pod(data)
    lots = g.crawlGoogle(newdata[num:num+1], "characterized by")
    crack = ' '.join([' '.join(s) for s in lots[disease]])

    raw, cands = fe.feature_extractor(crack)
    return lots, crack, raw, cands
#    hits, miss = fe.validate_features(cands)
#    return hits, miss

