from time import sleep
import unittest
from starterlib.logger import STLogger
from starterlib.threadlocal import ThreadLocal
from starterlib.httpclient import getHttpClient
from starterlib.config import getStaticConfig, getDynamicConfig, getFeatureConfig
import starterlib.constants as constants

class TestConfig(unittest.TestCase):

    def test_config(self):
        value = getStaticConfig("logLevel","DEFAULT")
        print("***Static Value:",value)
        value = getDynamicConfig("testKey","DEFAULT")
        print("***Value:",value)
        sleep(3)
        value = getDynamicConfig("testKey1","DEFAULT")
        print("***Value:",value)
        sleep(3)
        value = getDynamicConfig("testKey","DEFAULT")
        print("***Value:",value)

    def test_feature_config(self):
        value = getFeatureConfig("newfeature1")
        print("***Feature newfeature1:",ThreadLocal.getData(constants.THREADLOCAL_TENANTID), \
              ThreadLocal.getData(constants.THREADLOCAL_CALLER),"||",value)


if __name__ == '__main__':
    unittest.main()