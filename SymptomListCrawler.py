#!/usr/bin/python

"""Module for retrieving full list of symptoms from WrongDiagnosis, or
from existing file on filesystem.


"""

__author__ = 'Brian Soborg Mathiasen'
__version__= '1.0'
__modified__='10-02-2011'

import BaseCrawler
from BaseCrawler import BaseCrawler
import lxml
import string
import os
import SearchGoogle as SG

class SymptomListCrawler(BaseCrawler):


    def __init__ (self):
        self.symptoms_dict_by_letter = {}
        self.symptoms_list = []
        self.site = "http://medical-dictionary.thefreedictionary.com/"

    def get_symptoms_filesystem(self):
        try:
            fd = open('symptoms.dict', 'r')
            self.symptoms_dict_by_letter = eval(fd.read())
            fd.close()

            fd = open('symptoms.list', 'r')
            self.symptoms_list = eval(fd.read())
            fd.close()

#            return self.symptoms_dict_by_letter, self.symptoms_list

        except Exception:
            print "no such file(s), no symptoms loaded"
            return None

    def save_symptoms_filesystem(self):
        fd = open('symptoms.dict', 'w')
        fd.write(str(self.symptoms_dict_by_letter))
        fd.close()

        fd = open('symptoms.list', 'w')
        fd.write(str(self.symptoms_list))
        fd.close()

    def get_symptoms_medicinenet(self):

        for key in string.lowercase:
            url = 'http://www.medicinenet.com/script/main/alphaidx.asp?p=%s_sym' % key #(a_sym, b_sym...)
            html = self.open_url(url)

            parser = lxml.etree.HTMLParser()
            tree = lxml.etree.parse(html, parser)

            div_tag = tree.xpath("//div[@class='AZ_results']")[0]
            try:
                ul_tag = div_tag.getchildren()[2]

            except IndexError:
                print "No symptoms found for '%s', continuing anyway" %key
                break
            listtags = ul_tag.getchildren()
            sublist = []

            for li in listtags:
                text = string.lower(li.getchildren()[0].text)
                sublist.append(text)

            self.symptoms_dict_by_letter.update({key: sublist}) # dict of crap
            self.symptoms_list += sublist # list of crap


    def get_symptoms_wrongdiagnosis(self):

        url = 'http://www.wrongdiagnosis.com/lists/symptoms.htm'

        html = self.open_url(url)

        parser = lxml.etree.HTMLParser()
        tree = lxml.etree.parse(html, parser)

        for key in string.uppercase:
            A_tag = tree.xpath("//a[@name='%s']" % key)[0]
            h2_tag = A_tag.getnext()
            ul_tag = h2_tag.getnext()
            listtags = ul_tag.getchildren()
            sublist = []

            for tag in listtags:
                text = string.lower(tag.getchildren()[0].text)
                sublist.append(text)

            self.symptoms_dict_by_letter.update({string.lower(key): sublist}) # dict of crap
            self.symptoms_list += sublist # list of crap


    def symptomExists(self, symptom):
        """ matches whether the exact symptom exists in our known list of symptom
        """
        try:
            ret = symptom in self.symptoms_dict_by_letter[symptom[0]]
        except KeyError:
            return False
        return ret

    def addSymptom(self, symptom):
        symptom = string.lower(symptom)
        self.symptoms_list.append(symptom)
        self.symptoms_list.sort()

        thislist = self.symptoms_dict_by_letter[symptom[0]]
        thislist.append(symptom)
        thislist.sort()
        self.symptoms_dict_by_letter.update({symptom[0] : thislist})

    def getSymptomsContaining(self, symptom):
        """ return all symptoms for which 'symptom' is part of
        """
        symptoms = set(symptom.split(' '))
        results = []
        for s in self.symptoms_list:
            s_words = set(s.split(' '))
            if symptoms.issubset(s_words):
                results.append(s)
        return results

    def symptomExistsOnline(self, symptom):
        site = self.site+symptom.replace(' ', '+')
        html = self.open_url(site)
        parser = lxml.etree.HTMLParser()
        try:
            tree = lxml.etree.parse(html, parser)
        except TypeError:
            return False
        try:
            if "Word not found" in tree.xpath("//table[@id='ContentTable']/tr/td/div/p/text()")[0]:
                return False
        except:
            return tree.xpath("//td[@id='MainTitle']/h1")[0].text


