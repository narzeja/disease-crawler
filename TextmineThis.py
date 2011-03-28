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
    
    def getWordCount(self,data):
        """
        Counts the frequency distribution of terms.
        
        @param data     list or str     A list of terms or a document.
        
        @returns a list of lowercased terms and their frequencies.
        """
        
        if isinstance(data,list):
            l = []
            for terms in data:
                if terms != '': 
                    ll = terms.split(' ')
                    l.extend(ll)
            l = [term.strip().lower() for term in l if term != '']
            fdist = nltk.FreqDist(l)
        elif isinstance(data,str) or isinstance(data,unicode):
            l = [term.strip().lower() for term in data.split(' ') if term != '']
            fdist = nltk.FreqDist(l)
        else: 
            raise TypeError
        
        return fdist
    
    
    def stem(self,data,stemmer=nltk.PorterStemmer()):
        """
        Simply stems words.
        
        @param data     list or str     A list of terms or a document.
        @param stemmer  nltk.*Stemmer   A stemmer from the nltk library 
                                          (PorterStemmer by default).
        
        @returns a list of lowercased stemmed words.
        """
        
        if isinstance(data,list):
            l = []
            for terms in data:
                if terms != '': 
                    ll = terms.split(' ')
                    l.extend(ll)
            l = [stemmer.stem(term.strip().lower()) \
                for term in l if term != '']
        elif isinstance(data,str) or isinstance(data,unicode):
            l = [stemmer.stem(term.strip().lower()) \
                for term in data.split(' ') if term != '']
        else:
            raise TypeError
        
        return l
    
    
    def removeStopwords(self,data, 
                        stopList=nltk.corpus.stopwords.words("english")):
        """
        Removes stopwords in accordance to the nltk stopword-corpus using
        english words.
        
        @param data     list or str     A list of terms or a document.
        @param stopList list            By sending a stop word list to the
                                          function it allows a user defined 
                                          stop word list to be used instead 
                                          of the standard nltk stopword-corpus.
        
        @returns a list if non-stopwords.
        """
        
        if isinstance(data,list):
            l = [word.strip().lower() for word in data \
                if word not in stopList and word != '']
        elif isinstance(data,str) or isinstance(data,unicode):
            l = [word.strip().lower() for word in data.split(' ') \
                if word not in stopList and word != '']
        else:
            print type(data)
            raise TypeError
        
        return l
    
    def createTermDoc(self,data,stemming=True,rm_stopwords=True,
                        sanitizer=re.compile('[\W]')):
        """
        Create a term-document matrix.
        
        A term-count is given by the coordinat: 
            score = (term_hash[term],doc_hash[doc_id])
        These hashes are returned along with the matrix for later use and lookup.
        
        @param data         list    A list of tuples containing a document 
                                      id, the document and it's title.
                                      Example: [(id1,doc1,title1),
                                                (id2,doc2,title2),...]
        @param stemming     bool    Stem the words if True.
        @param rm_stopwords bool    Remove english stopwords if True.
        @param sanitizer    regexp  Provide a regular expression to sanitize 
                                      the document (default replaces all non-
                                      alphanumerical charecters with whitespaces)
        
        @returns a sparse dok-matrix (see scipy.sparse for info on the 'dok')
                 along with the term and document hashes.
        """
        # Build the hashes and scores
        term_hash, doc_hash, score_hash, name_hash = \
            self._getHashesAndScores(data,stemming,rm_stopwords,sanitizer)
        m = len(doc_hash); n = len(term_hash)
        
#        print "Building sparse term-doc matrix of size",m,"x",n
        
#        termDoc = scipy.sparse.dok_matrix((m, n))
        termDoc = numpy.matrix(numpy.zeros((m,n)))
        for doc,tscores in score_hash.items():
            for term,score in tscores.items():
                termDoc[doc_hash[doc],term_hash[term]] = score
        
        return termDoc, term_hash, doc_hash, name_hash
    
    
    def runTFIDF(self,tfidf):
        """
        Creates a Term-Frequency Inverse-Document-Frequency from a sparse
        coo_matrix, using log-transformation on TF and IDF.
        
        @param termDoc      sparse matrix   A scipy.sparse term-doc matrix.
        
        @returns a tf-idf processed sparse matrix
        """
        
        print "Converting to lil matrix format..."
#        tfidf = termDoc.tolil()
        print "Converting to csr and counting terms/doc occurences."
#        term_counts = [t.getnnz() for t in termDoc.tocsr().transpose()]
        term_counts = sum(tfidf>0).tolist()[0]
        
        print "Running TF-IDF..."
        for row in range(0,tfidf.shape[0]):
#            n=tfidf.getrow(row).nonzero()[1]
#            for col in (tfidf.getrow(row).nonzero()[1]):
            for col in tfidf[row,:].nonzero()[1].tolist()[0]:
                tf = tfidf[row,col]
                
                try:
                    tf = math.log(1 + tf)
                except:
                    print "Error on term frequency. Got:",tf
                
                try:
                    idf = math.log(tfidf.shape[0] / term_counts[col])
                except:
                    raise ZeroDivisionError
                
                tfidf[row,col]=tf*idf
        
        return tfidf
    
    def queryTheMatrix(self,termDoc,query,term_hash,doc_hash, name_hash,
                        stemming=True,rm_stopwords=True, 
                        sanitizer=re.compile('[\W]')):
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
        
        ####
        queryx = [sanitizer.sub(' ',x) for x in queryx]##
        
        queryx = [s.strip().lower() for s in query.split(',') if s!='']
#        queryx = [sanitizer.sub(' ',x) for x in queryx]
        queryx = [" ".join(self.stem(x)) for x in queryx if x]
        queryx = [self.removeStopwords(x.split(' ')) for x in queryx]
        print "Search terms:",queryx
        ####
        
        
        # Sanitize query terms
#        query = sanitizer.sub(' ',query)
#        
#        if isinstance(query,list):
#            searchTerms = [s.strip().lower() for s in query if s!='']
#        elif isinstance(query,str):
#            searchTerms = [s.strip().lower() for s in query.split(' ') if s!='']
#        else:
#            raise TypeError
#        
#        if rm_stopwords: 
#            searchTerms = self.removeStopwords(searchTerms) # remove stopwords
#        if stemming: 
#            searchTerms = self.stem(searchTerms) # stem the document
#        
#        print "Search terms: ",searchTerms
        
        #######
        scores = {}
        for terms in queryx:
            docs=[]
            for term in terms:
                try:
                    n = term_hash[term]
                except:
                    print "Term not found: '"+term+"'"
                    continue
                docs.extend(termDoc[:,n].nonzero()[0].tolist()[0])
            
            fq = nltk.FreqDist(docs)
            #docs = [x for x in docs if fq[x]==len(terms)]
            print "number of terms:",len(terms)
            print "number of terms divided by two:",len(terms)/2
            docs = [x for x in docs if fq[x]>len(terms)/2]
            
            # Sum score measure:
            rev_doc_hash = dict(zip(doc_hash.values(),doc_hash.keys()))
            for doc in docs:
                score = termDoc[doc,n]
                
                doc_id = rev_doc_hash[doc] # extract the original orpha-nums 
                
                try:
                    scores[doc_id] += score
                except:
                    scores[doc_id] = score
        #######
        
#        scores = {}
#        for term in searchTerms:
#            try:
#                n = term_hash[term]
#            except:
#                print "Term not found: '"+term+"'"
#                continue
#            
#            docs = set(termDoc[:,n].nonzero()[0].tolist()[0])
#            
#            # Sum score measure:
#            rev_doc_hash = dict(zip(doc_hash.values(),doc_hash.keys()))
#            for doc in docs:
#                score = termDoc[doc,n]
#                
#                doc_id = rev_doc_hash[doc] # extract the original orpha-nums 
#                
#                try:
#                    scores[doc_id] += score
#                except:
#                    scores[doc_id] = score
        
        # Sort the scores (by value of course)
        scores = sorted(scores.items(), key=lambda (k,v): (v,k), reverse=True)
        # Replace orpha-nums with document titles
        scores = [(name_hash[s[0]],s[1]) for s in scores]
        
        # EXPERIMENT:
        # Normalized cumultative summation of the scores
        totalsum = float(sum([s[1] for s in scores]))
        scores = [(s[0],s[1]/totalsum*100) for s in scores]
        
        return scores
    
    
    def documentCorrelation(self,doc1,doc2,measure=hcluster.cosine,
                            stemming=True,rm_stopwords=True,
                            sanitizer=re.compile('[\W]')):
        """
        Calculates the (by default cosine) correlation of two documents
        
        @param doc1       str/list  Document one
        @param doc2       str/list  Document two
        @param measure    hcluster  Similarity measure from hcluster (cosine by
                                      default). Must be a measure of the 
                                      smilairty of two vectors.
        @param stemming     bool    Stem the words if True.
        @param rm_stopwords bool    Remove english stopwords if True.
        @param sanitizer    regexp  Provide a regular expression to sanitize 
                                      the document (default replaces all non-
                                      alphanumerical charecters with whitespaces)
        
        @returns the similarity score
        """
        data = [("1",doc1,"document 1"),("2",doc2,"document 2")]
        
        termDoc,_,_,_ = self.createTermDoc(data,stemming,rm_stopwords,sanitizer)
        termDoc = termDoc.todense()
        
        correlation_score = measure(termDoc[0,:],termDoc[1,:])
        
        return correlation_score
    
    
    #########################
     # AUXILLARY FUNCTIONS #
    #########################
    
    
    def _getHashesAndScores(self,data,stemming,rm_stopwords,sanitizer):
        """ (used by the createTermDoc-method)
        Build a term hash, a doc hash and a term-doc score hash
        
        @param data         list    A list of tuples containing a document 
                                      id and the document where the id is a 
                                      num and the document a string.
                                      Example: [(id1,doc1),(id2,doc2)]
        @param stemming     bool    Stem the words if True.
        @param sanitizer    regexp  Provide a regular expression to sanitize 
                                      the document (default replaces all non-
                                      alphanumerical charecters with whitespaces)
        
        @returns
            * a term hash, where the name of the term is the key,
            * a doc hash, where the id of the doc is the key,
            * a score hash, where the key is the term and doc hash 
                (e.g. score_hash[doc][term] = score)
            * and a name hash, where the id of the doc is the key.
        
        (Note that the hashes are zero-indexed!)
        """
        
#        print "Building hashes and scores..."
#        if rm_stopwords:    print "Option set: 'Removing stopwords'"
#        if stemming:        print "Option set: 'Stemming'"
        
        term_hash = {}
        doc_hash = {}
        name_hash = {}
        score_hash = {} # term-doc scores
        for document in data:
            doc_id  = int(document[0])
            doc = document[1]
            name = document[2]
            
            # Sanitize terms
            doc = sanitizer.sub(' ',doc)
            
            ### Mark irrelevant abstracts ###
            qualifier = "term does not characterize a disease"
            if qualifier in doc: name = "*"+name
            #################################
            
            if doc_hash.has_key(doc_id): continue # we don't want duplicates
            
            doc_hash[doc_id] = len(doc_hash) # assuming documents unique
            name_hash[doc_id] = name # name-hash for later quering..
            
            if rm_stopwords: doc = self.removeStopwords(doc) # remove stopwords
            if stemming: doc = self.stem(doc) # stem the document
            fdist = self.getWordCount(doc) # get the term distribution
            
            # build term hashes and term-doc scores
            score_hash[doc_id] = {}
            for term,score in fdist.items():
                if not term_hash.has_key(term): 
                    term_hash[term] = len(term_hash)
                score_hash[doc_id][term] = score
        
        return term_hash, doc_hash, score_hash, name_hash


