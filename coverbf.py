#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import os

import commonlib
import coverlib

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

if not input_file.uim:
    print("Input file does not contain uim block", file=sys.stderr)
    sys.exit(1)

tasks_performed = 0
results = coverlib.ResultSet(args.results_limit)
generator = coverlib.Generator(input_file.features_count)
for current in generator:
    coverAll = True

    for row in input_file.uim:
        cover = 0
        for i in range(input_file.features_count):
            if current[i] and row[i] != 0:
                cover += 1
                if cover == args.covering:
                    break

        if cover < args.covering:
            coverAll = False
            break

    tasks_performed += 1

    if coverAll:
        if results.append(coverlib.Result([x for x in current])) != None:
            print('Found coverage ', ' '.join(str(x) for x in current), file=sys.stderr)
            if results.is_full():
                break

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
