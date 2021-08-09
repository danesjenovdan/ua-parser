from parlaparser.data_parsers.base_parser import BaseParser
from parlaparser import settings
from parlaparser.utils.storage import DataStorage
from enum import Enum
from collections import Counter
from datetime import datetime, timedelta

import re
import csv
import requests

remap = {
    'Фракція ПОЛІТИЧНОЇ ПАРТІЇ "СЛУГА НАРОДУ"': 'Слуга Народу',
    'Фракція Політичної Партії "ГОЛОС" у Верховній Раді України дев\'ятого скликання': 'Голос',
    'Фракція ПОЛІТИЧНОЇ ПАРТІЇ "ЄВРОПЕЙСЬКА СОЛІДАРНІСТЬ"': "ЄС",
    'Фракція Політичної партії "ОПОЗИЦІЙНА ПЛАТФОРМА - ЗА ЖИТТЯ" у Верховній Раді України': 'ОПЗЖ',
    'Фракція політичної партії Всеукраїнське об\'єднання "Батьківщина" у Верховній Раді України дев\'ятого скликання': 'Батьківщина',
    'Група "Партія "За майбутнє"': 'За майбутнє',
    'Група "ДОВІРА"': 'Довіра'
}

class PeopleParser(BaseParser):
    def __init__(self, data_storage):
        super().__init__(data_storage)
        url = 'https://data.rada.gov.ua/ogd/mps/skl9/mp-posts_ids.csv'
        response = requests.get(url)
        with open(f'parlaparser/files/mp-posts_ids.csv', 'wb') as f:
            f.write(response.content)

        url = 'https://data.rada.gov.ua/ogd/mps/skl9/mp-posts_unit.txt'
        response = requests.get(url)
        with open(f'parlaparser/files/mp-posts_unit.tsv', 'wb') as f:
            f.write(response.content)

        url = 'https://data.rada.gov.ua/ogd/mps/skl9/mps09-data.csv'
        response = requests.get(url)
        with open(f'parlaparser/files/mps09-data.csv', 'wb') as f:
            f.write(response.content)



        posts_ids = csv.DictReader(
            open("parlaparser/files/mp-posts_ids.csv"),
            delimiter=',',
        )
        post_unit = csv.reader(
            open("parlaparser/files/mp-posts_unit.tsv", encoding="windows-1251"),
            delimiter='\t',
        )
        mps_data = csv.DictReader(
            open("parlaparser/files/mps09-data.csv"),
            delimiter=',',
        )

        posts_ids = {post['mp_id']: post for post in posts_ids if post['unit_type'] in ['grp', 'fra']}

        # fix names
        post_unit = {post[0]: post[1] for post in post_unit}
        for id, post in post_unit.items():
            if post in remap.keys():
                post_unit[id] = remap[post]

        mps_data = {mp['id']: mp for mp in mps_data}

        for id, mp in mps_data.items():
            if id in posts_ids.keys():
                print(mps_data[id])
                print(posts_ids[id])
                print()
                mps_data[id].update(posts_ids[id])
                mps_data[id]['fraction'] = post_unit[mp['unit_id']]
            else:
                mps_data[id]['fraction'] = 'Позафракційні'

            data = mps_data[id]

            start_time = datetime.strptime(data['date_begin'], '%d.%m.%Y').isoformat()
            if data['date_end']:
                end_time = datetime.strptime(data['date_end'], '%d.%m.%Y').isoformat()
            else:
                end_time = None

            print(data)

            organization_id, added_org = data_storage.get_or_add_organization(
                data['fraction'],
                {
                    'name': data['fraction'],
                    'parser_names': data['fraction'],
                    'classification': 'pg'
                }
            )
            if added_org:
                data_storage.add_org_membership(
                    {
                        'member': organization_id,
                        'organization': data_storage.main_org_id
                    }
                )

            parser_name = f'{data["last_name"]} {data["short_name"]}|{data["full_name"]}|{data["rada_id"]}'

            person_id, added_person = data_storage.get_or_add_person(
                data['full_name'],
                {
                    'name': data['full_name'],
                    'parser_names': parser_name,
                    'birth_date': datetime.strptime(data['birthday'], '%d.%m.%Y').isoformat(),
                }
            )
            if added_person:
                start_time = datetime.strptime(data['date_begin'], '%d.%m.%Y').isoformat()
                if data['date_end']:
                    end_time = datetime.strptime(data['date_end'], '%d.%m.%Y').isoformat()
                else:
                    end_time = None
                data_storage.add_membership(
                    {
                        'member': person_id,
                        'organization': organization_id,
                        'on_behalf_of': None,
                        'start_time': start_time,
                        'end_time': end_time,
                        'role': 'member'
                    }
                )
                data_storage.add_membership(
                    {
                        'member': person_id,
                        'organization': data_storage.main_org_id,
                        'on_behalf_of': organization_id,
                        'start_time': start_time,
                        'end_time': end_time,
                        'role': 'voter'
                    }
                )


if __name__ == "__main__":
    data_storage = DataStorage()
    pp = PeopleParser(data_storage)
