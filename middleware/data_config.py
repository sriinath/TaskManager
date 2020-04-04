import os
from falcon import HTTPServiceUnavailable

from connectors.sheetsv4 import SheetsV4

spreadsheet_id=os.environ.get('SPREADSHEET_ID', '')
sheet_id=os.environ.get('SHEET_ID', '')
api_key=os.environ.get('API_KEY', '')
sheet_name=os.environ.get('SHEET_NAME', '')

class DataConfig:
    def process_request(self, req, resp):
        if req.path != '/ping':
            req.context['SPREADSHEET_ID']=spreadsheet_id
            req.context['SHEET_ID']=sheet_id
            req.context['SHEET_NAME']=sheet_name
            req.context['API_KEY']=api_key
            access_token=SheetsV4.get_access_token()
            if access_token is None:
                raise HTTPServiceUnavailable(description='Cannot get access token for accessing data store')
            else:
                req.context['ACCESS_TOKEN']=access_token
