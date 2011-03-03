
import pod
import GCrawler as GC
import FeatureExtractor as FE

def everything(num, disease, extra="", strict=True):
    g = GC.GCrawler()
    data = pod.parseOrphaDesc()
    fe = FE.FeatureExtractor()

    newdata = g._convert_pod(data)
    lots = g.crawlGoogle(newdata[num:num+1], extra)
    crack = ' '.join([' '.join(s) for s in lots[disease]])

    raw, cands = fe.feature_extractor(crack, strict)
    return lots, crack, raw, cands
#    hits, miss = fe.validate_features(cands)
#    return hits, miss

