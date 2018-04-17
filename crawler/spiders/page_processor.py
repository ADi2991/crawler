import scrapy
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import crawler.spiders.helper_functions as hf
import hashlib
from crawler.spiders.document import Document


class ProjectSpider(scrapy.Spider):
    name = "crawly"
    handle_httpstatus_list = [404]
    allowed_domains = ["s2.smu.edu"]

    custom_settings = {
        'DUPEFILTER_CLASS':'scrapy.dupefilters.BaseDupeFilter'
    }

    titles = []
    anchored_urls = []
    img_urls = []
    indexed_page_signatures = dict()
    duplicate_urls = []
    indexed_urls = []
    broken_urls = []
    url_frontier = []
    documents = []

    def start_requests(self):
        start_urls = [
            'https://s2.smu.edu/~fmoore/'
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if response.status == 404:
            if response.url not in self.indexed_urls:
                self.indexed_urls.append(response.url)
                if response.url in self.url_frontier:
                    self.url_frontier.remove(response.url)
                print("\nLink %s is broken, added to broken urls" % response.url)
                self.broken_urls.append(response.url)
                # self.indexed_urls.append(response.url)
                print("Broken urls: %s\n" % self.broken_urls)
                # if response.url in self.url_frontier:
                #     self.url_frontier.remove(response.url)

        if response.status == 200:
            if response.url not in self.indexed_urls:
                self.indexed_urls.append(response.url)
                if response.url in self.url_frontier:
                    self.url_frontier.remove(response.url)
                # if response.url not in self.indexed_urls:
                page_signature = hashlib.md5(response.body).hexdigest()
                print("\n\nEntering " + response.url)
                if page_signature in self.indexed_page_signatures:
                    self.duplicate_urls.append(response.url)
                    print('This is a duplicate of ', self.indexed_page_signatures[page_signature])
                else:
                    soup = BeautifulSoup(response.text, 'html5lib')
                    current_page_anchors = []
                    title = ""
                    preview = ""

                    if hf.urltype(response.url) != 'txt':
                        # Adds title-contents
                        title = soup.title.string
                        self.titles.append(title)

                        # Adds links from anchor-tags in current page
                        current_page_anchors = hf.get_links(soup, response)
                        self.anchored_urls.extend(current_page_anchors)

                        # Adds links of graphic objects (images)
                        self.img_urls.extend(hf.get_img_links(response, soup))
                    else:
                        file = response.url.split("/")[-1]
                        title = file[:-4]
                    # Add url to indexed urls
                    # self.indexed_urls.append(response.url)

                    # Printing out title, anchor tags and image urls
                    # print("titles:", self.titles)
                    # print("anchors:", self.anchored_urls)
                    # print("img_urls:", self.img_urls)

                    # Hashing webpage for duplicate detection
                    self.indexed_page_signatures[page_signature] = response.url

                    preview = " ".join(word_tokenize(soup.body.text)[:20])
                    # term-frequency and incidence
                    (tf, incidence) = hf.tf_and_incidence(soup.text)
                    # print("tf = ", tf)
                    # print("\n\n")
                    # print("incidence = ", incidence)

                    document = Document()
                    document['url'] = response.url
                    document['doc_id'] = page_signature
                    document['tf'] = tf
                    document['incidence'] = incidence
                    document['preview'] = preview
                    document['title'] = title

                    # print("Current page details:\n", document)
                    print("Page details recorded!")
                    self.documents.append(document)

                    # Modify url frontier..
                    for url in current_page_anchors:
                        # ..add only the links that haven't been visited yet
                        if url not in self.indexed_urls and url not in self.url_frontier:
                            self.url_frontier.append(url)
                            # Add img links from anchor tags
                            if hf.urltype(url) in ['jpg', 'jpeg', 'png', 'gif']:
                                self.img_urls.append(url)

                    print("\nFrontier with added links: %s" % self.url_frontier)

                    url_filters = lambda url: hf.is_in_domain(url) and \
                                              hf.url_type_supported(url) and not \
                                                  hf.isRestricted(url)

                    self.url_frontier = list(filter(url_filters, self.url_frontier))
                    print("\nFrontier with links filtered: %s\n" % self.url_frontier)

                    for url in self.url_frontier:
                        if url not in self.indexed_urls:
                            print("Will now head to: %s\n" % url)
                            yield scrapy.Request(url=url, callback=self.parse)
            # else:
            #     print("\n URL %s already visited" % response.url)