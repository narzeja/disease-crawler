import SearchGoogle as SG
import TextmineThis as TT
import lxml
import lxml.html
from lxml import etree
import re
import time
import db as DB
import sqlite3
import unicodedata

class GCrawler():
    
    def __init__(self):
        """
        <description>
        """
        
        self.miner = TT.Textminer()
        self.searcher = SG.SearchGoogle()
        self.searcher.results_per_page = 20
        
        # Connect to existing database or initialise a new connection
        self.db_con = DB.db()
        self.db_cursor = self.db_con.c
    
    
    
    def crawlGoogle(self,patres,additional=None,corr_threshold=0.8):
        """
        <description>
        
        @param crawlData        list    List of search information on the form:
                                          [(disease name:str, initial info:str, 
                                           synonyms:list)]
        @param additional       str     Will be attached to each query.
        @param corr_threshold   float   Correlation (cosine by default) threshold.
        """
        
        # Selection: [patres INT, abstract TEXT, disease_name TEXT, author TEXT]
        crawlData = self.db_cursor.execute("SELECT * FROM disease_info "\
                                           "WHERE patres=?",[patres])
        crawlData = crawlData.fetchone()
        if not crawlData: raise KeyError
        
        # Optimizors
        whitelisted = {}
        blacklisted = self.db_cursor.execute("SELECT * FROM blacklisted_urls")
        blacklisted = [x[0] for x in blacklisted.fetchall()]
        
        patres          = crawlData[0]
        initial_info    = crawlData[1]
        query           = crawlData[2]
        
        print "Query:",query
        
        # Fetch synonyms of the disease name
        synonyms_sql = self.db_cursor.execute("SELECT DS.synonym "\
                                       "FROM disease_synonyms DS "\
                                       "WHERE DS.patres=?",[patres])
        synonyms = [x[0] for x in synonyms_sql.fetchall()]
        
        old_query = query 
        # append the query along with its synonyms
        if query not in synonyms: synonyms.append(query) 
        if additional: query += " "+additional # add additional search info
        
        try:
            urls = self.searcher.get_results(query)['url']
        except:
            print("\n---Killing the old Google Search instance---\n")
            # Some urls will be blocked by Google and searched for later
            try:
                self.db_cursor.execute("INSERT INTO missed_queries VALUES"\
                                        "(?,?)",[query,patres])
            except: pass # if it is already there, do nothing
            del self.searcher
            self.searcher = SG.SearchGoogle() # make a new searcher
        
        urlparser = re.compile(r'(.*)(//?)')
        blacklist_counter = 0; url_counter = 0
        for url in urls:
            # get the base of the url and skip if blacklisted
            url_base = re.search(urlparser,url).group(1)
            if url_base in blacklisted: 
                blacklist_counter += 1
                continue
            # crawl the page and optimize
            t1 = time.time()
            paragraphs = self.crawlURL(url,initial_info,synonyms,corr_threshold)
            t2 = time.time()-t1
            if paragraphs:
                url_counter += 1
                print 
                print "Paragraphs:",len(paragraphs)
                print "Site:",url
                
                paragraphs = "::".join(paragraphs)
                tup = [query,url,paragraphs]
                attributes = ["query","url", "data"]
                try:
                    # Insert [query TEXT, url TEXT, data TEXT]
                    self.db_cursor.execute("INSERT INTO googled_info VALUES (?,?,?)",
                                            tup)
                except:
                    print "Updating..."
                    self.db_cursor.execute("UPDATE googled_info SET "
                               + ", ".join([x+"=?" for x in attributes])
                               + " WHERE query=? AND url=?",
                                tup + [query,url])
            # If the parsing of the site takes over 25 sec or if the site
            # has not produced any results whitelist it
            elif not paragraphs or t2>25:
                if whitelisted.has_key(url_base):
                # If this has happened 6 times then blacklist the site
                    if whitelisted[url_base] == 5: 
                        try:
                            self.db_cursor.execute("INSERT INTO blacklisted_urls"
                                                + "VALUES (?)",[url_base])
                            blacklisted.append(url_base)
                        except: pass # if it is already blacklisted, do nothing
                    else: whitelisted[url_base] += 1
                else: whitelisted[url_base] = 1
        
        tup = [patres,query,url_counter,blacklist_counter]
        attributes = ["patres","query","recall","blacklisted"]
        try:
            # Insert [patres INT, query TEXT, recall INT, blacklisted INT]
            self.db_cursor.execute("INSERT INTO query VALUES (?,?,?,?)",
                            tup)
        except:
            self.db_cursor.execute("UPDATE query SET "
                        + ", ".join([x+"=?" for x in attributes])
                        + " WHERE patres=?",
                        tup + [patres])
        
        self.db_con.commit()
        
        print "Blacklisted:",blacklisted

    def crawlURL(self,url,initial_info,synonyms,corr_threshold=0.8):
        """
        Crawl a website for paragraphs that either has some similarity to the
        initial info, or little similarity but contains at least one of the
        synonyms.
        
        @param url              str     Website to be crawled
        @param  initial_info    str     Base information that the crawler texts
                                          are compared against.
        @param synonyms         list    The disease name along with synonyms and
                                          acronyms.
        @param corr_threshold   float   Correlation (cosine by default) threshold
        
        @returns a list containing the accepted texts (in any)
        """
        
        data = []
        page = self.searcher.open_url(url)
        
        # If the page couldn't be opened: give it 3 attempts
        count = 0
        while not page:
            print "Page could not be opened. Retrying in 2 secs (attempt "+str(count)+")"
            time.sleep(2)
            count+=1
            if count>2: return None
        
        parser = etree.HTMLParser()
        tree = lxml.etree.parse(page, parser)
         
        text = ""
        try:
            paragraphs = tree.xpath('//p')
        except AssertionError:
            return None
        for p in paragraphs:
            try:
                tmp = p.xpath('text()')
            except UnicodeDecodeError:
                print "Could not decode paragraph"
                continue
            
            tmp = " ".join(tmp) #
            tmp = tmp.split()   ## Ugly but works...
            tmp = " ".join(tmp) #
            
            if isinstance(tmp,unicode):
                tmp = unicodedata.normalize('NFKD', tmp).encode('ascii','ignore')
            
            lst = p.getchildren()
            for s in lst:
                try:
                    s = s.text
                except:
                    print "Could not "
                if isinstance(s,unicode):
                    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore')
                if s:
                    s = " ".join(s.split())
                    if s:
                        tmp += " "+s
            
            # Calculate the cosine similarity measure between the two documents
            score = self.miner.documentCorrelation(initial_info,tmp)
            
            # Sanitize for all non-alphanumerical characters
            sanitizer = re.compile('[\W]')
            synonyms = [sanitizer.sub(' ',x.lower()) for x in synonyms]
            tmp_old = tmp # return an unsanitized string
            tmp = sanitizer.sub(' ',tmp.lower())
            
            # Validate texts
            # ===============
            ## First test: Accept if above threshold
            # ---------------
            ## Second test: Accept if disease name (or a synonym) and one of the
            ## terms below are within the paragraph.
            if (score<corr_threshold) or \
                    (score<9.0 and\
                    re.search(r'characteri[s|z]ed by|characteristic|symptom|may include',tmp)\
                    and [x for x in synonyms if x+" " in tmp]): 
                data.append(tmp_old)
        
        return data
