#!/usr/bin/python

"""name.

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

#from nltk import *

import time
import re

class KeywordCrawler(object):

    def __init__(self):
        self.SG=SearchGoogle()

    def get_disease_info(self,disease):
        
        print "========== NEW QUERY BEGUN ============"
        print "Disease: "+disease

        # Search Google
        googled = self.SG.get_results(disease)

        disease=disease.lower()
        disease_split=disease.split(' ')

        for url in googled['url']:
            print url
            opened_url = self.SG.open_url(url)

            # ======= BEGIN PARSING ======= #

            try:
                # Parse the relevant section
                parser = etree.HTMLParser()
                tree = lxml.etree.parse(opened_url, parser)
                disease_info=tree.xpath('//text()')

                for text in disease_info:
                    count=0
                    for word in disease_split:
#                        if word in text.lower():
#                            count+=1
#                        if count==len(disease_split):
                        if "characterized by" in text.lower()
                            print text
                            # Run FreqDist on the split string, removing empty strings in the process
#                            fdist = FreqDist([word.lower() for word in text.split(' ') if word != ''])
#                            print fdist

            except: 
                continue

            print "======================="



















