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


import SearchGoogle as SG
import lxml

def pubmed_extractor(document):
    return


class Wikipedia(object):
    def __init__ (self):
        self.site = 'en.wikipedia.org'
        self.results = []

    def extract(self, SG):
        SG.site = self.site

        urls = SG.get_results(SG.query)['url']
        parser = lxml.etree.HTMLParser()

        for url in urls:
            doc_tree = lxml.etree.parse(url, parser)

            abstract = ""
            try:
                div_iterator = doc_tree.xpath("//div[@id='bodyContent']/p")[0].itertext()
            except IndexError:
                break
            try:
                while div_iterator:
                    abstract += div_iterator.next()
            except StopIteration:
                pass
            self.results.append(abstract)

        return {self.site: self.results}

class RareDiseases(object):
    def __init__ (self):
        self.site = 'rarediseases.org'
        self.results = []

    def extract(self, SG):#, document_tree):
        SG.site = self.site
        urls = SG.get_results(SG.query)['url']
        parser = lxml.etree.HTMLParser()

        for url in urls:
            doc_tree = lxml.etree.parse(url, parser)

            try:
                span_iterator = doc_tree.xpath("//span[@class='feature_body']")[0].itertext()
            except IndexError:
                break
            try:
                while not span_iterator.next() == 'General Discussion':
                    continue
            except StopIteration:
                break
            self.results.append(span_iterator.next())

        return {self.site: self.results}


class CrawlerController(object):

    def __init__ (self, results_per_page=1, query="albinism", search_location="any"):
        """
        @param results_per_page :: int # how many hits it should maximum return        parser = etree.HTMLParser()
        @param query :: str # the string to search for
        @param loc :: str # where to search for 'query' (any, title, body, links, url)
        """
        self.documents = [] # this is the collection of harvested documents, documents :: [str]
        self.crawlers = []
        self.sg = SG.SearchGoogle()
        self.sg.results_per_page = results_per_page
        self.sg.query = query
        self.sg.search_location = search_location
        self.crawlers.append(RareDiseases())
        self.crawlers.append(Wikipedia())


    def initiateCrawlers(self):
        """ start each crawler instance, harvest documents and extract information using the extractor
        """
#        self.sg.site = self.RD.site
        for crawler in self.crawlers:
            self.documents.append(crawler.extract(self.sg))

##        self.sg.site = self.Wiki.site
#        self.documents.append(self.Wiki.extract(self.sg))


