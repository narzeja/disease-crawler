import SearchGoogle as SG
import TextmineThis as TT
import lxml
import lxml.html
from lxml import etree
import unicodedata
import re

class GCrawler():
    
    def __init__(self):
        """
        <description>
        """
        
        self.miner = TT.Textminer()
        self.searcher = SG.SearchGoogle()
        self.searcher.results_per_page = 30
    
    #temp function - to be replaced when the database gets up!!
    def _convert_pod(self,pod_data):
        return [(x[2],x[1],[]) for x in pod_data]
    
    def crawlGoogle(self,crawlData,additional=None,corr_threshold=0.8):
        """
        <description>
        
        @param crawlData        list    List of search information on the form:
                                          [(disease name:str, initial info:str, 
                                           synonyms:list)]
        @param additional       str     Will be attached to each query.
        @param corr_threshold   float   Correlation (cosine by default) threshold.
        """
        
        missed_urls = [] # Some urls will be blocked and searched for later
        googled_info = {}
        for data in crawlData:
            query           = data[0]
            initial_info    = data[1]
            synonyms        = data[2]
            googled_info[query] = []
            
            synonyms.append(query) # append the query along with its synonyms
            if additional: query += " "+additional # add additional search info
            
            try:
                urls = self.searcher.get_results(query)['url']
                buffy = []
                for url in urls:
                    vampireslayer = self.crawlURL(url,initial_info,synonyms,corr_threshold)
                    if vampireslayer: buffy.append(vampireslayer)
                googled_info[query].append(buffy)
            except:
                print("Killing the old Google Search instance")
                missed_urls.append(query)
                del self.searcher
                self.searcher = SG.SearchGoogle() # make a new searcher
        
        # TODO: fix missed urls
        
        return googled_info
    
    def crawlURL(self,url,initial_info,synonyms,corr_threshold=0.8):
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
        
        @returns a list containing the accepted texts (in any)
        """
        
        data = []
        page = self.searcher.open_url(url)
        
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
            score = self.miner.documentCorrelation(initial_info,tmp)
            
            # Sanitize for all non-alphanumerical characters
            sanitizer = re.compile('[\W]')
            synonyms = [sanitizer.sub(' ',x.lower()) for x in synonyms] 
            tmp = sanitizer.sub(' ',tmp.lower())
            
            # Validate texts
            if (score<corr_threshold) or \
                    (score<9.0 and \
                    re.search(r'characteri[s|z]ed by|characteristic',tmp) and \
                    [x for x in synonyms if x+" " in tmp]): 
                print "################### FOUND ONE!!"
                data.append(tmp)
        
        return data
