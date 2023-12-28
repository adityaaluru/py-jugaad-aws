from time import sleep
import unittest
import threading
from starterlib.logger import STLogger
from starterlib.threadlocal import ThreadLocal

class TestLogger(unittest.TestCase):

    def logMessage(self,threadId,msg,logger):
        ThreadLocal.setData("caller","aditya.aluru-"+str(threadId))
        logger.warning("threadId: "+str(threadId)+msg)
        sleep(threadId)
        logger.error("threadId: "+str(threadId)+msg+"-returning from sleep")

    def test_formatter(self):
        logger = STLogger.getLogger(__name__)
        for index in range(3):
            threadObj = threading.Thread(target=self.logMessage,args=(index,"Log message",logger))
            threadObj.start()

if __name__ == '__main__':
    unittest.main()