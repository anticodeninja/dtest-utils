#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utils

class DataFile:

    def __init__(self, filename):
        self.features = None
        self.pfeatures = None
        self.objects = None
        self.uim = None
        self.tests = None

        self.features_min = None
        self.features_max = None
        self.features_len = None
        
        self.features_count = None
        self.pfeatures_count = None
        self.patterns = None
        self.lset_len = None
        self.rset_len = None
        self.uim_len = None
        self.tests_len = None

        if filename:
            self.__read_file(filename)
            self.__calc_and_check()

    def get_reduced(self, test):
        if all(test):
            return self

        new_features_count = sum(1 if x else 0 for x in test)
        def reduce_obj(obj):
            return tuple(x for x, m in zip(obj, test) if m)
        
        clone = DataFile(None)
        
        clone.features = [reduce_obj(x) for x in self.features]
        clone.pfeatures = [x for x in self.pfeatures]
        clone.objects = [reduce_obj(x) for x in self.objects]
        clone.tests = [True] * new_features_count

        clone.features_min = reduce_obj(self.features_min)
        clone.features_max = reduce_obj(self.features_max)

        clone.features_count = new_features_count
        clone.pfeatures_count = self.pfeatures_count
        clone.lset_len = self.lset_len
        clone.rset_len = self.rset_len
        clone.tests_len = 1
        
        clone.__calc_and_check()
        return clone

    def __read_file(self, filename):
        with open(filename, 'r') as input_file:
            input_stream = utils.file_to_stream(input_file)

            while True:
                header = next(input_stream, None)

                if header is None or header == 'info:':
                    break
                elif header == 'learning_set:':
                    self.__read_lset_block(input_stream)
                elif header == 'ranges:':
                    self.__read_ranges_block(input_stream)
                elif header == 'recognize_set:':
                    self.__read_rset_block(input_stream)
                elif header == 'uim:':
                    self.__read_uim_block(input_stream)
                elif header == 'uim_weight:':
                    self.__read_uim_weight_block(input_stream)
                elif header == 'tests:':
                    self.__read_tests_block(input_stream)
                else:
                    raise Exception('Cannot parse {0}, current chunk: {1}'.format(filename, header))

    def __read_lset_block(self, input_stream):
        self.__set_lset_len(int(next(input_stream)))
        self.__set_features_count(int(next(input_stream)))
        self.__set_pfeatures_count(int(next(input_stream)))
        
        self.features = []
        self.pfeatures = []
        for i in range(self.lset_len):
            self.features.append(tuple(self.__parse_feature(next(input_stream)) for j in range(self.features_count)))
            self.pfeatures.append(tuple(self.__parse_pfeature(next(input_stream)) for j in range(self.pfeatures_count)))

    def __read_ranges_block(self, input_stream):
        self.__set_features_count(int(next(input_stream)))
        
        self.features_min = tuple(int(next(input_stream)) for j in range(self.features_count))
        self.features_max = tuple(int(next(input_stream)) for j in range(self.features_count))

    def __read_uim_block(self, input_stream):
        self.__set_uim_len(int(next(input_stream)))
        self.__set_features_count(int(next(input_stream)))

        self.uim = []
        for i in range(self.uim_len):
            self.uim.append(tuple(self.__parse_feature(next(input_stream)) for j in range(self.features_count)))

    def __read_uim_weight_block(self, input_stream):
        self.__set_features_count(int(next(input_stream)))

        self.uim_weights = tuple(self.__parse_feature(next(input_stream)) for j in range(self.features_count))

    def __read_tests_block(self, input_stream):
        self.__set_tests_len(int(next(input_stream)))
        self.__set_features_count(int(next(input_stream)))

        self.tests = []
        for i in range(self.tests_len):
            self.tests.append(tuple(next(input_stream) != '0' for j in range(self.features_count)))

    def __read_rset_block(self, input_stream):
        self.__set_rset_len(int(next(input_stream)))
        self.__set_features_count(int(next(input_stream)))

        self.objects = []
        for i in range(self.rset_len):
            self.objects.append(tuple(self.__parse_feature(next(input_stream)) for j in range(self.features_count)))

    def __calc_and_check(self):
        # Calc Patterns subset
        if self.features or self.pfeatures:
            self.patterns = dict()
            for feature_item, pfeature_item in zip(self.features, self.pfeatures):
                data = self.patterns.setdefault(tuple(pfeature_item), [])
                data.append(feature_item)

        if not self.features_min and self.features:
            self.features_min = [x for x in self.features[0]]
            for obj in self.features:
                for i in range(self.features_count):
                    if self.features_min[i] > obj[i]:
                        self.features_min[i] = obj[i]

        if not self.features_max and self.features:
            self.features_max = [x for x in self.features[0]]
            for obj in self.features:
                for i in range(self.features_count):
                    if self.features_max[i] < obj[i]:
                        self.features_max[i] = obj[i]

        if self.features_min or self.features_max:
            self.features_len = tuple(b - a + 1 for a, b in zip(self.features_min, self.features_max))

    def __set_lset_len(self, lset_len):
        if self.lset_len is not None and self.lset_len != lset_len:
            raise Exception('Invalid data, lset_len is not consist in blocks')
        self.lset_len = lset_len

    def __set_rset_len(self, rset_len):
        if self.rset_len is not None and self.rset_len != rset_len:
            raise Exception('Invalid data, rset_len is not consist in blocks')
        self.rset_len = rset_len

    def __set_uim_len(self, uim_len):
        if self.uim_len is not None and self.uim_len != uim_len:
            raise Exception('Invalid data, uim_len is not consist in blocks')
        self.uim_len = uim_len

    def __set_tests_len(self, tests_len):
        if self.tests_len is not None and self.tests_len != tests_len:
            raise Exception('Invalid data, tests_len is not consist in blocks')
        self.tests_len = tests_len

    def __set_features_count(self, features_count):
        if self.features_count is not None and self.features_count != features_count:
                raise Exception('Invalid data, features_count is not consist in blocks')
        self.features_count = features_count

    def __set_pfeatures_count(self, pfeatures_count):
        if self.pfeatures_count is not None and self.pfeatures_count != pfeatures_count:
                raise Exception('Invalid data, pfeatures_count is not consist in blocks')
        self.pfeatures_count = pfeatures_count

    @staticmethod
    def __parse_feature(value):
        if value != '-':
            return int(value)
        else:
            return None

    @staticmethod
    def __parse_pfeature(value):
        if value != '-':
            return int(value)
        else:
            return None

    @staticmethod
    def format_feature(value):
        if value is None:
            return '-'
        return str(value)

    @staticmethod
    def format_pfeature(value):
        if value is None:
            return '-'
        return str(value)
