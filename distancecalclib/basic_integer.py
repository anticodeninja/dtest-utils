from itertools import combinations

from .base import BaseAlgorithm
from utils import calc_comb

class BasicIntegerAlgorithm(BaseAlgorithm):
    def __init__(self, data, func):
        super().__init__(data, func)

    def id(self):
        return "BaIntWOSH"
        
    def description(self):
        return "Basic Integer Algorithm w/o SH"

    def calc_shs(self, pattern_id):
        pdata = self._data.patterns[pattern_id]
        
        upper = sum(self.__distance(x1, x2) for x1, x2 in combinations(pdata, 2))
        bottom = calc_comb(len(pdata), 2)
        return (upper, bottom)

    def calc_shx(self, pattern_id, obj):
        pdata = self._data.patterns[pattern_id]
        
        upper = sum(self.__distance(x, obj) for x in pdata)
        bottom = len(pdata)
        return (upper, bottom)

    def __distance(self, v1, v2):
        return sum(self._func(x1, x2, self._data.features_len[i]) if x1 != None and x2 != None else 0
                   for i, (x1, x2) in enumerate(zip(v1, v2))) / self._data.features_count
