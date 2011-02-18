#!/usr/bin/python

""" This module handles all crawling through a number of crawler
entities. It utilizes multiple existing crawlers to harvest documents
and paragraphs from known sites: orpha.net, medicinenet,
rarediseases.org, wrongdiagnosis.org

It collects information in relation to some query from each site
crawled, with the ability to ignore some crawler instances to focus the
harvesting.

The crawlers should be instantiated through customization of the
'SearchGoogle' class where each crawler should be instantiated with
their corresponding 'site' and extraction function The extraction
function defines how information and documents should be harvested from
each of the results of the site search.

e.g.
wrongdiagnosis may contain valuable information in <div
class="information"> tags, and information should be harvested as such.
where as medicinenet may contain the information we need immediately
after a <H2>Document</H2> tag.

"""

__author__ = 'Brian Soborg Mathiasen'
__version__= '1.0'
__modified__='10-02-2011'

import time
import RareDiseases as RD
import Wikipedia as WIKI

#class Pubmed(object):
#    def __init__(self):
#        self.site = 'ncbi.nlm.nih.gov'
#        self.results = []
#        self.parser = lxml.etree.HTMLParser()

#    def extract(sef, SG, query):
#        SG.site = self.site

#        urls = SG.get_results(query)['url']



#        return {self.site: self.results}


#class Wrongdiagnosis(object):
#    def __init__(self):
#        self.site = 'wrongdiagnosis.com'
#        self.results = []
#        self.parser = lxml.etree.HTMLParser()

#    def extract(self):
#        SG.site = self.site

#        urls = SG.get_results(query)['url']

#        wd_link=None
#        for url in urls:
#            if "intro.htm" in url:
#                wd_link = url
#            if "/medical/" in url and not flag1:
#                wd_link = url.replace('medical',query[0])
#                wd_link = wd_link.replace('.htm','/intro.htm')

#            if wd_link:
#                opened_url = SG.open_url(wd_link)

#                parser = lxml.etree.HTMLParser()
#                tree = lxml.etree.parse(opened_url, self.parser)
#                return tree
#                disease_info = tree.xpath('//div[@id="wd_content"]/p')


#        return {self.site: self.results}


#def initiateWikiCrawl(query="albinism", results_per_page=1, search_location="any"):
#    wiki = WIKI.Wikipedia(query)

#    documents = []
#    ret = wiki.extract()
#    return ret
#    documents.append(ret)

#    return documents


#def initiateRarediseasesCrawl(query="albinism", results_per_page=1, search_location="any"):
#    rd = RD.RareDiseases(query)
#    documents = []

#    ret = rd.extract()
#    return ret
#    documents.append(ret)

#    return documents

class CrawlerController(object):

    def __init__(self, query="albinism", results_per_page=1, search_location="any"):
        """
        @param results_per_page :: int # how many hits it should maximum return parser = etree.HTMLParser()
        @param query :: str # the string to search for
        @param loc :: str # where to search for 'query' (any, title, body, links, url)
        """
        self.documents = [] # this is the collection of harvested documents, documents :: [str]
        self.crawlers = []

        self.crawlers.append(RareDiseases(query, results_per_page, search_location))
        self.crawlers.append(Wikipedia(query, results_per_page, search_location))


    def initiateCrawlers(self):
        """ start each crawler instance, harvest documents and extract information using the extractor
        """
#        self.sg.site = self.RD.site
        for crawler in self.crawlers:
            self.documents.append(crawler.extract())

#        self.sg.site = self.Wiki.site
#        self.documents.append(self.RD.extract())
#        time.sleep(15)
#        self.documents.append(self.Wiki.extract())


