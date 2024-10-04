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

        organization = data_storage.organization_storage.get_or_add_object(
            {
                'name': data['party_name'],
                'parser_names': data['party_name'],
                'classification': 'pg'
            }
        )
        if organization.is_new:
            data_storage.organization_membership_storage.get_or_add_object(
                {
                    'member': organization.id,
                    'organization': data_storage.main_org_id,
                    'mandate': data_storage.mandate_id,
                }
            )

        parser_name = f'{data["last_name"]} {data["short_name"]}|{data["full_name"]}|{data["rada_id"]}'

        person = data_storage.person_storage.get_or_add_object(
            {
                'name': data['full_name'],
                'parser_names': parser_name,
                'date_of_birth': datetime.strptime(data['birthday'], '%d.%m.%Y').date().isoformat(),
            }
        )
        if person.is_new:
            start_time = datetime.strptime(data['date_begin'], '%d.%m.%Y').isoformat()
            if data['date_end']:
                end_time = datetime.strptime(data['date_end'], '%d.%m.%Y').isoformat()
            else:
                end_time = None
            data_storage.membership_storage.get_or_add_object(
                {
                    'member': person.id,
                    'organization': organization.id,
                    'on_behalf_of': None,
                    'start_time': start_time,
                    'end_time': end_time,
                    'role': data['role'] if data['role'] else 'member',
                    'mandate': data_storage.mandate_id
                }
            )
            data_storage.membership_storage.get_or_add_object(
                {
                    'member': person.id,
                    'organization': data_storage.main_org_id,
                    'on_behalf_of': organization.id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'role': 'voter',
                    'mandate': data_storage.mandate_id
                }
            )
        else:
            pass

