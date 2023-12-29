import time, math
import requests
from .  import threadlocal, constants
from . import logger as log
from requests.adapters import HTTPAdapter

# PENDING: Move these to constants
DEFAULT_RETRIES=2
DEFAULT_MAX_REDIRECTS=0
DEFAULT_TIMEOUT=(2,5)
DEFAULT_POOL_CONN=10
DEFAULT_POOL_MAX=10
DEFAULT_POOL_BLOCK=False


class STHttpAdapter(HTTPAdapter):
        def __init__(
            self,
            pool_connections=DEFAULT_POOL_CONN,
            pool_maxsize=DEFAULT_POOL_MAX,
            max_retries=DEFAULT_RETRIES,
            pool_block=DEFAULT_POOL_BLOCK,
            timeout = DEFAULT_TIMEOUT
            ): 
             self.__STtimeout__ = timeout
             super().__init__(pool_connections,pool_maxsize,max_retries,pool_block)

        def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
            logger = log.STLogger.getLogger(__name__)

            timeout = self.__STtimeout__

            if threadlocal.ThreadLocal.getData("correlationId") is not None:
                request.headers[constants.HTTP_CORRELATION_ID_HEADER] = threadlocal.ThreadLocal.getData(constants.THREADLOCAL_CORRELATION_ID)

            startTime = time.time()*1000
            response = super().send(request, stream=stream, timeout=timeout, verify=verify, cert=cert, proxies=proxies)
            timeElapsed = math.ceil(time.time()*1000 - startTime)

            logMsg = {
                 "requestUrl":response.request.url,
                 "responseCode":response.status_code,
                 "timeElapsed":timeElapsed
            }
            if response.status_code >= 300:
                logMsg["responseMsg"] = response.text
                logger.error(logMsg)
            else:
                logger.info(logMsg)

            return response

def getHttpClient(timeout=DEFAULT_TIMEOUT,max_redirects=DEFAULT_MAX_REDIRECTS, max_retries=DEFAULT_RETRIES):
  
    s = requests.Session()
    s.max_redirects = max_redirects

    optimizedAdapter = STHttpAdapter(max_retries=max_retries,timeout=timeout)
    s.mount("https://",optimizedAdapter)
    s.mount("http://",optimizedAdapter)

    return s


if __name__ == '__main__':
    response = getHttpClient().get('https://api.github.com/events')
    print(response.text)
