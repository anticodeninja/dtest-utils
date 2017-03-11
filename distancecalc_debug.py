#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from functools import *
from itertools import *

import utils
from datafile import DataFile
from distancecalclib import *

# Constants

DELTA = 0.1 ** 6
COLUMNS = 120

# Functions

def distance_feature(v1, v2, m):
    return 1 - abs(v1 - v2) / (m - 1)

# Reading Input
parser = argparse.ArgumentParser()
parser.add_argument('input', help='input file')
parser.add_argument('-s', '--subset', dest='test', nargs='+',
                    type=int, help='use only following subset of features')
args = parser.parse_args()

data = DataFile(args.input)
    
if args.test:
    tests = args.test
elif data.tests:
    tests = data.tests
else:
    tests = [[1] * data.features_count]

# Input Info
print(utils.make_header('Patterns', COLUMNS))
patterns_keys = sorted(data.patterns.keys())
for pattern in patterns_keys:
    print(utils.make_header('Pattern "{0}"'.format(' '.join(data.format_pfeature(x) for x in pattern)),
                            COLUMNS, filler='-'))
    utils.print_tables([data.patterns[pattern]], converters=[data.format_feature])

print(utils.make_header('Objects to Recognize', COLUMNS))
for obj in data.objects:
    utils.print_tables([[obj]], converters=[data.format_feature])

# Output Info
for test in tests:
    print()
    print(utils.make_header('Test "{0}"'.format(' '.join('1' if x else '0' for x in test)), COLUMNS, border=True))
    print()

    work_data = data.get_reduced(test)
    algorithmes = [
        IterativeIntegerAlgorithm(work_data, distance_feature),
        ReducedBinaryAlgorithm(work_data, distance_feature),
        BasicIntegerAlgorithm(work_data, distance_feature),
        ReducedIntegerAlgorithm(work_data, distance_feature)
    ]
    
    print(utils.make_header('Simularity in Pattern', COLUMNS))
    
    table_headers = ['P'] + [algo.id() for algo in algorithmes]
    table_convertes = [str] + [lambda x: "{0:.2f}".format(x) for algo in algorithmes]
    table_data = [[]] + [[] for algo in algorithmes]

    shs = {}
    
    for pattern in patterns_keys:
        table_data[0].append([' '.join(work_data.format_pfeature(x) for x in pattern)])
        reference = None
        for column_id, algo in enumerate(algorithmes, 1):
            result_tuple = algo.calc_shs(pattern)
            result_calc = result_tuple[0] / result_tuple[1] if result_tuple[1] > 0 else 0
            if not reference:
                reference = result_calc
            result_ref = 1 if abs(reference - result_calc) < DELTA else 0
            table_data[column_id].append([result_tuple[0], result_tuple[1], result_calc, result_ref])
            shs.setdefault(algo, {}).setdefault(pattern, result_calc)
    utils.print_tables(table_data, headers=table_headers, converters=table_convertes, header_filler='~')

    print(utils.make_header('Simularity Objects to Pattern', COLUMNS))
    
    for obj in work_data.objects:
        print(utils.make_header('Object "{0}"'
                                .format(' '.join(data.format_feature(x) for x in obj)),
                                COLUMNS, filler='-'))
        
        table_data = [[]] + [[] for algo in algorithmes]
        
        for pattern in patterns_keys:
            table_data[0].append([' '.join(work_data.format_pfeature(x) for x in pattern)])
            reference = None
            for column_id, algo in enumerate(algorithmes, 1):
                result_tuple = algo.calc_shx(pattern, obj)
                result_calc = result_tuple[0] / result_tuple[1] if result_tuple[1] > 0 else 0
                proximity = result_calc / shs[algo][pattern]
                if not reference:
                    reference = result_calc
                    table_data[column_id].append([result_tuple[0], result_tuple[1], result_calc, proximity])
                else:
                    result_ref = 1 if abs(reference - result_calc) < DELTA else 0
                    table_data[column_id].append([result_tuple[0], result_tuple[1], result_calc, proximity, result_ref])
                
        utils.print_tables(table_data, headers=table_headers, converters=table_convertes, header_filler='~')
