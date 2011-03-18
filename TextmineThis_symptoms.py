import nltk
import scipy
import numpy
import re
import math
import hcluster

__author__ = "Henrik Groenholt Jensen"


class Textminer:
    
    """
    <description>
    
    @requires   python-nltk along with the english nltk stopword-corpus
    @requires   installation of the hcluster-library
    """
    def __init__(self):
        """
        <description>
        """
    
    
    def stem(self,data,stemmer=nltk.PorterStemmer()):
        """
        Simply stems words.
        
        @param data     list or str     A list of terms or a document.
        @param stemmer  nltk.*Stemmer   A stemmer from the nltk library 
                                          (PorterStemmer by default).
        
        @returns a list of lowercased stemmed words.
        """
        
        l=None
        if isinstance(data,str) or isinstance(data,unicode):
            ll = data.split(' ')
            ll = [stemmer.stem(term.strip().lower()) for term in ll if term != '']
            l = " ".join(ll)
        else:
            print data
            print type(data)
        
        return l
    
    
    def createTermDoc(self,data,stemming=True):
        """
        Create a term-document matrix.
        
        A term-count is given by the coordinat: 
            score = (symptom_hash[term],doc_hash[doc_id])
        These hashes are returned along with the matrix for later use and lookup.
        
        @param data         list    A list of tuples containing a document 
                                      id, the document and it's title.
                                      Example: [(id1,symptomlist1,title1),
                                                (id2,symptomlist2,title2),...]
        @param stemming     bool    Stem the words if True.
        @param rm_stopwords bool    Remove english stopwords if True.
        @param sanitizer    regexp  Provide a regular expression to sanitize 
                                      the document (default replaces all non-
                                      alphanumerical charecters with whitespaces)
        
        @returns a sparse dok-matrix (see scipy.sparse for info on the 'dok')
                 along with the term and document hashes.
        """
        # Build the hashes and scores
        symptom_hash, doc_hash, score_hash, name_hash = \
            self._getHashesAndScores(data,stemming)
        m = len(doc_hash); n = len(symptom_hash)
        
        termDoc = numpy.matrix(numpy.zeros((m,n)))
        for doc,tscores in score_hash.items():
            for term,score in tscores.items():
                try:
                    termDoc[doc_hash[doc],symptom_hash[term]] = score
                except:
                    print score
        
        return termDoc, symptom_hash, doc_hash, name_hash
    
    
    def runTFIDF(self,termDoc):
        """
        Creates a Term-Frequency Inverse-Document-Frequency from a sparse
        coo_matrix, using log-transformation on TF and IDF.
        
        @param termDoc      sparse matrix   A scipy.sparse term-doc matrix.
        
        @returns a tf-idf processed sparse matrix
        """
        
        term_counts = sum(termDoc>0).tolist()[0]
        
        print "Running TF-IDF..."
        for row in range(0,termDoc.shape[0]):
            for col in termDoc[row,:].nonzero()[1].tolist()[0]:
                tf = termDoc[row,col]
                
                try:
                    tf = math.log(1 + tf)
                except:
                    print "Error on term frequency. Got:",tf
                
                try:
                    idf = math.log(termDoc.shape[0] / term_counts[col])
                except:
                    raise ZeroDivisionError
                
                termDoc[row,col]=tf*idf
        
        return termDoc
    
    def queryTheMatrix(self,termDoc,query,term_hash,doc_hash, name_hash,
                        stemming=True):
        """
        Given a term-dcoument matrix and a term, document and name hash,
        a list of document scores are returned based on a string or list of
        terms (the query). The score represents the documents relevance to the
        query. The dcoument score is a simple a simple summation of the scores
        of each relevant term in the document.
        
        @param termDoc  sparse matrix   A scipy.sparse term-doc matrix.
        @param query      str/list      The query to from which scores are 
                                          produced.
        @param term_hash    dic     Term hash, where the term itself is the key.
        @param doc_hash     dic     Doc hash, where the id of the doc is the key.
        @param name_hash    dic     Name hash, where the id of the doc is the key.
        @param stemming     bool    Stem the words if True.
        @param rm_stopwords bool    Remove english stopwords if True.
        @param sanitizer    regexp  Provide a regular expression to sanitize 
                                      the document (default replaces all non-
                                      alphanumerical charecters with whitespaces).
        
        @returns a list of tuples containing the document name and score 
        - sorted by score in descending order.
        """
        
        # split by comma into symptom-terms
        if isinstance(query,str) or isinstance(query,unicode):
            searchTerms = [s.strip().lower() for s in query.split(',') if s!='']
        else:
            raise TypeError
        
        # stem the document
        if stemming: searchTerms = [self.stem(x) for x in searchTerms if x]
        
        print "Search terms: ",searchTerms
        
        scores = {}
        for term in searchTerms:
            try:
                n = term_hash[term]
            except:
                print "Term not found: '"+term+"'"
                continue
                
            docs = termDoc[n,:].nonzero()[1].tolist()[0]
            
            # Sum score measure:
            rev_doc_hash = dict(zip(doc_hash.values(),doc_hash.keys()))
            for doc in docs:
                score = termDoc[doc,n]
                
                doc_id = rev_doc_hash[doc] # extract the original orpha-nums 
                
                try:
                    scores[doc_id] += score
                except:
                    scores[doc_id] = score
        
        # Sort the scores (by value of course)
        scores = sorted(scores.items(), key=lambda (k,v): (v,k), reverse=True)
        # Replace orpha-nums with document titles
        scores = [(name_hash[s[0]],s[1]) for s in scores]
        
        # EXPERIMENT:
        # Normalized cumultative summation of the scores
        totalsum = float(sum([s[1] for s in scores]))
        scores = [(s[0],s[1]/totalsum*100) for s in scores]
        
        return scores
    
    
    #########################
     # AUXILLARY FUNCTIONS #
    #########################
    
    
    def _getHashesAndScores(self,data,stemming):
        """ (used by the createTermDoc-method)
        Build a symptom hash, a doc hash and a term-doc score hash
        
        @param data         list    A list of tuples containing a document 
                                      id and the document where the id is a 
                                      num and the document a string.
                                      Example: [(id1,doc1),(id2,doc2)]
        @param stemming     bool    Stem the words if True.
        @param sanitizer    regexp  Provide a regular expression to sanitize 
                                      the document (default replaces all non-
                                      alphanumerical charecters with whitespaces)
        
        @returns
            * a symptom hash, where the name of the symptom is the key,
            * a doc hash, where the id of the doc is the key,
            * a score hash, where the key is the symptom and doc hash 
                (e.g. score_hash[doc][symptom] = score)
            * and a name hash, where the id of the doc is the key.
        
        (Note that the hashes are zero-indexed!)
        """
        
        symptom_hash = {}
        doc_hash = {}
        name_hash = {}
        score_hash = {} # term-doc scores
        for disease in data:
            doc_id  = int(disease[0])
            symptom_dist = disease[1]
            name = disease[2]
            
#            # Sanitize symptoms
#            doc = sanitizer.sub(' ',doc)
#            
#            ### Mark irrelevant abstracts ###
#            qualifier = "term does not characterize a disease"
#            if qualifier in doc: name = "*"+name
            #################################
            
            if doc_hash.has_key(doc_id): continue # we don't want duplicates
            
            doc_hash[doc_id] = len(doc_hash) # assuming documents unique
            name_hash[doc_id] = name # name-hash for later quering..
            
            # stem the symptoms
            if stemming: symptom_dist = [(self.stem(x[0]),x[1]) for x in symptom_dist]
            
#            fdist = self.getWordCount(doc) # get the term distribution
            
            # build symptom hashes and term-doc scores
            score_hash[doc_id] = {}
            for symptom,score in symptom_dist:
                if not symptom_hash.has_key(symptom): 
                    symptom_hash[symptom] = len(symptom_hash)
                score_hash[doc_id][symptom] = score
        
        return symptom_hash, doc_hash, score_hash, name_hash


