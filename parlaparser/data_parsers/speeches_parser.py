from parlaparser.data_parsers.base_parser import BaseParser
from parlaparser import settings
from enum import Enum
from datetime import datetime
from babel.dates import format_date

import logging
import re
import locale
"""
{
    'type': 'speechess',
    'sitting': sitting,
    'date': date,
    'speeches': self.speeches
}
{
    'speaker': self.speaker,
    'content': self.content,
    'time': self.time,
    'order': self.order
}
"""
class SpeechesParser(BaseParser):
    def __init__(self, data, data_storage):
        super().__init__(data_storage)
        # set locale for parsing date
        locale.setlocale(locale.LC_TIME, "uk_UA")

        start_time = datetime.strptime(data['date'], "%d %B %Y")

        ua_date = format_date(start_time, format='d MMMM YYYY', locale='uk')
        sitting_name = f'ЗАСІДАННЯ, {ua_date}'

        session_id = self.data_storage.add_or_get_session({
            'name': sitting_name,
            'organization': self.data_storage.main_org_id,
            'organizations': [self.data_storage.main_org_id],
            'start_time': start_time.isoformat()
        })

        if session_id in self.data_storage.sessions_with_speeches:
            logging.warning('Speeches of this session was already parsed')
            return

        self.speeches = []
        for i, speech in enumerate(data['speeches']):
            person_id, added_person = data_storage.get_or_add_person(
                speech['speaker']
            )
            data['speeches'][i]['speaker'] = person_id
            data['speeches'][i]['session'] = session_id

            time = datetime.strptime(speech['time'], '%X').time()

            data['speeches'][i]['start_time'] = datetime.combine(start_time.date(), time).isoformat()


        self.data_storage.add_speeches(data['speeches'])
