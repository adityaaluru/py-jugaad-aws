import functools
import time, math
from . import logger as log, threadlocal, constants

logger = log.STLogger.getLogger(__name__)

def api(app):
    def decorator_api(apiHandler):
        @functools.wraps(apiHandler)
        def wrap_api(*args, **kwargs):

            # Pre processing
            startTime = time.time()*1000

            # Calling the inner function
            returnValue = apiHandler(*args, **kwargs)

            # Post processing
            timeElapsed = math.ceil(time.time()*1000 - startTime)
            logMsg = {
                    "timeElapsed":timeElapsed,
                    "request": {
                        "sourceIp": app.current_request.context["identity"]["sourceIp"],
                        "domainName": app.current_request.context["domainName"],
                        "method": app.current_request.method,
                        "path": app.current_request.context["resourcePath"],
                        "requestId": app.current_request.context["requestId"],
                    },
                    "response": {
                        "code": 200,
                        "message": "OK"
                    }
            }
            logger.info(logMsg)

            return returnValue
        return wrap_api
    return decorator_api

def extractThreadContext(app):
    if app.headers.get(constants.THREADLOCAL_TENANTID)