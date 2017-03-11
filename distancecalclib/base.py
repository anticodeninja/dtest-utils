class BaseAlgorithm:

    def __init__(self, data, func):
        self._data = data
        self._func = func

    def id(self):
        raise Exception('Not implemented')

    def description(self):
        raise Exception('Not implemented')

    def calc_shs(self, pattern_id):
        raise Exception('Not implemented')

    def calc_shx(self, pattern_id, obj):
        raise Exception('Not implemented')
