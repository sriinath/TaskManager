import falcon

from connectors.redis import Redis
from routes.Ping import Ping
from routes.Tasks import Tasks
from routes.TasksList import TasksList

api = falcon.API()
api.add_route('/ping', Ping())
api.add_route('/api/tasks', Tasks())
api.add_route('/api/tasks/{id:int}', TasksList())

try:
    Redis.connect()
except Exception as e:
    print('Exception while connecting redis', e)

if __name__ == "__main__":
    from wsgiref import simple_server
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()