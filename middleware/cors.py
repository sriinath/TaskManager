import falcon
class CORS:
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS, POST, PUT, DELETE')
        if req.method == 'OPTIONS':
            raise falcon.http_status.HTTPStatus(falcon.HTTP_200, body='\n')