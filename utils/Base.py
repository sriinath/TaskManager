from connectors.redis import Redis
from falcon import HTTPInternalServerError, \
    HTTPError, \
    HTTPPreconditionFailed, \
    HTTPUnprocessableEntity, \
    HTTPServiceUnavailable, \
    HTTPConflict, \
    HTTPNotFound, \
    HTTPBadRequest, \
    HTTPUnauthorized, \
    HTTPForbidden, \
    HTTP_400

class Base:
    def raise_error(self, error_code=None, desc='Something went wrong in server'):
        if error_code and error_code != 500:
            if error_code == 401 or error_code == 403:
                redis_cli=Redis.get_redis_client()
                if redis_cli is not None:
                    access_token=redis_cli.delete('sheets_v4_access')
                else:
                    print('Redis client is not active')
            if error_code == 400:
                raise HTTPBadRequest(description=desc or '')
            elif error_code == 401:
                raise HTTPUnauthorized(description=desc or '')
            elif error_code == 403:
                raise HTTPForbidden(description=desc or '')
            elif error_code == 404:
                raise HTTPNotFound(description=desc or '')
            elif error_code == 409:
                raise HTTPConflict(description=desc or '')
            elif error_code == 412:
                raise HTTPPreconditionFailed(description=desc or '')
            elif error_code == 422:
                raise HTTPUnprocessableEntity(description=desc or '')
            elif error_code == 503:
                raise HTTPServiceUnavailable(description=desc or '')
            else:
                raise HTTPError(HTTP_400, description=desc or '', code=error_code)
        else:
            raise HTTPInternalServerError(description=desc or '')