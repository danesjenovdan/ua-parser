import requests

class BaseParser(object):
    def __init__(self, data_storage):
        self.data_storage = data_storage
        pass
