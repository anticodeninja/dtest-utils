#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import utils
import coverlib

from datafile import DataFile

parser = argparse.ArgumentParser()
parser.add_argument('input', help='input file')
parser.add_argument('-c', '--covering', dest='covering', type=int, help='amount of column which should be covered', default=1)
parser.add_argument('-l', '--result-limit', dest='results_limit', type=int, help='maximal amount of result', default=10)
args = parser.parse_args()

data = DataFile(args.input)

def generator():
    temp = [0] * data.features_count

    while True:
        index = data.features_count - 1
        while index > 0 and not (temp[index] == 1 and temp[index-1] == 0):
            index -= 1

        if index != 0:
            temp[index-1] = 1
            start = index
            next_step = data.features_count - sum(temp[index+1:])
        else:
            start = 0
            next_step = data.features_count - sum(temp) - 1
            if next_step == -1:
                return
            
        for i in range(index, data.features_count):
            temp[i] = 0 if i < next_step else 1
        yield temp

tasks_performed = 0
results = coverlib.ResultSet(args.results_limit)
for current in generator():
    coverAll = True

    for row in data.uim:
        cover = 0
        for i in range(data.features_count):
            if current[i] and row[i] != 0:
                cover += 1
                if cover == args.covering:
                    break

        if cover < args.covering:
            coverAll = False
            break

    tasks_performed += 1

    if coverAll:
        results.append(coverlib.Result([x for x in current]))
        if results.is_full():
            break

for result in results:
    print(result)

print("Stats:")
print("  performed tasks: {0}".format(tasks_performed))
