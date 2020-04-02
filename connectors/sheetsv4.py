import os
import requests
import json
from threading import Thread

from config import SHEETS_V4
from connectors.redis import Redis

class SheetsV4:
    __username=os.environ.get('V4_USERNAME', '')
    __password=os.environ.get('V4_PASSWORD', '')

    @staticmethod
    def __set_access_token(access_token):
        if access_token is not None:
            redis_cli=Redis.get_redis_client()
            if redis_cli is not None:
                redis_cli.set('sheets_v4_access', access_token)
            else:
                print('redis is not connected')

    @staticmethod
    def __get_access_info():
        if SheetsV4.__username and SheetsV4.__password:
            endpoint=SHEETS_V4['ENDPOINT'] + SHEETS_V4['LOGIN']
            sheets_access=requests.post(
                endpoint,
                data=json.dumps({'username': SheetsV4.__username, 'password': SheetsV4.__password})
            )
            sheets_access=sheets_access.json()
            print(sheets_access)
            if 'user' in sheets_access and 'access_token' in sheets_access['user']:
                access=sheets_access['user']['access_token']
                t=Thread(target=SheetsV4.__set_access_token, args=(access,))
                t.start()
                return access
            else:
                return None
        else:
            print('username and password to access v4 is not provided')
            return None

    @staticmethod
    def get_access_token():
        redis_cli=Redis.get_redis_client()
        if redis_cli is not None:
            access_token=redis_cli.get('sheets_v4_access')
            if access_token is not None:
                return access_token
        return SheetsV4.__get_access_info()