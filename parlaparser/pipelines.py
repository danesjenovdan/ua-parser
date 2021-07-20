# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from parlaparser.utils.storage import DataStorage
from parlaparser.data_parsers.person_parser import PersonParser
from parlaparser.data_parsers.speeches_parser import SpeechesParser

import logging


class ParlaparserPipeline:
    def __init__(self, *args, **kwargs):
        super(ParlaparserPipeline, self).__init__(*args, **kwargs)
        logging.warning('........::Start parser:........')
        self.data_storage = DataStorage()

    def process_item(self, item, spider):
        if item['type'] == 'person':
            PersonParser(item, self.data_storage)
        elif item['type'] == 'speeches':
            SpeechesParser(item, self.data_storage)
        return ''
