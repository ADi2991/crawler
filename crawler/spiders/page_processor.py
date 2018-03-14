import scrapy
from bs4 import BeautifulSoup
import crawler.spiders.helper_functions as hf

class ProjectSpider(scrapy.Spider):
    name = "crawly"
    titles = []
    my_urls = []

    def start_requests(self):
        urls = [
            'https://s2.smu.edu/~fmoore/'
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        self.titles.extend(soup.title.contents)
        self.my_urls.extend(hf.get_links(soup))
        print(self.titles)
        print(self.my_urls)
