#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import combinations

from distancelib.base import BaseAlgorithm
from commonlib import calc_comb

class ReducedIntegerAlgorithm(BaseAlgorithm):
    def __init__(self, ranges, func):
        super().__init__(ranges, func)

    def id(self):
        return "ReIntWSH"
        
    def description(self):
        return "Reduced Integer Algorithm w/ SH, suggested by AV Yamshanov"

    def calc_shs(self, pattern_id):
        pdata = self._data.patterns[pattern_id]
        
        upper = sum(self.__row_distance2(x1, x2) for x1, x2 in combinations(pdata, 2)) +\
                sum(self.__row_distance1(x) for x in pdata)
        bottom = sum(self.__row_variants(x1) * self.__row_variants(x2) for x1, x2 in combinations(pdata, 2)) +\
                 sum(calc_comb(self.__row_variants(x), 2) for x in pdata)
        return (upper, bottom)

    def calc_shx(self, pattern_id, obj):
        pdata = self._data.patterns[pattern_id]
        upper = sum(self.__row_distance2(obj, x) for x in pdata)
        bottom = sum(self.__row_variants(obj) * self.__row_variants(x) for x in pdata)
        return (upper, bottom)
    
    def __prod(self, iterable):
        res = 1
        for x in iterable:
            res *= x
        return res

    def __row_distance1(self, v):
        result = 0

        for i in range(self._data.features_count):
            result += calc_comb(self.__row_variants(v) / self.__feature_variants(v[i], i), 2) \
                      * self.__feature_distance2(v[i], v[i], i)
            result += self.__row_variants(v) * self.__feature_distance1(v[i], i) \
                      / self.__feature_variants(v[i], i)

        result = result / self._data.features_count
        return result

    def __row_distance2(self, v1, v2):
        result = 0
        
        for i in range(self._data.features_count):
            result += self.__feature_distance2(v1[i], v2[i], i) \
                      / self.__feature_variants(v1[i], i) \
                      / self.__feature_variants(v2[i], i)

        result = result * self.__row_variants(v1) * self.__row_variants(v2) / self._data.features_count
        return result

    def __feature_distance1(self, value, index):
        feature_min, feature_max = self.__feature_range(value, index)
        feature_len = self._data.features_len[index]

        result = 0
        for i in range(feature_min, feature_max):
            for j in range(i+1, feature_max+1):
                result += self._func(i, j, feature_len)

        return result
    
    def __feature_distance2(self, value1, value2, index):
        feature1_min, feature1_max = self.__feature_range(value1, index)
        feature2_min, feature2_max = self.__feature_range(value2, index)
        feature_len = self._data.features_len[index]
        
        result = 0
        for i in range(feature1_min, feature1_max+1):
            for j in range(feature2_min, feature2_max+1):
                result += self._func(i, j, feature_len)

        return result

    def __feature_range(self, value, index):
        return (self._data.features_min[index] if value is None else value,
                self._data.features_max[index] if value is None else value)

    def __feature_variants(self, value, index):
        feature_min, feature_max = self.__feature_range(value, index)
        return feature_max - feature_min + 1
    
    def __row_variants(self, v):
        return self.__prod(self._data.features_len[i] if v[i] == None else 1 for i in range(self._data.features_count))

