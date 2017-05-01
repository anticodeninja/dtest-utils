#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import math

class InputFileStream:

    def __init__(self, fileobj):
        self.__file = fileobj
        self.__line = []

    def read(self):
        while True:
            if self.__line is None:
                return None
        
            if len(self.__line) == 0:
                self.__line = self.__file.readline()
                self.__line = self.__line.strip().split() if len(self.__line) > 0 else None
                continue

            return self.__line.pop(0)
        

class OutputFileStream:

    def __init__(self, fileobj):
        self.__file = fileobj
        self.__empty_line = True

    def write(self, *args):
        for x in args:
            if x == '\n':
                self.__file.write('\n')
                self.__empty_line = True
                continue

            if not self.__empty_line:
                self.__file.write(' ')
            self.__empty_line = False
                
            self.__file.write(str(x))

def calc_comb(n, k):
    if k > n:
        return 0
    return math.factorial(n) // math.factorial(k) // math.factorial(n - k)

def calc_key(pobj):
    return " ".join(pobj)

def calc_variations(obj, minimal, maximal):
    multiplier = 1
    for i in range(len(obj)):
        if obj[i] == '-':
            multiplier *= maximal[i] - minimal[i] + 1
    return multiplier

def binarize(row):
    return tuple(1 if x != 0 else 0 for x in row)

def reduce_objects(features, pfeatures, patterns_take, objects_take):
    patterns = group_pattern(features, pfeatures)
    keys = [(key, len(value.features)) for key, value in patterns.items()]
    keys.sort(key=lambda x: x[1], reverse=True)

    if patterns_take:
        keys = keys[:patterns_take]

    objects_count = sum(x[1] for x in keys)
    if not objects_take:
        objects_take = objects_count

    patterns_count = [0] * len(keys)
    for i in range(len(keys)):
        patterns_count[i] = objects_take * keys[i][1] // len(features)
    for i in reversed(range(len(keys))):
        patterns_count[i] = min(keys[i][1], patterns_count[i] + objects_take - sum(patterns_count))

    if sum(patterns_count) < objects_take:
        raise Exception('objects is not enough')

    result = []
    for i in range(len(keys)):
        pattern = patterns[keys[i][0]]
        random.shuffle(pattern.features)
        for j in range(patterns_count[i]):
            result.append([pattern.features[j], pattern.pfeature])
    random.shuffle(result)

    return [x[0] for x in result], [x[1] for x in result]

def iterate_last(it):
    it = iter(it)
    prev = next(it)
    for item in it:
        yield prev, False
        prev = item
    yield prev, True

def make_header(value, width, filler='=', border=False):
    if len(value) < width:
        value = value + ' '
    if len(value) < width:
        value = ' ' + value
        
    while len(value) < width:
        if len(value) < width:
            value = value + filler
        if len(value) < width:
            value = filler + value

    if border:
        real_len = len(value)
        value = filler * real_len + '\n' + value + '\n' + filler * real_len

    return value

def print_tables(tables,
                 headers=None,
                 converters=None,
                 column_delimiter=' ',
                 table_delimiter='  ',
                 header_filler='='):
    
    cell_size = [0] * len(tables)
    cell_count = [0] * len(tables)
    tables_width = [0] * len(tables)
    rows = 0
    patterns = [None] * len(tables)

    if not converters:
        converters = [str] * len(tables)
    
    for i, table in enumerate(tables):
        converter = converters[i]
        for row in table:
            cell_size[i] = max(cell_size[i], max(len(converter(x)) for x in row))
            cell_count[i] = max(cell_count[i], len(row))
        rows = max(rows, len(table))
        patterns[i] = '{{0:{0}}}'.format(cell_size[0])
        tables_width[i] = cell_size[i] * cell_count[i] + len(column_delimiter) * (cell_count[i] - 1)

    if headers:
        chunks = []
        for i, table in enumerate(tables):
            header = make_header(headers[i], tables_width[i], header_filler)
            chunks.append(header)
            chunks.append(table_delimiter)
        chunks.pop()
        print(''.join(chunks))

    generators = [(row for row in table) for table in tables]
    for i in range(rows):
        chunks = []
        for i, generator in enumerate(generators):
            pattern = patterns[i]
            converter = converters[i] 
            for x in next(generator):
                cell = pattern.format(converter(x))
                for j in range(len(cell), cell_size[i]):
                    chunks.append(' ')
                chunks.append(cell)
                chunks.append(column_delimiter)
            chunks.pop()
            chunks.append(table_delimiter)
        chunks.pop()
        print(''.join(chunks))

