import scrapy
import re
import requests 

from csv import DictReader


class PeopleSpider(scrapy.Spider):
    name = 'people'
    custom_settings = {
        'ITEM_PIPELINES': {
            'parlaparser.pipelines.ParlaparserPipeline': 1
        },
        'CONCURRENT_REQUESTS': '1'
    }
    allowed_domains = ['https://data.rada.gov.ua']
    start_urls = ['https://data.rada.gov.ua/ogd/mps/skl9/mps09-data.csv']


    def parse(self, response):
        file_name = f'parlaparser/files/mps.csv'
        with open(file_name, 'wb') as f:
            f.write(response.body)
        with open(file_name) as rows:

            for row in DictReader(rows):

                full_name = row["full_name"].replace(',','')
                party_name = row["party_name"].replace(',','')

                print(full_name, party_name)

                row.update({
                    'type': 'person',
                    'role': 'member',
                })

                yield row
