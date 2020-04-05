import falcon
from threading import Thread
import os

from connectors.redis import Redis
from routes.Ping import Ping
from routes.Tasks import Tasks
from routes.TasksList import TasksList

from middleware.data_config import DataConfig
from middleware.auth import Authentication

api = falcon.API(middleware=[Authentication(), DataConfig()])
api.add_route('/ping', Ping())
api.add_route('/api/tasks', Tasks())
api.add_route('/api/tasks/{id:int}', TasksList())

try:
    redisThread=Thread(target=Redis.connect, args=())
    print('starting redis')
    redisThread.start()
    print('joining redis')
    redisThread.join()
    print('joined redis')
except Exception as e:
    print('Exception while connecting redis', e)

if __name__ == "__main__":
    from wsgiref import simple_server
    PORT = os.environ.get('PORT', 8000)
    httpd = simple_server.make_server('0.0.0.0', int(PORT), api)
    httpd.serve_forever()