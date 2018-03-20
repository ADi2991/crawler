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

![picture](page_as_doc.png)
![picture](page_as_doc2.png)
![picture](url_stats.png)

* Data Structures:
- The different link stats (broken urls, links of duplicates, graphic file links, indexed links)
 are all stored in lists
- The words along with their counts are stored as key-value pairs 
  in a Counter (a Dictionary-based implementation in Python)
- A dictionary is used to store page response signatures (fingerprints) and their urls as key-value pairs respectively.
  A page with the same text will have the same signature, and hence will be a duplicate. This is output in the logs.
- Details of a parsed page are recorded and stored as a Document, which is a dictionary that holds values of
  url, term-incidence, term-frequency and the doc-id (signature/fingerprint).





