
import lxml
import SearchGoogle

class RareDiseases(object):
    def __init__(self, query):
        self.site = 'rarediseases.org'
        self.results = []
        self.parser = lxml.etree.HTMLParser()
        self.query = query

        self.sg = SearchGoogle.SearchGoogle()
        self.sg.results_per_page = 1
        self.sg.search_location = "any"
        self.sg.site = "rarediseases.org"


    def extract(self):
        urls = self.sg.get_results(self.query)['url']

        for url in urls:
            opurl = self.sg.open_url(url)
            doc_tree = lxml.etree.parse(opurl, self.parser)

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

