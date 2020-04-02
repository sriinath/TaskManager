import json
import os
import requests
from falcon import HTTP_201, HTTP_200
from json.decoder import JSONDecodeError

from connectors.sheetsv4 import SheetsV4
from config import SHEETS_V4
from utils.Base import Base
from utils.TaskManagerError import TaskManagerError

class Tasks(Base):
    def on_post(self, req, resp):
        try:
            req_body=json.load(req.bounded_stream)
            access_token=SheetsV4.get_access_token()
            if access_token is not None:
                if 'title' in req_body:
                    from datetime import date
                    today = date.today()
                    title=req_body.get('title')
                    desc=req_body.get('description', '')
                    start_date=req_body.get('start_date', '')
                    end_date=req_body.get('end_date', '')
                    total_time=req_body.get('total_time', '')
                    sub_tasks=req_body.get('sub_tasks', '{}')
                    is_completed=req_body.get('is_completed', False)
                    # dd/mm/YY
                    created_at=today.strftime("%d/%m/%Y")
                    updated_at=created_at

                    spreadsheet_id=os.environ.get('SPREADSHEET_ID', '')
                    sheet_name=os.environ.get('SHEET_NAME', '')
                    api_key=os.environ.get('API_KEY', '')
                    create_data_path=SHEETS_V4['CREATE_DATA'].replace('{spreadsheet_id}', spreadsheet_id)
                    endpoint=SHEETS_V4['ENDPOINT'] + create_data_path
                    create_task=requests.post(
                        endpoint,
                        data=json.dumps({
                            "values": [[
                                title,
                                desc,
                                start_date,
                                end_date,
                                total_time,
                                is_completed,
                                sub_tasks,
                                created_at,
                                updated_at
                            ]]
                        }),
                        headers={'Authorization': api_key},
                        params={'range': sheet_name, 'access_token': access_token}
                    )
                    if create_task.status_code == 201:
                        resp.body=json.dumps({
                            'status': 'Success',
                            'message': 'Successfully added the task'
                        })
                        resp.status=HTTP_201
                    else:
                        print('Api_key used is:', api_key)
                        print('Failure in creating task', create_task.json())
                        raise TaskManagerError(
                            message=create_task.json()['description'] or '',
                            status_code=create_task.status_code
                        )
                else:
                    raise TaskManagerError(
                        message='title is mandatory to process this request',
                        status_code=412
                    )
            else:
                raise TaskManagerError(message='Cannot get access token for accessing data store')
        except JSONDecodeError as err:
            print('Request body received', req.bounded_stream.read())
            print('Error while processing request', err)
            super().raise_error(desc='Cannot parse the body from the request', error_code=422)
        except TaskManagerError as e:
            super().raise_error(error_code=getattr(e, 'status_code'), desc=getattr(e, 'message'))
        except Exception as e:
            print('Exception occured while creating sheet', e)
            super().raise_error(desc='Something went wrong while creting sheet')

    def on_delete(self, req, resp, id):
        start_index=req.params.get('start_index', required=True)
        end_index=req.params.get('end_index', required=True)
        try:
            access_token=SheetsV4.get_access_token()
            if access_token is not None:
                if id:
                    spreadsheet_id=os.environ.get('SPREADSHEET_ID', '')
                    sheet_id=os.environ.get('SHEET_ID', '')
                    api_key=os.environ.get('API_KEY', '')
                    delete_data_path=SHEETS_V4['DELETE_DATA'].replace('{spreadsheet_id}', spreadsheet_id)
                    endpoint=SHEETS_V4['ENDPOINT'] + delete_data_path
                    create_task=requests.delete(
                        endpoint,
                        headers={'Authorization': api_key},
                        params={
                            'sheet_id': sheet_id,
                            'access_token': access_token,
                            'start_index': start_index,
                            'end_index': end_index
                        }
                    )
                    if create_task.status_code == 200:
                        resp.status=HTTP_200
                        resp.body=json.dumps({
                            'status': 'Success',
                            'message': 'Successfully deleted the task'
                        })
                    else:
                        print('Api_key used is:', api_key)
                        print('Failure in deleting task', create_task.json())
                        raise TaskManagerError(
                            message=create_task.json()['description'] or '',
                            status_code=create_task.status_code
                        )                    
                else:
                    raise TaskManagerError(
                        message='id is mandatory and cannot be empty to process this request',
                        status_code=412
                    )
            else:
                raise TaskManagerError(message='Cannot get access token for accessing data store')
        except TaskManagerError as e:
            super().raise_error(error_code=getattr(e, 'status_code'), desc=getattr(e, 'message'))
        except Exception as e:
            print('Exception occured while creating sheet', e)
            super().raise_error(desc='Something went wrong while creting sheet')
