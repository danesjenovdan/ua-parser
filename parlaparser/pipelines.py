# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from parlaparser.utils.storage import DataStorage
from parlaparser.data_parsers.person_parser import PersonParser
from parlaparser.data_parsers.speeches_parser import SpeechesParser
from settings import MANDATE, MANDATE_STARTIME, MAIN_ORG_ID, API_URL, API_AUTH

import logging


class ParlaparserPipeline:
    def __init__(self, *args, **kwargs):
        super(ParlaparserPipeline, self).__init__(*args, **kwargs)
        logging.warning('........::Start parser:........')
        self.storage = DataStorage(
            MANDATE, MANDATE_STARTIME, MAIN_ORG_ID, API_URL, API_AUTH[0], API_AUTH[1]
        )

    def process_item(self, item, spider):
        if item['type'] == 'person':
            PersonParser(item, self.storage)
        elif item['type'] == 'speeches':
            SpeechesParser(item, self.storage)
        return ''
