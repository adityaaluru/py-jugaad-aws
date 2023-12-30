import json
import logging, traceback
from time import strftime, localtime
from .  import threadlocal
from . import utils
from . import constants
import sys

# Usage examples:
# logger = STLogger.getLogger(__name__)
# logger.warning()

class STFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

    def format(self, record):
        logMsg = {
            "timestamp": strftime('%Y-%m-%dT%H:%M:%S%z', localtime(record.created)),
            "level": record.levelname,
            "caller": threadlocal.ThreadLocal.getData(constants.THREADLOCAL_CALLER),
            "tenantId": threadlocal.ThreadLocal.getData(constants.THREADLOCAL_TENANTID),
            "correlationId": threadlocal.ThreadLocal.getData(constants.THREADLOCAL_CORRELATION_ID),
            "appName": utils.getAppName(),
            "loggerName": record.name,
            "file": record.filename,
            "func": record.funcName,
            "lineNo": record.lineno,
            "thread": record.thread,
            "msg": record.msg,
            "exception": self.formatException(record.exc_info), # Handle this correctly
            #"task": record.taskName # FUTURE enhancement when AWS support Python 3.12 and above
        }
        if(record.levelno == logging.DEBUG):
            return json.dumps(logMsg)
        if(record.levelno == logging.INFO):
            infoLogMsg = logMsg.copy()
            infoLogMsg.pop("file")
            infoLogMsg.pop("func")
            infoLogMsg.pop("lineNo")
            infoLogMsg.pop("thread")
            infoLogMsg.pop("exception")
            return json.dumps(infoLogMsg)
        if(record.levelno == logging.WARNING):
            warnLogMsg = logMsg.copy()
            warnLogMsg.pop("file")
            warnLogMsg.pop("func")
            warnLogMsg.pop("thread")
            warnLogMsg.pop("lineNo")
            return json.dumps(warnLogMsg)
        if(record.levelno == logging.ERROR):
            errLogMsg = logMsg.copy()
            errLogMsg.pop("file")
            errLogMsg.pop("thread")
            return json.dumps(errLogMsg)
        if(record.levelno == logging.CRITICAL):
            return json.dumps(logMsg)

    def formatException(self,exc_info):
        if exc_info is not None:
            return traceback.format_exception(exc_info[1])
        else:
            return None

class STLogger:
    @staticmethod
    def getLogger(name):
        logger = logging.getLogger(name)
        logger.setLevel(STLogger.convertLogLevel(utils.getConfig(constants.LOG_LEVEL_KEY,constants.DEFAULT_LOG_LEVEL)))
        print("Logger Handlers: ",len(logger.handlers))
        for handler in logger.handlers:
            logger.removeHandler(handler)
        consoleHandler = logging.StreamHandler(stream=sys.stdout)
        consoleHandler.setFormatter(STFormatter())
        logger.addHandler(consoleHandler)
        return logger
    
    @staticmethod
    def convertLogLevel(logLevelString:str):
        if logLevelString.upper() == "DEBUG":
            return logging.DEBUG
        if logLevelString.upper() == "INFO":
            return logging.INFO
        if logLevelString.upper() == "WARN" or "WARNING":
            return logging.WARNING
        if logLevelString.upper() == "ERROR":
            return logging.ERROR
        if logLevelString.upper() == "CRITICAL":
            return logging.CRITICAL
        return logging.INFO
