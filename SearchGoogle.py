#!/usr/bin/python

"""Search google for relevant urls

This class will return a dictionary of urls, cached site urls, titles and summaries
from a specified search on google. Optionally it can be specified where to look 
for the query terms  in the search and how many results that should be returned.

Example of use: 'Getting it all'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
run = SearchGoogle()
run.cached_site = True
run.summary = True
run.title = True
run.get_results("query")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Partial list of search parameters for Google:
http://code.google.com/apis/searchappliance/documentation/64/xml_reference.html
"""

__author__ = 'Henrik Groenholt Jensen and Brian Soborg Mathiasen'
__version__= '1.0'
__modified__='26-01-2011'

from BaseCrawler import BaseCrawler
import lxml
import lxml.html
from lxml import etree

import time

class SearchGoogle(BaseCrawler):

    _results_per_page = "&num=20"
    _search_loc = "&as_occt=any"
    _site = ""

    retlog = ""

    # Return options
    url = True
    cached_site = False
    summary = False
    title = False

    failed_searches = []

    _return_options = [url,cached_site,summary,title]

    _results_cache = {}

    def __init__(self):
        self.results = []

    # Examplified use of decorater properties:
    # - search.results_per_page (returns 50)
    # - search.results_per_page = 100 (set variable value to 100)


    #######################
     ## CRAWLER OPTIONS ##
    #######################

    @property
    def results_per_page(self):
        return self._results_per_page

    @property
    def search_location(self):
        return self._search_loc

    @property
    def site(self):
        if len(self._site):
            return self._site
        else:
            return "Error: No site option set."

    def query(self):
        return self._query


    @results_per_page.setter
    def results_per_page(self, num):
        """
        @param num: Set the number of results per page
        @param type: int
        """
        assert isinstance(num,int)
        assert num>=0 and num<=999
        self._results_per_page = "&num="+str(num)

    def query(self, query):
        """
        @param query: Set the search query
        @param type: str
        """
        assert isinstance(query, str)
        self.query = query


    @search_location.setter
    def search_location(self,loc="any"):
        """
        @param loc: Specifiy where to look for query terms. "any" by default.
        @param options: "any","url","body","links" or "title"
        @param type: str
        """
        assert loc=="any" or loc=="url" or loc=="title" or loc=="body" or \
        loc=="links"
        self._search_loc = "&as_occt="+loc

    @site.setter
    def site(self,url):
        """ """
        assert isinstance(url,str)
        self._site="&as_sitesearch="+url

    ######################
     ## SEARCH RESULTS ##
    ######################

    def return_options(self):
        """Get current return options"""
        return [('url',self.url),('cached site',self.cached_site),
                ('summary',self.summary),('title',self.title)]

    def _search(self):
        """Search google to get a list of (by default) 20 result urls

        @return: Returns a list og google urls in descending order
        @rtype: list of urls
        """

#        print

        search_url = ("http://www.google.com/search?hl=en&lr=lang_en"+self.query+
            self._results_per_page+self._search_loc+"&as_qdr=all"+self._site)

#        print "Url used for search: "+search_url

        results = self.open_url(search_url)

#        if not results:
#            print ("Time stamp: ", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime()))
#            print 'Google 503-fried us :/'
#            print "... failed, aborting current search!"
#            self.failed_searches.append(search_url)
#            return {}

#            print 'Sleeping...'
#            time.sleep(15)
#            print 'Woke up! Retrying...'
#            results = self.open_url(search_url)

#            if not results:
#                print "... failed, aborting current search!"
#                self.failed_searches.append(search_url)
#                return {}


        parser = etree.HTMLParser()
        tree = lxml.etree.parse(results, parser)

        result_fields = tree.xpath('//li[@class="g"]')

#        print "Found "+str(len(result_fields))+" fields"

        search_results={}
        search_results['url'] = []
        search_results['cached_site'] = []
        search_results['summary'] = []
        search_results['title'] = []

        for field in result_fields:

            if self.url:
                result=field.xpath('h3/a[@class="l"]')
                try:
                    search_results['url'].append(result[0].get('href'))
                except:
                    continue

            if self.cached_site:
                result=field.xpath('div//span[@class="gl"]/a[1]')
                if len(result):
                    if result[0].text=="Cached": 
                        result = result[0].get('href')
                    else: result = ""
                    try:
                        search_results['cached_site'].append(result)
                    except:
                        search_results['cached_site'] = []
                        search_results['cached_site'].append(result)

            if self.summary:
                result=field.xpath('div[@class="s"]/text()')
                result="".join(result)
                if isinstance(result,unicode): result.encode('UTF8')
                search_results['summary'].append(result)

            if self.title:
                result=field.xpath('h3/a[@class="l"]/text()')
                result="".join(result)
                if isinstance(result,unicode): result.encode('UTF8')
                search_results['title'] = []

        return search_results


    def get_results(self,query, try_cache=False):
        """Get a dictionary of search results (depending on options set)

        @return: Returns a list of googled urls in descending order
        @rtype: dic of

        @raise KeyError: If no searches have been cached
        """

        self.query = "&q="+query.replace(' ','+')

        if try_cache:
            try:
                results = self._results_cache[self.query]
                if results[1]!=self.return_options():
                    self._results_cache[self.query] = (self._search(),self.return_options())
                    results = self._results_cache[self.query]
            except KeyError:
                self._results_cache[self.query] = (self._search(),self.return_options())
                results = self._results_cache[self.query]

            # Clear cache if over 300
            if len(self._results_cache)>300: self._results_cache={}
            return results[0]
        else:
            results = self._search()
            return results

