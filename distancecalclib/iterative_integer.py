from itertools import chain

from .base import BaseAlgorithm

class IterativeIntegerAlgorithm(BaseAlgorithm):
    def __init__(self, data, func):
        super().__init__(data, func)

    def id(self):
        return "ItIntWSH"

    def description(self):
        return "Iterative Integer Algorithm w/ SH"

    def calc_shs(self, pattern_id):
        pdata = self._data.patterns[pattern_id]
        
        res = (0, 0)
        for i1, r1 in enumerate(chain.from_iterable(self.__iterate(x) for x in pdata)):
            for i2, r2 in enumerate(chain.from_iterable(self.__iterate(x) for x in pdata)):
                if i2 > i1:
                    res = self.__sum(res, self.__distance(r1, r2))
        return res

    def calc_shx(self, pattern_id, obj):
        pdata = self._data.patterns[pattern_id]
        
        res = (0, 0)
        for r1 in chain.from_iterable(self.__iterate(x) for x in pdata):
            for r2 in self.__iterate(obj):
                res = self.__sum(res, self.__distance(r1, r2))
        return res

    def __sum(self, s1, s2):
        return (s1[0] + s2[0], s1[1] + s2[1])

    def __iterate(self, value):
        current = [x if x != None else 0 for x in value]
        iterate_indexes = [i for (i,x) in enumerate(value) if x == None]

        yield current

        if len(iterate_indexes) > 0:
            while True:
                if current[iterate_indexes[0]] < self._data.features_max[iterate_indexes[0]]:
                    current[iterate_indexes[0]] += 1
                else:
                    carrier_index = None
                    for i in range(1, len(iterate_indexes)):
                        if current[iterate_indexes[i]] < self._data.features_max[iterate_indexes[i]]:
                            carrier_index = i
                            break

                    if carrier_index is None:
                        break
                
                    current[iterate_indexes[i]] += 1
                    for i in range(carrier_index):
                        current[iterate_indexes[i]] = self._data.features_min[iterate_indexes[i]]
            
                yield current
                    
    def __distance(self, v1, v2):
        return (sum(self._func(x[0], x[1], self._data.features_len[i]) for i, x in enumerate(zip(v1,v2))),
                self._data.features_count)
