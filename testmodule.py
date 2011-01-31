import CrawlerInterface; reload(CrawlerInterface); from CrawlerInterface import CrawlerInterface
import OrphanetCrawler; reload(OrphanetCrawler)
import SearchGoogle; reload(SearchGoogle)
import DiseaseListCrawler; reload(DiseaseListCrawler)
import WrongdiagnosisCrawler; reload(WrongdiagnosisCrawler)

import KeywordCrawler; reload(KeywordCrawler)
from KeywordCrawler import KeywordCrawler

def test(urls):

    for url in urls:
#        CI=CrawlerInterface('orphanet',url[1])
#        CI=CrawlerInterface('wrongdiagnosis',url[1])
#        CI.get()
        KC=KeywordCrawler()
        KC.get_disease_info(url[1])

