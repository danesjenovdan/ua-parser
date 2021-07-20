from parlaparser.data_parsers.base_parser import BaseParser
from parlaparser import settings
from parlaparser.utils.storage import DataStorage
from enum import Enum
from collections import Counter
from datetime import datetime, timedelta

import logging
import re
import csv
import requests

OPTIONS = {
    '0': "absent",  # Absent
    '1': "for",     # For
    '2': "against", #Against
    '3': "absent",  # Abstain
    '4': "",        # Not voting
    '5': ""         # Usually we don't need this column
}

"""
voter_result example
{
    'date_agenda': '2019-08-29',
    'id_question': '2019082929',
    'id_event': '198',
    'for': '278',
    'against': '0',
    'abstain': '1',
    'not_voting': '20',
    'total': '417',
    'presence': '299',
    'absent': '118',
    'results': '2:1:1|3:1:1|4:6:1|5:1:1|6:6:1|7:6:0|8:6:1|9:3:1|10:6:1|11:1:1|12:6:0|13:6:0|14:6:0|15:1:1|16:1:1|17:1:1|18:1:1|19:1:1|20:1:1|21:1:1|22:1:1|23:1:1',
    'voting_result': '',
    'date_question': '2019-08-30T02:02:09',
    'type_event': '0',
    'date_event': '2019-08-30T02:07:50',
    'name_event': "Поіменне голосування про проект Постанови про календарний план проведення другої сесії Верховної Ради України дев'ятого скликання (№1087) - за основу та в цілому"}
}
"""


class VoteParser(BaseParser):
    def __init__(self, data_storage):
        super().__init__(data_storage)
        results = csv.DictReader(
            open("parlaparser/files/plenary_vote_results-skl9.tsv"),
            delimiter='\t',
            quoting=csv.QUOTE_NONE
        )
        results_dict = {line['id_event']: line
            for line in results
        }

        events = csv.DictReader(
            open("parlaparser/files/plenary_event_question-skl9.csv"),
            delimiter=',',
            quoting=csv.QUOTE_NONE
        )
        i=0
        result_event_ids = results_dict.keys()
        for event in events:
            if event['id_event']:
                if event['id_event'] in result_event_ids:
                    i+=1
                    results_dict[event['id_event']].update(event)

        # TODO for adding agenda items
        #data = requests.get("https://data.rada.gov.ua/ogd/zal/ppz/skl9/dict/agendas_9_skl.json").json()

        i=0
        for vote in results_dict.values():
            if i > 10:
                break
            if 'name_event' in vote.keys():
                start_time = datetime.fromisoformat(vote['date_event'])
                if vote['voting_result'] == '1':
                    result = True
                elif vote['voting_result'] == '0':
                    result = False
                else:
                    result = None
                new_motion = {
                    'title': vote['name_event'],
                    'text': vote['name_event'],
                    'datetime': start_time.isoformat(),
                    'result': result
                }

                new_vote = {
                    'name': vote['name_event'],
                    'timestamp': start_time.isoformat(),
                    'result': result
                }

                if not 'results' in vote.keys():
                    continue
                motion_obj = self.data_storage.set_motion(new_motion)
                new_vote['motion'] = motion_obj['id']
                vote_obj = self.data_storage.set_vote(new_vote)

                ballots = []

                for voter_result in vote['results'].split('|'):
                    mp_id, org_id, option = voter_result.split(':')
                    option = OPTIONS[option]
                    person_id, added_person = self.data_storage.get_or_add_person(
                        str(mp_id)
                    )
                    ballots.append({
                        'vote': vote_obj['id'],
                        'option': option,
                        'personvoter': person_id,
                    })

                self.data_storage.set_ballots(ballots)


if __name__ == "__main__":
    data_storage = DataStorage()
    vp = VoteParser(data_storage)
