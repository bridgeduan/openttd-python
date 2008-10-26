
class DataStorageClass(object):
    def __init__(self, dict={}):
        self.__dict__ = dict
    def __getitem__(self, key):
        return self.__dict__[key]
    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            raise AttributeError
    def __setattr__(self, key, value):
        if not key == "__dict__":
            self.__dict__[key] = value
    def __delattr__(self, key):
        del self.__dict__[key]
    def getDict(self):
        return self.__dict__