#!/usr/bin/python

"""Search google for pages from orphanet and parse disease information.

<Further describtion missing since the class is not completed>
"""

__author__ = 'Henrik Groenholt Jensen'
__version__= '1.0'
__modified__='29-10-2010'

import lxml
import lxml.html
from lxml import etree

import SearchGoogle
from SearchGoogle import SearchGoogle

import time
import re

class OrphanetCrawler(object):

    def __init__(self):
        self.SG=SearchGoogle()

    def get_disease_info(self,disease):
        
        print "========== NEW QUERY BEGUN ============"

        disease="\""+disease+"\""

        # Set GoogleCrawler options
#        self.SG.url = False
        self.SG.cached_site = True
        self.SG.site = "orpha.net"

        # Search Google
        googled = self.SG.get_results(disease)

        # What sites to look for among the results from Google
        orpha_link = None
        flag = False
        # Look in cached urls
        for cached_site in googled['cached_site']:
            if "Disease_Search.php" in cached_site and not flag: flag = True
            if "cgi-bin/OC_Exp.php" in cached_site and not flag: flag = True
            if flag:
                orpha_link = cached_site
                print "Orphanet cached url found"
                break

        # If no cached urls were found, look among the direct urls
        if not flag:
            for url in googled['url']:
                if "Disease_Search.php" in url and not flag: flag = True
                if "cgi-bin/OC_Exp.php" in url and not flag: flag = True
                if flag:
                    orpha_link = url
                    print "Orphanet url found"
                    break

        if orpha_link:
            print orpha_link
            opened_url = self.SG.open_url(orpha_link)

            # ======= BEGIN PARSING ======= #

            # Parse the relevant section
            parser = etree.HTMLParser()
            tree = lxml.etree.parse(opened_url, parser)
            disease_info=tree.xpath('//td[@class="twoColumnsTable"]//tr/td//text()')

            # BEGIN SPECIAL CASE # 
            # In some cases google returns invalid cached urls
            if not disease_info:
                flag = False
                for url in googled['url']:
                    if "Disease_Search.php" in cached_site and not flag: flag = True
                    if "cgi-bin/OC_Exp.php" in cached_site and not flag: flag = True
                    if flag: 
                        orpha_link = url
                        print "Orphanet url SPECIAL CASE found"
                        break
                # Redo parsing
                opened_url = self.SG.open_url(orpha_link)
                parser = etree.HTMLParser()            
                tree = lxml.etree.parse(opened_url, parser)            
                disease_info=tree.xpath('//td[@class="twoColumnsTable"]//tr/td//text()')
                # Give up if it is still invalid
                if not disease_info:
                    print "Unable to locate Orphanet site"
                    return None
            # END SPECIAL CASE #

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
            # Note: Prevlance parsing does not work in most cases and leaves an
            # empty list. BeautifulSoup would be needed in a second run.
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
            
        time.sleep(25)
        
        print 
        
        
