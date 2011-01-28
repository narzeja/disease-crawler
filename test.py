#!/usr/bin/python

"""
This class is designed to test the boundaries given by the Google Search
engine in terms of number of queries pr. hour, and decay time for
retries when blocked.


"""


__author__ = 'Brian Soborg Mathiasen'
__version__= '1.0'
__modified__='26-01-2011'

import SearchGoogle as SG
import IOmodule as iom


class Test(object):


    def __init__ (self, query="test", npp=99, itt=99):
        """ standard search will results in 100 queries using the
        keyword 'test'.
        """
        self.query = query
        self.npp = npp #number of urls to fetch and open pr iteration
        self.diseasenames = iom.pickleIn('.', 'orphanet_urls')

        # load the search machine instance

        self.iterations = len(self.diseasenames)
        self.GM = SG.SearchGoogle()
        self.GM.results_per_page = self.npp
#        for i in range(0, itt):
#            self.GMs.append()
        self.resulting_url_list = []

    def start(self, from_itt=0, num_itt=10, query_terms=[]):
        """ initiates the test and iterates the diseasenames from
        'from_itt' and gets 'num_itt' at a time.
        """
        collected_missed_urls = []
        self.resulting_url_list = []
        j = from_itt
        range_end = from_itt + num_itt

        if not query_terms:
            query_terms = self.diseasenames

        if range_end > len(query_terms):
            range_end = len(query_terms)
        for i in range(from_itt, from_itt+num_itt):
            print("Search iteration:", j)
            url, query = query_terms[j]
#            query = self.query + str(i)
            try:
                self.resulting_url_list.append(self.GM.get_results(query)['url'])
                j += 1
            except:
                print("Killing the old Google Search instance")
                collected_missed_urls += (url, query)
                del self.GM
                self.GM = SG.SearchGoogle() # make a new searcher
                self.GM.results_per_page = self.npp
                print("Done!")
                j += 1
        print("Now I'm done, here are the failed searches: ")
        return collected_missed_urls

#            urls = res['url']
#        return resulting_urldict_list

    def open_all_results(self):

        i = 0
        for urls in self.resulting_url_list:
#            urls = urldict['url']
            for url in urls:
                print("opening url number: " + str(i))
                handle = self.GM.open_url(url)
                i += 1

