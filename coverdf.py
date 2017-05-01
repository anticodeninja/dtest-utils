#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys

import commonlib
import coverlib

class Task:
    def __init__(self, rows, mask, covering, column):
        self.rows = rows
        self.mask = mask
        self.covering = covering
        self.column = column

    def __repr__(self):
        result = []
        result.append("current column: {0}".format(self.column))
        for i in range(len(self.rows)):
            result.append("{0}|{1}".format(
                " ".join("{0:2}".format(x) for x in self.rows[i]),
                "{0:2}".format(self.covering[i])))
        result.append("-" * (3 * len(self.mask)))
        result.append(" ".join("{0:2}".format(x) for x in self.mask))
        return "\n".join(result)

parser = argparse.ArgumentParser()
parser.add_argument('input',
                    help='input file')
parser.add_argument('output', nargs="?",
                    help='output file')
parser.add_argument('--no-transfer', dest='no_transfer', action="store_true",
                    help='no transfer blocks from input file to output')
parser.add_argument('-c', '--covering', dest='covering', type=int, default=1,
                    help='amount of column which should be covered')
parser.add_argument('-l', '--result-limit', dest='results_limit', type=int, default=10,
                    help='maximal amount of result')
args = parser.parse_args()

input_file = commonlib.DataFile()
input_file.load(args.input)
uim = [commonlib.binarize(x) for x in input_file.uim]

results = []
cost_barrier = coverlib.Result([1 for x in range(input_file.features_count)]).cost

tasks = [Task(uim, [0 for x in range(input_file.features_count)], [0 for x in range(input_file.uim_count)], -1)]
tasks_performed = 0
results = coverlib.ResultSet(args.results_limit)
while len(tasks) > 0:
    task = tasks.pop(0)
    result = coverlib.Result(task.mask)

    if result.cost >= cost_barrier:
        continue

    tasks_performed += 1

    if len(task.rows) == 0:
        if results.append(result) is not None:
            if results.is_full():
                cost_barrier = results[-1].cost            
        continue
    
    if task.column != -1:
        mask = [x for x in task.mask]
        mask[task.column] = 1
        
        rows = []
        covering = []
        for i in range(len(task.rows)):
            cover_koef = task.rows[i][task.column] + task.covering[i]
            if cover_koef < args.covering:
                rows.append(task.rows[i])
                covering.append(cover_koef)
            
    else:
        mask = task.mask
        rows = task.rows
        covering = task.covering

    weights = [0] * input_file.features_count
    for row in task.rows:
        for i in range(input_file.features_count):
            weights[i] += row[i]

    columns = []
    for i in range(input_file.features_count):
        if mask[i] == 0:
            columns.append((i, weights[i]))
    columns.sort(key=lambda x: x[1], reverse=True)

    for column in columns:
        tasks.insert(0, Task(rows, mask, covering, column[0]))

if args.output is None:
    args.output = args.input

output_file = commonlib.DataFile()
if args.output != '-' and os.path.exists(args.output):
    output_file.load(args.output)
if not args.no_transfer:
    output_file.transfer(input_file)
output_file.tests[args.covering] = [x.mask for x in results]
output_file.save(args.output)

print("Stats:", file=sys.stderr)
print("  performed tasks: {0}".format(tasks_performed), file=sys.stderr)
