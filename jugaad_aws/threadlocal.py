import threading

class ThreadLocal:
    @staticmethod
    def getData():
        threadData = {}
        keyPrefix = str(threading.get_ident())+"-"
        for key in threading.current_thread.__dict__:
            if(key.startswith(keyPrefix)):
                threadData[key.replace(keyPrefix,"")] = threading.current_thread.__dict__[key]
        return threadData
    @staticmethod
    def getData(key):
        keyPrefix = str(threading.get_ident())+"-"
        key = keyPrefix+key
        if(key in threading.current_thread.__dict__):
            return threading.current_thread.__dict__[key]
        else:
            return None
    @staticmethod
    def setData(key,value):
        keyPrefix = str(threading.get_ident())+"-"
        threading.current_thread.__dict__[keyPrefix+key] = value
    @staticmethod
    def resetData():
        keyPrefix = str(threading.get_ident())+"-"
        for key in threading.current_thread.__dict__.keys():
            if key.startswith(keyPrefix):
                threading.current_thread.__dict__.pop(key)
