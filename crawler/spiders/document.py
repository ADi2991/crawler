import scrapy


class Document(scrapy.Item):
    url = scrapy.Field()
    doc_id = scrapy.Field()
    tf = scrapy.Field()
    incidence = scrapy.Field()
    title = scrapy.Field()
    preview = scrapy.Field()
