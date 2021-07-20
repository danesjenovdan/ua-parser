from parlaparser.data_parsers.base_parser import BaseParser
import logging
from datetime import datetime


"""
{
                    'type': 'person',
                    'name': row['full_name'],
                    'org_name': row['party_name'],
                    'role': 'member',
                    'birthday': row['birthday'],
                    'gener': row['gender'],
                    'date_begin': row['date_begin'],
                    'date_end': row['date_end'],
                    'image': row['photo']
                }
"""

class PersonParser(BaseParser):
    def __init__(self, data, data_storage):
        super().__init__(data_storage)
        data = data

        organization_id, added_org = data_storage.get_or_add_organization(
            data['party_name'],
            {
                'name': data['party_name'],
                'parser_names': data['party_name'],
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
                    'role': data['role'] if data['role'] else 'member'
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
            # TODO save image
            # data_storage.parladata_api.upload_image(
            #     f'people/{person_id}',
            #     data['photo']
            # )
            # TODO add gender
