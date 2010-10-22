#!/usr/bin/python

"""Module for retrieving diseases from Orphanet

Retrieves the initial list of diseases and urls to their description on 
Orphanet
"""

__author__ = 'Henrik Groenholt Jensen'
__version__= '1.0'
__modified__='21-10-2010'

from BaseCrawler import BaseCrawler
import lxml
import lxml.html
from lxml import etree

# should be moved to the controller module:
import time
import random

class OrphanetDiseaseCrawler(BaseCrawler):
        
    orphanet_url = 'http://www.orpha.net/consor/cgi-bin/Disease_Search_List.php?lng=EN&TAG='

    def __init__(self):
        pass

    def get_results(self,query=None):
        """Get a tubled list of disease urls and names

        In short: Go through all the disease categories ('A','B','C'...) using
        ListCrawlerBase and parse the pages with lxml

        @return: List of tubles on the form [(url,name)]
        @rtype: list of tubles 
        """

        results=[]

        pages = lambda: ['0'] + [chr(x) for x in range(65,90)]
        pages_url_base = "http://www.orpha.net/consor/cgi-bin/"

        for page in pages():
            result=None

            category_url = self.orphanet_url + page

            html = self.open_url(category_url)

            parser = etree.HTMLParser()
            tree = lxml.etree.parse(html, parser)
            specific_urls = tree.xpath("//div[@id='result-box']/ul/li/a")
            
            result=[(pages_url_base+url.get("href"),url.text) for url in specific_urls]
            
            results.extend(result)

            print "Current category:",page,"- retrived",len(result),"urls"
            print "In total:",len(results),"urls\n"

        return results



