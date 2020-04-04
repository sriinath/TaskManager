import os
from falcon import HTTPUnauthorized, HTTPServiceUnavailable, HTTP_200
from google.oauth2 import id_token
from google.auth.transport import requests
import json
from threading import Thread

from connectors.redis import Redis

from processes import configure_user

CLIENT_ID=os.environ.get('CLIENT_ID', '')

class Authentication:
    def process_request(self, req, resp):
        if req.path != '/ping':
            token=req.get_header('Authorization')
            if token:
                try:
                    auth_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
                    if auth_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                        raise ValueError('Wrong issuer.')
                    username = auth_info['name']
                    userid = auth_info['sub']
                    constructed_id=username + '_' + userid
                    try:
                        redis_cli=Redis.get_redis_client()
                        user_info=redis_cli.hget('task_manager_users', constructed_id)
                        if user_info is None:
                            resp.body=json.dumps(dict(
                                is_new_user=True,
                                user_id=userid,
                                username=username
                            ))
                            resp.status=HTTP_200
                            resp.complete=True
                            user_thread=Thread(target=configure_user, args=(constructed_id, username, userid))
                            print('configuring new user')
                            user_thread.start()
                            print('New user configuration initiated')
                        else:
                            user_info=json.loads(user_info)
                            req.context['SHEET_ID']=user_info['sheetid']
                            req.context['SHEET_NAME']=user_info['sheet_name']
                    except Exception as e:
                        print('Exception in authenticating user', e)
                        raise HTTPServiceUnavailable(description='Exception in authenticating user')
                except ValueError:
                    raise HTTPUnauthorized(description='Token passed in header either expired or is not valid')
            else:
                raise HTTPUnauthorized(description='Authorization header is mandatory for processing the request')
