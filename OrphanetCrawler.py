#!/usr/bin/python

"""Search google for pages from orphanet and parse disease information.

<Further describtion missing since the class is not completed>
"""

__author__ = 'Henrik Groenholt Jensen'
__version__= '1.0'
__modified__='22-10-2010'

import lxml
import lxml.html
from lxml import etree

from SearchGoogle import SearchGoogle
import time
import re

class OrphanetCrawler(SearchGoogle):

    count=0
    run=0

    def __init__(self):
        pass

    def crawl_url(self,url):
        
        print "========== NEW QUERY BEGUN ============"
                
        url="\""+url+"\""
        
        # Set GoogleCrawler options
        self.url = False
        self.cached_site = True
        self.site = "orpha.net"
        
        # Search Google        
        urls = self.get_results(url)                
        
        # What sites to look for among the results from Google
        orpha_link = None        
        flag = False
        for cached_site in urls['cached_site']:
            if "Disease_Search.php" in cached_site and not flag: flag = True
            if "cgi-bin/OC_Exp.php" in cached_site and not flag: flag = True
            if flag: 
                orpha_link = cached_site
                print "Orphanet url found"
                break
        
        # Status printouts
        if flag:
            self.count+=1
            self.run+=1
        else:
            self.run+=1
        print "~~~~~~~~~~"
        print "Percentage found: "+str(float(self.count)/self.run)
        print "Run: "+str(self.run)
        print "~~~~~~~~~~"
        
        
        if orpha_link:
        
            print orpha_link
            opened_url = self.open_url(orpha_link)

            # ======= BEGIN PARSING ======= #

            # Parse the relevant section
            parser = etree.HTMLParser()            
            tree = lxml.etree.parse(opened_url, parser)            
            disease_info=tree.xpath('//td[@class="twoColumnsTable"]//tr/td//text()')

            # Sanitize the results a bit and remove empty strings
            sanitizer = re.compile(r'[\r|\n|\t]')
            disease_info=[sanitizer.sub('', e) for e in disease_info]
            disease_info=[e for e in disease_info if not e.isspace()]
            
            print disease_info
            
            # Number of results can vary so we need to tokenize
            tokens=["Orpha number","Prevalence of rare diseases","Inheritance","Age of onset","ICD 10 code","MIM number","Synonym(s)"]
            token_indices=[disease_info.index(e) for e in tokens]
            assert len(token_indices)==7
            results={}
            results["Orpha number"]=disease_info[token_indices[0]+1:token_indices[1]]
            results["Prevalence"]=disease_info[token_indices[1]+1:token_indices[2]]
            results["Inheritance"]=disease_info[token_indices[2]+1:token_indices[3]]
            results["Age of onset"]=disease_info[token_indices[3]+1:token_indices[4]]
            results["ICD 10 code"]=disease_info[token_indices[4]+1:token_indices[5]]
            results["MIM number"]=disease_info[token_indices[5]+1:token_indices[6]]
            results["Synonyms"]=disease_info[token_indices[6]+1:]
            
            disease_summary="".join(tree.xpath('//div[@class="article"]/p//text()'))
            
            if "An Orphanet summary for this disease is currently" in disease_summary:
                disease_summary="-"
            elif "This term does not characterize a disease but a group of diseases" in disease_summary:
                disease_summary="Group of diseases"
            results["Summary"]=disease_summary
            
#            print results
            print results['Prevalence']
            
#        time.sleep(1)
            
        
        
