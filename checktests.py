#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

import commonlib

parser = argparse.ArgumentParser()
parser.add_argument('input', help='file for check')
parser.add_argument('reference', nargs='?', help='file with reference uim')
args = parser.parse_args()

input_file = commonlib.DataFile()
input_file.load(args.input)

if not input_file.uim:
    print("tests without uim cannot be validated")
    sys.exit(1)

for test_koef, tests in input_file.tests.items():
    if len(set(tests)) != len(tests):
        print("tests h={0} contains duplicates".format(test_koef))
        continue

    for test in tests:
        coverAll = True

        for row in input_file.uim:
            cover = 0
            for i in range(input_file.features_count):
                if test[i] and row[i]:
                    cover += 1
                    if cover == test_koef:
                        break

            if cover < test_koef:
                print("test row [{0}] (h={1}) does not cover all uim rows".format(' '.join(test), test_koef))
                sys.exit(1)


if args.reference:
    reference_file = commonlib.DataFile()
    reference_file.load(args.reference)

    for test_koef, tests in input_file.tests.items():
        reference_tests = reference_file.tests.get(test_koef, None)
        if reference_tests is None:
            print("reference file does not contain reference tests h={0}".format(test_koef))
            continue

        input_stats = {}
        for test in tests:
            test_len = sum(test)
            input_stats[test_len] = input_stats.get(test_len, 0) + 1

        reference_stats = {}
        for test in reference_tests:
            test_len = sum(test)
            reference_stats[test_len] = reference_stats.get(test_len, 0) + 1

        remaining = len(tests)
        for x in sorted(reference_stats.keys()):
            if (input_stats[x] != reference_stats[x]) if input_stats[x] != remaining else (remaining > reference_stats[x]):
                print("number of tests h={0}, features={1} differs".format(test_koef, x))
                sys.exit(1)

            remaining -= input_stats[x]


print("tests correct")
sys.exit(0)
