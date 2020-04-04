import requests
import os
import json

from connectors.sheetsv4 import SheetsV4
from config import SHEETS_V4
from connectors.redis import Redis

spreadsheet_id=os.environ.get('SPREADSHEET_ID', '')
api_key=os.environ.get('API_KEY', '')

def configure_user(key, username, user_id):
    access_token=SheetsV4.get_access_token()
    if access_token is None:
        print('Cannot get access token for accessing data store')
        print('Failed to configure user in datstore')
    else:
        user_info=create_datastore(access_token, key)
        if user_info is not None and 'data' in user_info and 'id' in user_info['data']:
            sheet_id=user_info['data']['id']
            status=configure_datastore(access_token, key)
            if status:
                try:
                    print('setting user in local store')
                    redis_cli=Redis.get_redis_client()
                    redis_cli.hset(
                        'task_manager_users',
                        key,
                        json.dumps({
                            'username': username,
                            'userid': user_id,
                            'sheetid': sheet_id,
                            'sheet_name': key
                        })
                    )
                    print('successfully configured user')
                except Exception as e:
                    print('Exception in redis connection', e)
            else:
                print('Cannot configure user in local store since configuration is not success')
        else:
            print('Failed to configure user since sheet id is not found in data')

def create_datastore(access_token, key):
    print('Creating user in datastore')
    create_sheet_path=SHEETS_V4['CREATE_SHEET'].replace('{spreadsheet_id}', spreadsheet_id)
    create_sheet_path=create_sheet_path.replace('{sheet_id}', key)
    endpoint=SHEETS_V4['ENDPOINT'] + create_sheet_path
    create_task=requests.post(
        endpoint,
        headers={'Authorization': api_key},
        params={'access_token': access_token}
    )
    if create_task.status_code == 201:
        print('Successfully created user in datastore')
        return create_task.json()
    else:
        print('Api_key used is:', api_key)
        print('access token used is:', access_token)
        print('Failure in creating user in datastore', create_task.json())
        return None

def configure_datastore(access_token, sheet_name):
    print('configuring data store')
    create_field_path=SHEETS_V4['CREATE_DATA'].replace('{spreadsheet_id}', spreadsheet_id)
    endpoint=SHEETS_V4['ENDPOINT'] + create_field_path
    create_fields=requests.post(
        endpoint,
        data=json.dumps({
            "values": [[
                'TITLE',
                'DESCRIPTION',
                'DATE',
                'START_TIME',
                'END_TIME',
                'TOTAL_TIME',
                'IS_COMPLETED',
                'SUB_TASKS',
                'UPDATED_AT',
                'CREATED_AT'
            ]]
        }),
        headers={'Authorization': api_key},
        params={'range': sheet_name, 'access_token': access_token}
    )
    if create_fields.status_code == 201:
        print('successfully configured the user in datastore')
        return True
    else:
        print('Api_key used is:', api_key)
        print('access token used is:', access_token)
        print('Failure in creating task', create_fields.json())
        return False