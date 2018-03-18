import scrapy
from bs4 import BeautifulSoup
import crawler.spiders.helper_functions as hf
import hashlib
from crawler.spiders.document import Document


class ProjectSpider(scrapy.Spider):
    name = "crawly"

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

    def start_requests(self):
        start_urls = [
            'https://s2.smu.edu/~fmoore/'
        ]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            page_signature = hashlib.md5(response.body).hexdigest()
            print("\n\nEntering " + response.url)
            if page_signature in self.indexed_page_signatures:
                self.duplicate_urls.append(response.url)
                print('This is a duplicate of ', self.indexed_page_signatures[page_signature])
            else:
                soup = BeautifulSoup(response.text, 'html5lib')
                current_page_anchors = []

                if hf.urltype(response.url) != 'txt':
                    # Adds title-contents
                    self.titles.extend(soup.title.contents)
                    # Adds links from anchor-tags in current page
                    current_page_anchors = hf.get_links(soup)
                    self.anchored_urls.extend(current_page_anchors)

                    # Adds links of graphic objects (images)
                    self.img_urls.extend(hf.get_img_links(response.url, soup))

                # Printing out title, anchor tags and image urls
                # print("titles:", self.titles)
                # print("anchors:", self.anchored_urls)
                # print("img_urls:", self.img_urls)

                # Hashing webpage for duplicate detection
                self.indexed_page_signatures[page_signature] = response.url

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

                print("Current page details:\n", document)

                # Add url to indexed urls
                self.indexed_urls.append(response.url)

                # Modify url frontier..
                for url in current_page_anchors:
                    # ..add only the links that haven't been visited yet
                    if url not in self.indexed_urls:
                        self.url_frontier.append(url)
                print("Updated frontier:", self.url_frontier)

                for url in self.url_frontier:
                    if hf.isInDomain(url) and hf.urlTypeSupported(url) and url not in self.indexed_urls:
                        if hf.isRestricted(url):
                            print("The url (%s) is restricted by robots.txt!" % url)
                        print("Will now head to: %s\n" % url)
                        self.url_frontier.remove(url)
                        yield scrapy.Request(url=url, callback=self.parse)
                    # else:
                    #     self.url_frontier.remove(url)
        else:
            self.broken_urls.append(response.url)
