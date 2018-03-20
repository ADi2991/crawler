To-dos
✔ List all URLs
✔ Contents of <TITLE> 
✔ Duplicate detection, report duplicate page URLs
✔ List URLs of graphic files
✔ tf-df with stemming
✔ 20 most common words
CSE7337, Aditya Rao (47221503)


This project requires the following python packages to be installed:
scrapy, beautifulsoup4 and nltk.

After navigating to the crawler directory, run

> scrapy crawl crawly

where crawly is the name of this crawler

* Most of the outputs (duplicates, indexed URLs, parsed documents, URL of graphic files, 20 most common words)
  are printed in the log.

* On successful run, the spider will also generate tf-df.csv in this directory, which contains all the
  term and document frequencies of parsed documents.

![alt text] (page_as_doc.png)
![alt text] (page_as_doc2.png)
![alt text] (url_stats.png)



