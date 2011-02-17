
import lxml
import SearchGoogle

class Wikipedia(object):
    def __init__(self, query):
        self.site = 'en.wikipedia.org'
        self.results = []
        self.child_result = []
        self.parser = lxml.etree.HTMLParser()
        self.query = query

        self.sg = SearchGoogle.SearchGoogle()
        self.sg.results_per_page = 1
        self.sg.search_location = "any"
        self.sg.site = "en.wikipedia.org"

    def extract(self):
        urls = self.sg.get_results(self.query)['url']

        for url in urls:
            intermed_results = []
            opurl = self.sg.open_url(url)
            doc_tree = lxml.etree.parse(opurl, self.parser)

            div = doc_tree.xpath("//div[@id='bodyContent']")[0]
            divchildren = div.getchildren()

            self.child_result = []
            current = []

            for elm in divchildren:
                if elm.tag == "h2":
                    self.child_result.append(current)
                    current = []
                    current.append(elm.getchildren()[1])
                if elm.tag == "p" or elm.tag == "ul":
                    current.append(elm)
                if elm.tag == "h3":
                    current.append(elm.getchildren()[1])

            for li in self.child_result:
                abstract = ""
                for text in li:
                    if text.tag == "span":
                        abstract += "<%s>: " % text.text
                    else:
                        textit = text.itertext()
                        try:
                            while textit:
                                abstract += textit.next()
                        except StopIteration:
                            pass
                intermed_results.append(abstract)
                #FIXME: The intermediate results should be filtered,
                # only return introduction and sections related to symptoms?
            self.results.append(intermed_results)
        return {self.site: self.results}


