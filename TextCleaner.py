import FeatureExtractor as FE
import db as DB
import nltk


class TextCleaner(object):

    def __init__(self):
        self.fe = FE.FeatureExtractor(tagger='braubt', retrain=False)
        self.db = DB.db()


    def red_pill(self):
        qucursor = self.db.c.execute("select query, url, data from googled_info")

        qufetch = qucursor.fetchall()[:1]
        for (query, url, data) in qufetch:
            datasplit = data.split("::")
            newdata = []
            for d in datasplit:
                cleansed = self.clean_references(d)
                if cleansed:
                    newdata.append(d)

            paragraphs = "::".join(newdata)
            attributes = ["query", "url", "data"]
            tup = [query,url,paragraphs]
            try:
                self.db.c.execute("INSERT INTO googled_info_cleansed VALUES (?,?,?)", tup)
            except:
                self.db.c.execute("UPDATE googled_info_cleansed SET "
                           + ", ".join([x+"=?" for x in attributes])
                           + " WHERE query=? AND url=?",
                            tup + [query,url])

        self.db.sqlserver.commit()

    def clean_references(self, document):
        documents = self.fe.preprocess(document)
        dchunks = [nltk.ne_chunk(d) for d in documents]
        prev_chunk = None
        prev_prev_chunk = None
        result = []
        three_row = False
        for sentence in dchunks:
            for chunk in sentence:
                try:
                    if prev_prev_chunk == 'PERSON':
#                        print "PREV_PREV: person"
                        three_row = True

                    if prev_chunk == 'PERSON':
#                        print "PREV: person"
                        prev_prev_chunk = 'PERSON'

                    if chunk.node == 'PERSON':
#                        print "CURRENT: person"
                        prev_chunk = 'PERSON'

                except AttributeError:
                    pass
            if not three_row:
                result.append(sentence)
                prev_chunk = False
                prev_prev_chunk = False

        return result


