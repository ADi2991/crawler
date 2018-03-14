import scrapy
from bs4 import BeautifulSoup
import crawler.spiders.helper_functions as hf
import hashlib

class ProjectSpider(scrapy.Spider):
    name = "crawly"

    custom_settings = {
        'DUPEFILTER_CLASS':'scrapy.dupefilters.BaseDupeFilter'
    }

    titles = []
    my_urls = []
    img_urls = []
    indexed = dict()
    duplicate_urls = []

    def start_requests(self):
        urls = [
            'https://s2.smu.edu/~fmoore/',
            'https://s2.smu.edu/~fmoore/'
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        url_hash = hashlib.md5(response.body).hexdigest()
        print("hash this time: " + url_hash)
        if url_hash not in self.indexed:
            soup = BeautifulSoup(response.text, 'html.parser')
            self.titles.extend(soup.title.contents)
            self.my_urls.extend(hf.get_links(soup))
            self.img_urls.extend(hf.get_img_links(response.url, soup))
            print("titles:", self.titles)
            print("anchors:", self.my_urls)
            print("img_urls:", self.img_urls)
            self.indexed[url_hash] = response.url
        else:
            self.duplicate_urls.append(response.url)
            print('duplicate:', self.duplicate_urls)