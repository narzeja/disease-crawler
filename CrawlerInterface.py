#!/usr/bin/python

"""Get a dictionary of disease names and urls, information on a given disease or 
genericly crawl google results for further disease information.

Instantiates a predefined crawler module and returns a list of urls to parse
data from
"""

__author__ = 'Henrik Groenholt Jensen'
__version__= '1.0'
__modified__='29-10-2010'

import DiseaseListCrawler
from DiseaseListCrawler import DiseaseListCrawler
import OrphanetCrawler
from OrphanetCrawler import OrphanetCrawler
import WrongdiagnosisCrawler
from WrongdiagnosisCrawler import WrongdiagnosisCrawler

class CrawlerInterface(object):

    crawler=None
    lst=[]

    def __init__(self, page, disease): 
        """Given a keyword a specific crawler is chosen to parse disease 
        information.
        
        @param crawler: Specifies what crawler module to be used.
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Possible options currently include:
          - diseaselist    -> get a list of all diseases and oprhanet urls
          - generic        -> genericly crawl google search results
          - orphanet       -> intial info parser
          - wiki           -> intial info parser
          - wrongdiagnosis -> intial info parser          - 
          - rarediseases   -> intial info parser
          - mim            -> intial info parser
          - icd10          -> intial info parser
          - medpedia       -> intial info parser
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        @type crawler: str

        @param disease: Only relevant for the 'google'-crawler
        @type disease: str

        @raise NotImplemented: If the page is not recognized
        """       
        assert isinstance(page,str)
        assert isinstance(disease,str)

        self.page = page
        self.disease = disease

        if 'diseaselist' in page.lower():
            self.crawler = DiseaseListCrawler
        
        if 'orphanet' in page.lower():
            self.crawler = OrphanetCrawler
        
        
        ### To be implemented...
                
        if 'wiki' in self.page.lower():
            raise NotImplemented
        
        if 'wrongdiagnosis' in self.page.lower():
            self.crawler = WrongdiagnosisCrawler
            
        if 'generic' in self.page.lower():
            raise NotImplemented
            
        
        ### Optionally to be implemented...
            
        if 'rarediseases' in self.page.lower():
            raise NotImplemented
        
        if 'mim' in self.page.lower():
            raise NotImplemented
            
        if 'icd10' in self.page.lower():
            raise NotImplemented
            
        if 'medpedia' in self.page.lower():
            raise NotImplemented


        if not self.page:
            print 'Crawler: ', page 
            raise NotImplemented

    def get(self):
        """         
        @return: Returns a dictionary of information depending on the crawler.
        @rtype: dictionary
        """
        
        crawler = self.crawler()

        return crawler.get_disease_info(self.disease)


