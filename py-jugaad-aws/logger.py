import json
import logging
from time import strftime, localtime
from .  import threadlocal
from . import utils
from . import constants

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
            "loggerName": record.name,
            "file": record.filename,
            "func": record.funcName,
            "lineNo": record.lineno,
            "thread": record.thread,
            "msg": record.msg,
            "exception": record.exc_info, # Handle this correctly
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

class STLogger:
    @staticmethod
    def getLogger(name):
        logger = logging.getLogger(name)
        logger.setLevel(STLogger.convertLogLevel(utils.getConfig(constants.LOG_LEVEL_KEY,constants.DEFAULT_LOG_LEVEL)))
        for handler in logger.handlers:
            logger.removeHandler(handler)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(STFormatter())
        logger.addHandler(consoleHandler)
        return logger
    
    @staticmethod
    def convertLogLevel(logLevelString:str):
        if logLevelString.upper() is "DEBUG":
            return logging.DEBUG
        if logLevelString.upper() is "INFO":
            return logging.INFO
        if logLevelString.upper() is "WARN" or "WARNING":
            return logging.WARNING
        if logLevelString.upper() is "ERROR":
            return logging.ERROR
        if logLevelString.upper() is "CRITICAL":
            return logging.CRITICAL
        return logging.INFO
