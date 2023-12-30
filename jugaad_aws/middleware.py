import functools
import time, math, uuid
from . import logger as log, threadlocal, constants, errors

logger = log.STLogger.getLogger(__name__)

def api(app,authZScope=None,exceptionHandler=None):
    def decorator_api(apiHandler):
        @functools.wraps(apiHandler)
        def wrap_api(*args, **kwargs):

            # Pre processing
            startTime = time.time()*1000
            logMsg = {
                "request": {
                    "sourceIp": app.current_request.context["identity"]["sourceIp"],
                    "domainName": app.current_request.context["domainName"],
                    "method": app.current_request.method,
                    "path": app.current_request.context["resourcePath"],
                    "requestId": app.current_request.context["requestId"],
                },
            }
            extractThreadContext(app.current_request.headers)

            # Authenticate the request
            if authZScope is not None:
                authenticate(app.current_request.headers,authZScope)

            # Calling the inner function
            try:
                returnValue = apiHandler(*args, **kwargs)
            except Exception as err:
                timeElapsed = math.ceil(time.time()*1000 - startTime)
                logMsg["timeElapsed"] = timeElapsed

                if exceptionHandler is not None:
                    returnValue = exceptionHandler(err)
                    logMsg["response"] = {
                        "message": "Exception raised by api handle: "+apiHandler.__name__
                    }
                    logger.exception(logMsg)
                else:
                    returnValue = getHTTPErrResponse(err)
                    logMsg["response"] = {
                        "code": returnValue.get("statusCode"),
                        "exception": type(err).__qualname__,
                        "errors": returnValue.get("errors")
                    }
                    logger.exception(logMsg)
            else:
                logMsg["response"] = {
                    "code": 200,
                    "message": "OK"
                }
                logger.info(logMsg)

            return returnValue
        return wrap_api
    return decorator_api

def extractThreadContext(headers):
    if headers.get(constants.HTTP_TENANT_ID_HEADER) is not None:
        threadlocal.ThreadLocal.setData(constants.THREADLOCAL_TENANTID,headers.get(constants.HTTP_TENANT_ID_HEADER))
    if headers.get(constants.HTTP_CORRELATION_ID_HEADER) is not None:
        threadlocal.ThreadLocal.setData(constants.THREADLOCAL_TENANTID,headers.get(constants.HTTP_CORRELATION_ID_HEADER))
    else:
        threadlocal.ThreadLocal.setData(constants.THREADLOCAL_CORRELATION_ID,uuid.uuid4().hex)

#This needs to be implemented
def authenticate(headers,authZScope):
    if headers.get(constants.HTTP_AUTH_KEY_HEADER) is not None:
        #Check a table with DDB for the allowed scopes for this api key.
        #If allowed, set the user context in the threadlocal (caller)
        pass
    else:
        if headers.get(constants.HTTP_AUTH_HEADER) is not None:
            #Validate the JWT token with the key and check if the token has the scopes defined.
            #Cache the JWT private key using dynamic configuration (use /GLOBAL_CONFIG_DYNAMIC/jwtKey in parameter)
            #Also support /GLOBAL_CONFIG_DYNAMIC/jwtKeyNew for key rotation
            #If allowed, set the user context in the threadlocal (caller)
            pass
    return

def getHTTPErrResponse(err):
    errResponse = {}
    errResponse["errors"] = err.args
    errResponse["statusCode"] = 500
    if isinstance(err,errors.BadRequestError):
        errResponse["statusCode"] = 400
    if isinstance(err,errors.UnAuthorizedError):
        errResponse["statusCode"] = 401
    if isinstance(err,errors.ForbiddenError):
        errResponse["statusCode"] = 403
    if isinstance(err,errors.NotFoundError):
        errResponse["statusCode"] = 404
    if isinstance(err,errors.LargeResponseError):
        errResponse["statusCode"] = 413
    if isinstance(err,errors.InternalServerError):
        errResponse["statusCode"] = 500
    return errResponse
