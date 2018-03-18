import scrapy
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import nltk.stem.porter as porter
from collections import Counter

base_url = 'https://s2.smu.edu/~fmoore/'
supported_types = ['txt', 'html', 'htm', 'php']
restricted_folder = '/dontgohere'

def get_links(soup):
    anchor_links = [anchor['href'] for anchor in soup.find_all('a')]
    anchored_urls = []
    for link in anchor_links:
        if 'http' not in link:
            anchored_urls.append(base_url+link)
        else:
            anchored_urls.append(link)
    return anchored_urls

def get_img_links(base, soup):
    return [base+img['src'] for img in soup.find_all('img')]

def tf_and_incidence(text):
    tokens = word_tokenize(text)
    filtered_tokens = [token for token in tokens if len(token)>1 or token.isalpha()]
    porter_stemmer = porter.PorterStemmer(mode = 'ORIGINAL_ALGORITHM')
    stemmed_tokens = list(map(porter_stemmer.stem, filtered_tokens))
    unique_stemmed_tokens = set(stemmed_tokens)
    return (Counter(stemmed_tokens), Counter(unique_stemmed_tokens))


def isInDomain(url):
    return base_url in url


def urlTypeSupported(url):
    return urltype(url) in supported_types


def urltype(url):
    return url[url.find('.', -5)+1:]


def isRestricted(url):
    return restricted_folder in url