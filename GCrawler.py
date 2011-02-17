from BaseCrawler import BaseCrawler
import lxml
import lxml.html
from lxml import etree
import TextmineThis
import unicodedata
import re

class GCrawler(BaseCrawler):
    
    def __init__(self):
        pass
    
    def crawl(self,url,initial_info,synonyms,corr_threshold=0.8):
        """
        Crawl a website for paragraphs that either has some similarity to the
        initial info, or little similarity but contains at least one of the
        synonyms.
        
        @param url              str     Website to be crawled
        @param  initial_info    str     Base information that the crawler texts
                                          are compared against.
        @param synonyms         list    The disease name along with synonyms and
                                          acronyms.
        @param corr_threshold   float   Correlation (cosine by default) threshold
        
        @returns a list containing the url and a list of accepted texts (in any)
        """
        
        miner = TextmineThis.Textminer()
        data = {}
        data[url] = []
        page = self.open_url(url)
        
        print "URL:",url
        
        parser = etree.HTMLParser()
        tree = lxml.etree.parse(page, parser)
         
        text = ""
        paragraphs = tree.xpath('//p')
        for p in paragraphs:
            tmp = p.xpath('text()')
            
            tmp = " ".join(tmp) #
            tmp = tmp.split()   ## Ugly but works...
            tmp = " ".join(tmp) #
            
            if isinstance(tmp,unicode):
                tmp = unicodedata.normalize('NFKD', tmp).encode('ascii','ignore')
            
            lst = p.getchildren()
            for s in lst:
                s = s.text
                if isinstance(s,unicode):
                    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore')
                if s:
                    s = " ".join(s.split())
                    if s:
                        tmp += " "+s
            
            # Calculate the cosine similarity measure between the two documents
            score = miner.documentCorrelation(initial_info,tmp)
            
            # Sanitize for all non-alphanumerical characters
            sanitizer = re.compile('[\W]')
            synonyms = [sanitizer.sub(' ',x.lower()) for x in synonyms] 
            tmp = sanitizer.sub(' ',tmp.lower())
            
            # Validate texts
            if (score<corr_threshold) or \
                    (score<9.0 and \
                    re.search(r'characteri[s|z]ed by|characteristic',tmp) and \
                    [x for x in synonyms if x+" " in tmp]): 
                
                data[url].append(tmp)
        
        return data
