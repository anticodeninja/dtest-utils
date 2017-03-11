from itertools import combinations

from .base import BaseAlgorithm
from utils import calc_comb

class ReducedBinaryAlgorithm(BaseAlgorithm):
    def __init__(self, data, func):
        super().__init__(data, func)

    def id(self):
        return "ReBinWSH"

    def description(self):
        return "Reduced Binary Algorithm w/ SH, suggested by AE Yankovskaya, fixed by AV Yamshanov"

    def calc_shs(self, pattern_id):
        pdata = self._data.patterns[pattern_id]
        
        upper = sum(self.__t2(x1, x2) * 2 ** (self.__d1(x1) + self.__d1(x2)) for x1, x2 in combinations(pdata, 2)) +\
                sum(self.__d2(x1, x2) * 2 ** (self.__d1(x1) + self.__d1(x2) - 1) for x1, x2 in combinations(pdata, 2)) +\
                sum(2 * self.__d1(x) * calc_comb(2 ** (self.__d1(x) - 1), 2) for x in pdata) +\
                sum(self.__t1(x) * calc_comb(2 ** self.__d1(x), 2) for x in pdata)
        bottom = self._data.features_count * sum(2 ** (self.__d1(x1) + self.__d1(x2)) for x1, x2 in combinations(pdata, 2)) +\
                 self._data.features_count * sum(calc_comb(2 ** self.__d1(x), 2) for x in pdata)
        return (upper, bottom)

    def calc_shx(self, pattern_id, obj):
        pdata = self._data.patterns[pattern_id]
                
        upper = sum(self.__t2(obj, x) * 2 ** (self.__d1(obj) + self.__d1(x)) for x in pdata) +\
                sum(self.__d2(obj, x) * 2 ** (self.__d1(obj) + self.__d1(x) - 1) for x in pdata)
        bottom = self._data.features_count * sum(2 ** (self.__d1(obj) + self.__d1(x)) for x in pdata)
        return (upper, bottom)

    def __d1(self, v):
        return sum(x is None for x in v)

    def __d2(self, v1, v2):
        return sum(x1 is None or x2 is None for x1, x2 in zip(v1, v2))

    def __t1(self, v):
        return sum(x is not None for x in v)

    def __t2(self, v1, v2):
        return sum(x1 == x2 and x1 is not None and x2 is not None for x1, x2 in zip(v1, v2))

