from datetime import datetime, timedelta
from collections import OrderedDict

from parlaparser import settings

import scrapy
import re
import requests
import json


class SpeechesSpider(scrapy.Spider):
    name = 'speeches'
    custom_settings = {
        'ITEM_PIPELINES': {
            'parlaparser.pipelines.ParlaparserPipeline': 1
        },
        'CONCURRENT_REQUESTS': '1'
    }

    def __init__(self):
        url = f'https://data.rada.gov.ua/ogd/zal/agenda/skl9/stenogram-202101.json'
        print(url)
        response = requests.get(url)
        with open(f'parlaparser/files/session.json', 'wb') as f:
            f.write(response.content)
        with open('parlaparser/files/session.json') as data_file:
            self.data = json.load(data_file)

    def start_requests(self):
        end = datetime.now()
        months = OrderedDict(((settings.MANDATE_STARTIME + timedelta(_)).strftime(r"%Y%m"), None) for _ in range((end - settings.MANDATE_STARTIME).days)).keys()
        for month in months:
            url = f'https://data.rada.gov.ua/ogd/zal/agenda/skl9/stenogram-{month}.json'
            print(url)
            try:
                response = requests.get(url)
            except:
                continue
            if response.status_code >= 400:
                print(f'[ERROR] Got status code {response.status_code} from {url}')
                continue
            with open(f'parlaparser/files/session.json', 'wb') as f:
                f.write(response.content)
            with open('parlaparser/files/session.json') as data_file:
                self.data = json.load(data_file)
                for item in self.data.values():
                    if 'url' in item.keys():
                        request = scrapy.Request(item['url'], callback=self.parse)
                        request.meta['item'] = item
                        yield request
                    if 'urls' in item.keys():
                        for speeches_url in item['urls']:
                            request = scrapy.Request(speeches_url, callback=self.parse)
                            request.meta['item'] = item
                            yield request


    def parse_session_metadata(self, response):
        lines = ['sitting_name', 'location', 'date', 'chairman']
        cyrillic_all_caps_words = r'[\sАБВГҐДЂЃЕЁЄЖЅЗИІЇЙЈКЛЉМНЊОПРСТЋЌУЎФХЦЧЏШЩЪЫЬЭЮЯ.]+$'
        idx = 0
        rows = response.css(".sten_item_content > .MsoNormal[align=center] span::text, .sten_item_content > .MsoNormal[align=center]::text, .sten_item_content > div[align=center]::text").extract()
        output = {}
        for row in rows:
            row = row.strip()

            if lines[idx] == 'chairman':
                row = re.search(cyrillic_all_caps_words, row)
                if row:
                    row = row[0].strip()

            if not row:
                continue

            output[lines[idx]] = row
            idx += 1

            if idx > 3:
                break

        return output


    def parse(self, response):
        metadata = self.parse_session_metadata(response)
        chairman = metadata['chairman']
        sitting = metadata['sitting_name']

        date = response.css(".date::text").extract_first().strip()

        self.time = '00:00:00'
        self.speaker = None
        self.content = ''
        self.speeches = []
        self.order = 1

        time_regex = r'([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$'

        cyrillic_chars = r'^[\sАБВГҐДЂЃЕЁЄЖЅЗИІЇЙЈКЛЉМНЊОПРСТЋЌУЎФХЦЧЏШЩЪЫЬЭЮЯ.]+$'

        cyrillic_uppercase_start_person = r'(^[АБВГҐДЂЃЕЁЄЖЅЗИІЇЙЈКЛЉМНЊОПРСТЋЌУЎФХЦЧЏШЩЪЫЬЭЮЯ. ]{8,}\s)'

        for paragraph_dom in response.css(".MsoNormal")[5:]:
            center_paragraf = paragraph_dom.css("[align=center]::text")

            paragraph = paragraph_dom.css("::text").extract_first()
            if paragraph:
                paragraph = paragraph.strip()

            if center_paragraf:
                if re.match(cyrillic_chars, paragraph):
                    chairman = paragraph
                continue

            # pass if empty line
            if not paragraph:
                continue

            # find time
            elif re.match(time_regex, paragraph):
                self.time = paragraph

            # speech of chairman
            elif paragraph.startswith('ГОЛОВУЮЧИЙ') or paragraph.startswith('ГОЛОВУЮЧА'):
                if self.content:
                    self.add_speech()
                self.speaker = chairman
                self.content = paragraph[11:]

            # if parafraph contains all upper case chars is speeker name
            elif re.match(cyrillic_chars, paragraph):
                if self.content:
                    self.add_speech()
                self.speaker = paragraph
            # if is special paragraph with which starts with speker without time in the same paragraf of content
            elif re.match(cyrillic_uppercase_start_person, paragraph):
                if self.content:
                    self.add_speech()
                self.speaker = re.match(cyrillic_uppercase_start_person, paragraph)[0].strip()
                self.content = paragraph[len(self.speaker):].strip()
            else:
                self.content += ' ' + paragraph

        yield {
            'type': 'speeches',
            'sitting': sitting,
            'date': date,
            'speeches': self.speeches
        }


    def add_speech(self):
        self.speeches.append({
            'speaker': self.speaker,
            'content': self.content.strip(),
            'time': self.time,
            'order': self.order
        })
        self.content = ''
        self.order += 1
