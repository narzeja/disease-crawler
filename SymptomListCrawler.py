#!/usr/bin/python

"""Module for retrieving full list of symptoms from WrongDiagnosis, or
from existing file on filesystem.


"""

__author__ = 'Brian Soborg Mathiasen'
__version__= '1.0'
__modified__='07-02-2011'

import BaseCrawler
from BaseCrawler import BaseCrawler
import lxml
import lxml.html
from lxml import etree
import string
import os


class SymptomListCrawler(BaseCrawler):


    def __init__ (self):
        pass


    def get_symptoms(self, from_filesystem=False):

        if from_filesystem:
            try:
                fd = open('symptoms.dict', 'r')
                result_dict = eval(fd.read())
                fd.close()

                fd = open('symptoms.list', 'r')
                result_list = eval(fd.read())
                fd.close()

                return result_dict, result_list
            except Exception:
                print "no such file"
                return

        result_dict = {}
        result_list = []

        url = 'http://www.wrongdiagnosis.com/lists/symptoms.htm'

        html = self.open_url(url)

        parser = etree.HTMLParser()
        tree = lxml.etree.parse(html, parser)

        for key in string.uppercase:
            A_tag = tree.xpath("//a[@name='%s']" % key)[0]
            h2_tag = A_tag.getnext()
            ul_tag = h2_tag.getnext()
            listtags = ul_tag.getchildren()
            sublist = []

            for tag in listtags:
                text = tag.getchildren()[0].text
                sublist.append(text)

            result_dict.update({key: sublist}) # dict of crap
            result_list += sublist # list of crap

        fd = open('symptoms.dict', 'w')
        fd.write(str(result_dict))
        fd.close()

        fd = open('symptoms.list', 'w')
        fd.write(str(result_list))
        fd.close()

        return result_dict, result_list


