import json
import requests
from falcon import HTTP_200
from json.decoder import JSONDecodeError

from config import SHEETS_V4
from utils.Base import Base
from utils.TaskManagerError import TaskManagerError

class TasksList(Base):
    def on_delete(self, req, resp, id):
        try:
            if id:
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
                        'start_index': id,
                        'end_index': id + 1
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
            else:
                raise TaskManagerError(
                    message='id is mandatory and cannot be empty to process this request',
                    status_code=412
                )
        except TaskManagerError as e:
            super().raise_error(error_code=getattr(e, 'status_code'), desc=getattr(e, 'message'))
        except Exception as e:
            print('Exception occured while deleting sheet', e)
            super().raise_error(desc='Something went wrong while deleting sheet')
    
    def on_put(self, req, resp, id):
        try:
            req_body=json.load(req.bounded_stream)
            if id:
                desc=req_body.get('description', '')
                date=req_body.get('date', '')
                start_time=req_body.get('start_time', '')
                end_time=req_body.get('end_time', '')
                total_time=req_body.get('total_time', '')
                sub_tasks=req_body.get('sub_tasks', '{}')
                is_completed=req_body.get('is_completed', False)
                from datetime import datetime
                now = datetime.now()
                updated_at=now.strftime("%d/%m/%Y %H:%M:%S")

                spreadsheet_id=req.context['SPREADSHEET_ID'] or ''
                sheet_name=req.context['SHEET_NAME'] or ''
                api_key=req.context['API_KEY'] or ''
                access_token=req.context['ACCESS_TOKEN'] or ''

                update_data_path=SHEETS_V4['UPDATE_DATA'].replace('{spreadsheet_id}', spreadsheet_id)
                endpoint=SHEETS_V4['ENDPOINT'] + update_data_path
                update_task=requests.put(
                    endpoint,
                    data=json.dumps({
                        "data": [{
                            "range": '{}!B{}:I{}'.format(sheet_name, id + 1, id + 1),
                            "values": [[
                                desc,
                                date,
                                start_time,
                                end_time,
                                total_time,
                                is_completed,
                                sub_tasks,
                                updated_at
                            ]]
                        }]
                    }),
                    headers={'Authorization': api_key},
                    params={'access_token': access_token}
                )
                if update_task.status_code == 200:
                    resp.body=json.dumps({
                        'status': 'Success',
                        'message': 'Successfully added the task'
                    })
                    resp.status=HTTP_200
                else:
                    print('Api_key used is:', api_key)
                    print('Failure in creating task', update_task.json())
                    raise TaskManagerError(
                        message=update_task.json()['description'] or '',
                        status_code=update_task.status_code
                    )
            else:
                raise TaskManagerError(
                    message='id is mandatory and cannot be empty to process this request',
                    status_code=412
                )
        except JSONDecodeError as err:
            print('Request body received', req.bounded_stream.read())
            print('Error while processing request', err)
            super().raise_error(desc='Cannot parse the body from the request', error_code=422)
        except TaskManagerError as e:
            super().raise_error(error_code=getattr(e, 'status_code'), desc=getattr(e, 'message'))
        except Exception as e:
            print('Exception occured while updating sheet', e)
            super().raise_error(desc='Something went wrong while updating sheet')

    def on_get(self, req, resp, id):
        try:
            if id:
                spreadsheet_id=req.context['SPREADSHEET_ID'] or ''
                sheet_name=req.context['SHEET_NAME'] or ''
                api_key=req.context['API_KEY'] or ''
                access_token=req.context['ACCESS_TOKEN'] or ''

                get_data_path=SHEETS_V4['GET_DATA'].replace('{spreadsheet_id}', spreadsheet_id)
                endpoint=SHEETS_V4['ENDPOINT'] + get_data_path
                title_range='{}!A1:J1'.format(sheet_name)
                data_range='{}!A{}:J{}'.format(sheet_name, id + 1, id + 1)
                get_task=requests.get(
                    endpoint,
                    headers={'Authorization': api_key},
                    params={
                        'access_token': access_token,
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
            else:
                raise TaskManagerError(
                    message='id is mandatory and cannot be empty to process this request',
                    status_code=412
                )                 
        except TaskManagerError as e:
            super().raise_error(error_code=getattr(e, 'status_code'), desc=getattr(e, 'message'))
        except Exception as e:
            print('Exception occured while getting sheet', e)
            super().raise_error(desc='Something went wrong while getting sheet')
