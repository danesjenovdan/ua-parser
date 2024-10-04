from parlaparser.data_parsers.base_parser import BaseParser
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

        session = self.data_storage.session_storage.get_or_add_object({
            'name': sitting_name,
            'organization': self.data_storage.main_org_id,
            'organizations': [self.data_storage.main_org_id],
            'start_time': start_time.isoformat(),
            'mandate': self.data_storage.mandate_id,
        })

        if session.get_speech_count() > 0:
            logging.warning('Speeches of this session was already parsed')
            return

        self.speeches = []
        for i, speech in enumerate(data['speeches']):
            person = data_storage.people_storage.get_or_add_object({
                'name': speech['speaker']
            })
            data['speeches'][i]['speaker'] = person.id
            data['speeches'][i]['session'] = session.id

            time = datetime.strptime(speech['time'], '%X').time()

            data['speeches'][i]['start_time'] = datetime.combine(start_time.date(), time).isoformat()


        session.add_speeches(data['speeches'])
