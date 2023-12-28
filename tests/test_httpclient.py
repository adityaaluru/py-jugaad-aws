from time import sleep
import unittest
from starterlib.logger import STLogger
from starterlib.threadlocal import ThreadLocal
from starterlib.httpclient import getHttpClient
class TestHttp(unittest.TestCase):

    def test_http(self):
        ThreadLocal.setData("correlationId","123123-1231231")
        response = getHttpClient().get('https://api.github.com/evnts')
        print(response.text)

if __name__ == '__main__':
    unittest.main()