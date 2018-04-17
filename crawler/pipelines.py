# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from collections import Counter
import csv

class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

    def close_spider(self, spider):
        for i in range(len(spider.documents)):
            print("\nDocument %d :%s\n" % (i+1, spider.documents[i]))
        print("duplicate links: %s\n" % spider.duplicate_urls)
        print("broken links: %s\n" % spider.broken_urls)
        print("image links: %s\n" % spider.img_urls)
        print("indexed links: %s\n" % spider.indexed_urls)

        unified_word_count = self.get_unified_word_count(spider)
        print("20 most common words:\n", unified_word_count.most_common(20))

        self.fill_zero_counts(spider, self.normalize(unified_word_count))
        doc_freq = self.get_docfreq(spider)
        self.export_tfdf(spider.documents, doc_freq)
        self.export_doc_details(spider.documents)


    def get_unified_word_count(self, spider):
        unified_word_count = Counter()
        for doc in spider.documents:
            unified_word_count += doc['tf']
        return unified_word_count

    def normalize(self, unified_word_count):
        norm_wc = Counter(unified_word_count)
        for word in norm_wc:
            norm_wc[word] = 0
        return norm_wc

    def fill_zero_counts(self, spider, unified_word_counts):
        doc_freq = Counter()
        for doc in spider.documents:
            for word in unified_word_counts:
                if word not in doc['incidence']:
                    doc['tf'][word] = unified_word_counts[word]
                    doc['incidence'][word] = unified_word_counts[word]

    def get_docfreq(self, spider):
        doc_freq = Counter()
        for doc in spider.documents:
            doc_freq += doc['incidence']
        return doc_freq

    def export_tfdf(self, documents, doc_freq):
        with open('tf-df.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')

            #Column-names
            column_names = ['word']
            for i in range(len(documents)):
                column_names.append('Document '+str(i+1))
            column_names.append('df')
            writer.writerow(column_names)

            # Values
            for word in doc_freq:
                row = []
                tfs = [doc['tf'][word] for doc in documents]
                df = doc_freq[word]
                row.append(word)
                row.extend(tfs)
                row.append(df)
                writer.writerow(row)

    def export_doc_details(self, documents):
        with open('title_preview.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            column_names = ['Document', 'title', 'preview', 'url']
            writer.writerow(column_names)

            for i in range(len(documents)):
                row = list()
                row.append("Document "+str(i+1))
                row.append(documents[i]['title'])
                row.append(documents[i]['preview'])
                row.append(documents[i]['url'])
                writer.writerow(row)

