import scrapy
from bs4 import BeautifulSoup

def get_links(soup):
    return [anchor['href'] for anchor in soup.find_all('a')]

def get_img_links(base, soup):
    return [base+img['src'] for img in soup.find_all('img')]