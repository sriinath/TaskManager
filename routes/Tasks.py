import json
import requests
from falcon import HTTP_201, HTTP_200
from json.decoder import JSONDecodeError
from time import strptime

from config import SHEETS_V4
from utils.Base import Base
from utils.TaskManagerError import TaskManagerError

def format_data(task_data, start=0, end=10, start_date=None, end_date=None):
    result_data=list()
    start_date=strptime(start_date, "%d/%m/%Y") if start_date else None
    end_date=strptime(end_date, "%d/%m/%Y") if end_date else None
    for data in task_data:
        date=strptime(data['DATE'], "%Y-%m-%d") if 'DATE' in data else None
        if date is not None and (
            (not start_date and not end_date) or
            (not start_date or (start_date and date >= start_date)) and
            (not end_date or (end_date and date <= end_date))
            ):
            result_data.append(data)
    result_data.reverse()
    return result_data[start: end]

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
        req_params=req.params
        limit=req_params.get('limit', 10)
        offset=req_params.get('offset', 0)
        start_date=req_params.get('start_date', None)
        end_date=req_params.get('end_date', None)
        index=limit *  offset
        start_index=index + 1
        end_index=index = limit
        try:
            spreadsheet_id=req.context['SPREADSHEET_ID'] or ''
            sheet_name='srinath karthikeyan_cDZUZSHqFzLHjpz5iInsAeCD7R02'
            api_key=req.context['API_KEY'] or ''
            access_token=req.context['ACCESS_TOKEN'] or ''

            get_data_path=SHEETS_V4['GET_DATA'].replace('{spreadsheet_id}', spreadsheet_id)
            endpoint=SHEETS_V4['ENDPOINT'] + get_data_path
            title_range='{}!A1:J1'.format(sheet_name)
            data_range='{}'.format(sheet_name)
            get_task=requests.get(
                endpoint,
                headers={'Authorization': api_key},
                params={
                    'access_token': access_token,
                    'row_info': True,
                    'range': json.dumps([title_range, data_range])
                }
            )
            formatted_output=format_data(
                get_task.json()[1:],
                start_date=start_date,
                end_date=end_date,
                start=start_index,
                end=end_index
            )
            if get_task.status_code == 200:
                resp.status=HTTP_200
                resp.body=json.dumps({
                    'status': 'Success',
                    'data': formatted_output
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
