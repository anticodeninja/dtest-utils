#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import utils
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
parser.add_argument('input', help='input file')
parser.add_argument('-c', '--covering', dest='covering', type=int, help='amount of column which should be covered', default=1)
parser.add_argument('-l', '--result-limit', dest='results_limit', type=int, help='maximal amount of result', default=1)
args = parser.parse_args()

data = utils.read_uim(args.input)
height = len(data)
width = len(data[0])

utils.binarize(data)
results = []
cost_barrier = coverlib.Result([1 for x in range(width)]).cost

tasks = [Task(data, [0 for x in range(width)], [0 for x in range(height)], -1)]
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

    weights = [0] * width
    for row in task.rows:
        for i in range(width):
            weights[i] += row[i]

    columns = []
    for i in range(width):
        if mask[i] == 0:
            columns.append((i, weights[i]))
    columns.sort(key=lambda x: x[1], reverse=True)

    for column in columns:
        tasks.insert(0, Task(rows, mask, covering, column[0]))
    
for result in results:
    print(result)

print("Stats:")
print("  performed tasks: {0}".format(tasks_performed))
