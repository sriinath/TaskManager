import json
import requests
from falcon import HTTP_201, HTTP_200
from json.decoder import JSONDecodeError

from config import SHEETS_V4
from utils.Base import Base
from utils.TaskManagerError import TaskManagerError

class Tasks(Base):
    def on_post(self, req, resp):
        try:
            req_body=json.load(req.bounded_stream)
            if 'title' in req_body:
                from datetime import datetime
                now = datetime.now()
                title=req_body.get('title')
                date=req_body.get('date', '')
                desc=req_body.get('description', '')
                start_time=req_body.get('start_time', '')
                end_time=req_body.get('end_time', '')
                total_time=req_body.get('total_time', '')
                sub_tasks=req_body.get('sub_tasks', '{}')
                is_completed=req_body.get('is_completed', False)
                created_at=now.strftime('%d/%m/%Y %H:%M:%S')
                updated_at=created_at

                spreadsheet_id=req.context['SPREADSHEET_ID'] or ''
                sheet_name=req.context['SHEET_NAME'] or ''
                api_key=req.context['API_KEY'] or ''
                access_token=req.context['ACCESS_TOKEN'] or ''

                create_data_path=SHEETS_V4['CREATE_DATA'].replace('{spreadsheet_id}', spreadsheet_id)
                endpoint=SHEETS_V4['ENDPOINT'] + create_data_path
                create_task=requests.post(
                    endpoint,
                    data=json.dumps({
                        "values": [[
                            title,
                            desc,
                            date,
                            start_time,
                            end_time,
                            total_time,
                            is_completed,
                            sub_tasks,
                            updated_at,
                            created_at
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
        except JSONDecodeError as err:
            print('Request body received', req.bounded_stream.read())
            print('Error while processing request', err)
            super().raise_error(desc='Cannot parse the body from the request', error_code=422)
        except TaskManagerError as e:
            super().raise_error(error_code=getattr(e, 'status_code'), desc=getattr(e, 'message'))
        except Exception as e:
            print('Exception occured while creating sheet', e)
            super().raise_error(desc='Something went wrong while creting sheet')

    def on_delete(self, req, resp):
        start_index=req.params.get('start_index', required=True)
        end_index=req.params.get('end_index', required=True)
        try:
            spreadsheet_id=req.context['SPREADSHEET_ID'] or ''
            sheet_id=req.context['SHEET_ID'] or ''
            api_key=req.context['API_KEY'] or ''
            access_token=req.context['ACCESS_TOKEN'] or ''

            delete_data_path=SHEETS_V4['DELETE_DATA'].replace('{spreadsheet_id}', spreadsheet_id)
            endpoint=SHEETS_V4['ENDPOINT'] + delete_data_path
            delete_task=requests.delete(
                endpoint,
                headers={'Authorization': api_key},
                params={
                    'sheet_id': sheet_id,
                    'access_token': access_token,
                    'start_index': start_index,
                    'end_index': end_index
                }
            )
            if delete_task.status_code == 200:
                resp.status=HTTP_200
                resp.body=json.dumps({
                    'status': 'Success',
                    'message': 'Successfully deleted the task'
                })
            else:
                print('Api_key used is:', api_key)
                print('Failure in deleting task', delete_task.json())
                raise TaskManagerError(
                    message=delete_task.json()['description'] or '',
                    status_code=delete_task.status_code
                )                    
        except TaskManagerError as e:
            super().raise_error(error_code=getattr(e, 'status_code'), desc=getattr(e, 'message'))
        except Exception as e:
            print('Exception occured while deleting sheet', e)
            super().raise_error(desc='Something went wrong while deleting sheet')

    def on_get(self, req, resp):
        limit=req.params.get('limit', 10)
        offset=req.params.get('offset', 0)
        index=limit *  offset
        start_index=index + 1
        end_index=index = limit
        try:
            spreadsheet_id=req.context['SPREADSHEET_ID'] or ''
            sheet_name=req.context['SHEET_NAME'] or ''
            api_key=req.context['API_KEY'] or ''
            access_token=req.context['ACCESS_TOKEN'] or ''

            get_data_path=SHEETS_V4['GET_DATA'].replace('{spreadsheet_id}', spreadsheet_id)
            endpoint=SHEETS_V4['ENDPOINT'] + get_data_path
            title_range='{}!A1:J1'.format(sheet_name)
            data_range='{}!A{}:J{}'.format(sheet_name, start_index + 1, end_index + 1)
            get_task=requests.get(
                endpoint,
                headers={'Authorization': api_key},
                params={
                    'access_token': access_token,
                    'row_info': True,
                    'range': json.dumps([title_range, data_range])
                }
            )
            if get_task.status_code == 200:
                resp.status=HTTP_200
                resp.body=json.dumps({
                    'status': 'Success',
                    'data': get_task.json()
                })
            else:
                print('Api_key used is:', api_key)
                print('Failure in getting task', get_task.json())
                raise TaskManagerError(
                    message=get_task.json()['description'] or '',
                    status_code=get_task.status_code
                )                    
        except TaskManagerError as e:
            super().raise_error(error_code=getattr(e, 'status_code'), desc=getattr(e, 'message'))
        except Exception as e:
            print('Exception occured while getting sheet', e)
            super().raise_error(desc='Something went wrong while getting sheet')
