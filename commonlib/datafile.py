#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commonlib
import sys

class DataFile:

    def __init__(self):
        self.__reset_collections()
        self.__reset_calculated()

    def load(self, filename):
        self.__reset_collections();
        
        input_file = open(filename, 'r') if filename != '-' else sys.stdin
        
        try:
            input_stream = commonlib.InputFileStream(input_file)

            while True:
                header = input_stream.read()

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
                elif header == 'uim_weights:':
                    self.__read_uim_weights_block(input_stream)
                elif header == 'tests:':
                    self.__read_tests_block(input_stream)
                else:
                    raise Exception('Cannot parse {0}, current chunk: {1}'.format(filename, header))

        finally:
            if input_file != sys.stdin:
                input_file.close()
                
        self.bake(True)
        return self

    def save(self, filename):
        self.bake(False)

        output_file = open(filename, 'w') if filename != '-' else sys.stdout
            
        try:
            output_stream = commonlib.OutputFileStream(output_file)
            
            if self.features:
                self.__write_lset_block(output_stream)
            if (self.features_min or self.features_max) and not self.features_ranges_calced:
                self.__write_ranges_block(output_stream)
            if self.rfeatures:
                self.__write_rset_block(output_stream)
            if self.uim:
                self.__write_uim_block(output_stream)
            if self.uim_weights:
                self.__write_uim_weights_block(output_stream)
            if len(self.tests) > 0:
                self.__write_tests_block(output_stream)

        finally:
            if output_file != sys.stdout:
                output_file.close()

    def transfer(self, orig):
        if self.features is None and orig.features is not None:
            self.features = orig.features
            self.pfeatures = orig.pfeatures

        if self.features_min is None and orig.features_min is not None:
            self.features_min = orig.features_min
            self.features_max = orig.features_max
            self.features_ranges_calced = orig.features_ranges_calced

        if self.uim is None and orig.uim is not None:
            self.uim = orig.uim

        if self.uim_weights is None and orig.uim_weights is not None:
            self.uim_weights = orig.uim_weights

        for test_koef, tests in orig.tests.items():
            if test_koef not in self.tests:
                self.tests[test_koef] = tests

        if self.rfeatures is None and orig.rfeatures is not None:
            self.rfeatures = orig.rfeatures

    def get_reduced(self, test):
        if all(test):
            return self

        new_features_count = sum(1 if x else 0 for x in test)
        def reduce_obj(obj):
            return tuple(x for x, m in zip(obj, test) if m)
        
        clone = DataFile()
        clone.features = [reduce_obj(x) for x in self.features]
        clone.pfeatures = [x for x in self.pfeatures]
        clone.rfeatures = [reduce_obj(x) for x in self.rfeatures]
        clone.tests = [[True] * new_features_count]
        clone.features_min = reduce_obj(self.features_min)
        clone.features_max = reduce_obj(self.features_max)
        clone.features_ranges_calced = self.features_ranges_calced
        clone.bake(True)
        
        return clone

    def bake(self, full=True):
        if full:
            self.__reset_calculated()

        if (self.features is None) != (self.pfeatures is None):
            raise Exception('data cannot contains only features or rfeatures subset')

        if self.features:
            if self.features_count is None:
                self.features_count = len(self.features[0])
            if self.pfeatures_count is None:
                self.pfeatures_count = len(self.pfeatures[0])
            if self.lset_count is None:
                self.lset_count = len(self.features)

            if len(self.features) != self.lset_count or\
               len(self.pfeatures) != self.lset_count:
                raise Exception('Invalid data, lset_count is not consist in different blocks')

            for x in self.features:
                if len(x) != self.features_count:
                    raise Exception('Invalid data, features_count is not consist in different blocks')
                
            for x in self.pfeatures:
                if len(x) != self.pfeatures_count:
                    raise Exception('Invalid data, pfeatures_count is not consist in different blocks')


        if (self.uim_weights is not None) and (self.uim is None):
            raise Exception('data cannot contains uim_weights without uim')

        if self.uim is not None:
            if self.features_count is None:
                self.features_count = len(self.uim[0])
            if self.uim_count is None:
                self.uim_count = len(self.uim)

            for x in self.uim:
                if len(x) != self.features_count:
                    raise Exception('Invalid data, features_count is not consist in different blocks')

            if self.uim_weights is not None and len(self.uim_weights) != self.features_count:
                raise Exception('Invalid data, features_count is not consist in different blocks')

        if self.features_min and self.features_max:
            if len(self.features_min) != self.features_count or\
               len(self.features_max) != self.features_count:
                raise Exception('Invalid data, features_count is not consist in different blocks')

        self.tests = {k: v for k, v in self.tests.items() if len(v) > 0}
        if len(self.tests) > 0:
            if self.features_count is None:
                self.features_count = len(next(iter(self.tests.values()))[0])

            for h, cur_tests in self.tests.items():
                for x in cur_tests:
                    if len(x) != self.features_count:
                        raise Exception('Invalid data, features_count is not consist in different blocks')

        if self.rfeatures is not None:
            if self.features_count is None:
                self.features_count = len(self.rfeatures[0])
            if self.rset_count is None:
                self.rset_count = len(self.rfeatures)

            if self.rset_count != len(self.rfeatures):
                raise Exception('Invalid data, rset_count is not consist in different blocks')
            
            for x in self.rfeatures:
                if len(x) != self.features_count:
                    raise Exception('Invalid data, features_count is not consist in different blocks')

        if full:
            if self.features:
                self.patterns = dict()
                for feature_item, pfeature_item in zip(self.features, self.pfeatures):
                    self.patterns.setdefault(tuple(pfeature_item), []).append(feature_item)

                if not self.features_min:
                    self.features_ranges_calced = True
                    self.features_min = [x for x in self.features[0]]
                    for obj in self.features:
                        for i in range(self.features_count):
                            if self.features_min[i] > obj[i]:
                                self.features_min[i] = obj[i]

                if not self.features_max:
                    self.features_ranges_calced = True
                    self.features_max = [x for x in self.features[0]]
                    for obj in self.features:
                        for i in range(self.features_count):
                            if self.features_max[i] < obj[i]:
                                self.features_max[i] = obj[i]

            if self.features_min and self.features_max:
                self.features_len = tuple(b - a + 1 for a, b in zip(self.features_min, self.features_max))
        

    def __read_lset_block(self, input_stream):
        lset_count = int(input_stream.read())
        features_count = int(input_stream.read())
        pfeatures_count = int(input_stream.read())

        self.features = []
        self.pfeatures = []
        for i in range(lset_count):
            self.features.append(tuple(self.__parse_feature(input_stream.read()) for j in range(features_count)))
            self.pfeatures.append(tuple(self.__parse_pfeature(input_stream.read()) for j in range(pfeatures_count)))

    def __write_lset_block(self, output_stream):
        output_stream.write('learning_set:', self.lset_count, self.features_count, self.pfeatures_count, '\n')
        
        for lx, px in zip(self.features, self.pfeatures):
            output_stream.write(*lx)
            output_stream.write('')
            output_stream.write(*px)
            output_stream.write('\n')

        output_stream.write('\n')

    def __read_ranges_block(self, input_stream):
        features_count = int(input_stream.read())
        
        self.features_min = tuple(int(input_stream.read()) for j in range(features_count))
        self.features_max = tuple(int(input_stream.read()) for j in range(features_count))

    def __write_ranges_block(self, output_stream):
        output_stream.write('ranges:', self.features_count, '\n')

        output_stream.write(*self.features_min)
        output_stream.write('\n')
        output_stream.write(*self.features_max)
        output_stream.write('\n', '\n')

    def __read_uim_block(self, input_stream):
        uim_count = int(input_stream.read())
        features_count = int(input_stream.read())

        self.uim = []
        for i in range(uim_count):
            self.uim.append(tuple(self.__parse_feature(input_stream.read()) for j in range(features_count)))

    def __write_uim_block(self, output_stream):
        output_stream.write('uim:', self.uim_count, self.features_count, '\n')
        
        for row in self.uim:
            output_stream.write(*row)
            output_stream.write('\n')
        output_stream.write('\n')

    def __read_uim_weights_block(self, input_stream):
        features_count = int(input_stream.read())

        self.uim_weights = tuple(self.__parse_feature(input_stream.read()) for j in range(features_count))

    def __write_uim_weights_block(self, output_stream):
        output_stream.write('uim_weights:', self.features_count, '\n')
        output_stream.write(*self.uim_weights)
        output_stream.write('\n', '\n')

    def __read_tests_block(self, input_stream):
        tests_h_koef = int(input_stream.read())
        tests_count = int(input_stream.read())
        features_count = int(input_stream.read())

        cur_test = []
        for i in range(tests_count):
            cur_test.append(tuple(input_stream.read() != '0' for j in range(features_count)))
        self.tests[tests_h_koef] = cur_test

    def __write_tests_block(self, output_stream):
        for h in sorted(self.tests.keys()):
            cur_tests = self.tests[h]
            output_stream.write('tests:', h, len(cur_tests), self.features_count, '\n')

            for row in cur_tests:
                output_stream.write(*[1 if x else 0 for x in row])
                output_stream.write('\n')
            output_stream.write('\n')

    def __read_rset_block(self, input_stream):
        rset_count = int(input_stream.read())
        features_count = int(input_stream.read())

        for i in range(rset_count):
            self.rfeatures.append(tuple(self.__parse_feature(input_stream.read()) for j in range(features_count)))

    def __reset_collections(self):
        self.features = None
        self.pfeatures = None
        self.rfeatures = None
        self.uim = None
        self.uim_weights = None
        self.tests = {}
        self.features_min = None
        self.features_max = None
        self.features_ranges_calced = False

    def __reset_calculated(self):
        self.features_count = None
        self.pfeatures_count = None
        self.patterns = None
        self.lset_count = None
        self.rset_count = None
        self.uim_count = None
        self.tests_count = None
        self.features_len = None

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
