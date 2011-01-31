#!/usr/bin/python

"""name

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

class WrongdiagnosisCrawler(object):

    def __init__(self):
        self.SG=SearchGoogle()

    def get_disease_info(self,disease):

        print "========== NEW QUERY BEGUN ============"

        print "Disease: "+disease

        # Set GoogleCrawler options
        self.SG.site = "wrongdiagnosis.com"

        # Search Google
        googled = self.SG.get_results(disease)

        # What sites to look for among the results from Google
        flag1=False; flag2=False
        wd_link=None
        for url in googled['url']:
            if "intro.htm" in url: flag1 = True
            if "/medical/" in url and not flag1: flag2 = True
            if flag1:
                print url
                wd_link = url.replace('medical','a')
                print wd_link
                print "Wrongdiagnosis url found"
                break
            if flag2:
                print url
                wd_link = url.replace('medical','a')
                wd_link = wd_link.replace('.htm','/intro.htm')
                print wd_link
                print "Wrongdiagnosis url found"
                break

        if wd_link:
            print wd_link
            opened_url = self.SG.open_url(wd_link)
            print opened_url

            # ======= BEGIN PARSING ======= #

#/html/body/div[2]/div[3]/div[2]/p
#/html/body/div[2]/div[3]/div[2]/p[2]

            # Parse the relevant section
            parser = etree.HTMLParser()
            tree = lxml.etree.parse(opened_url, parser)
            #/html/body/div[2]/div[3]/div[2]/p
            disease_info=tree.xpath('//div[@id="wd_content"]/p')



            print disease_info

        else: print "Did not locate disease."


        time.sleep(25)
