import scrapy
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import nltk.stem.porter as porter
from collections import Counter


def get_links(soup):
    return [anchor['href'] for anchor in soup.find_all('a')]

def get_img_links(base, soup):
    return [base+img['src'] for img in soup.find_all('img')]

def tf_and_incidence(text):
    tokens = word_tokenize(text)
    filtered_tokens = [token for token in tokens if len(token)>1 or token.isalpha()]
    porter_stemmer = porter.PorterStemmer(mode = 'ORIGINAL_ALGORITHM')
    stemmed_tokens = list(map(porter_stemmer.stem, filtered_tokens))
    unique_stemmed_tokens = set(stemmed_tokens)
    return (Counter(stemmed_tokens), Counter(unique_stemmed_tokens))