#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import commonlib
import sys

parser = argparse.ArgumentParser()
parser.add_argument('input', help='input file for statistic calculation')
parser.add_argument('--format', help='output format', choices=['plain', 'json'], default='plain')
args = parser.parse_args()

data = commonlib.DataFile()
data.load(args.input)

result = []
result.append(('lset_count', data.lset_count))
result.append(('features_count', data.features_count))
result.append(('pfeatures_count', data.pfeatures_count))
result.append(('patterns', len(data.patterns)))
result.append(('features_min', data.features_min))
result.append(('features_max', data.features_max))

#

skips = [0 for x in range(data.features_count)]
for obj in data.features:
    for i in range(data.features_count):
        if obj[i] is None:
            skips[i] += 1

skips_rates = [x / data.lset_count for x in skips]
result.append(('skips_rates', skips_rates))
result.append(('skips_average_rate', sum(skips_rates) / data.features_count))

#
            
def calc_variations(obj):
    multiplier = 1
    for i in range(data.features_count):
        if obj[i] is None:
            multiplier *= data.features_max[i] - data.features_min[i] + 1
    return multiplier

substitution_strings_count = 0
for obj in data.features:
    substitution_strings_count += calc_variations(obj) - 1
result.append(('substitution_strings_count', substitution_strings_count))

#

umi_calculations_reduced = 0
umi_calculations_full = 0

patterns_keys = [x for x in data.patterns.keys()]
for i in range(len(patterns_keys) - 1):
    for j in range(i + 1, len(patterns_keys)):
        p1_reduced = 0
        p1_full = 0
        for x in data.patterns[patterns_keys[i]]:
            p1_reduced += 1
            p1_full += calc_variations(x)

        p2_reduced = 0
        p2_full = 0
        for x in data.patterns[patterns_keys[i]]:
            p2_reduced += 1
            p2_full += calc_variations(x)

        umi_calculations_reduced += p1_reduced * p2_reduced
        umi_calculations_full += p1_full * p2_full

result.append(('umi_calculations_reduced', umi_calculations_reduced))
result.append(('umi_calculations_full', umi_calculations_full))
result.append(('umi_calculations_economy', (umi_calculations_full - umi_calculations_reduced) / umi_calculations_full))

#

s_calculations_reduced = 0
s_calculations_full = 0
sx_calculations_reduced = 0
sx_calculations_full = 0
for i in range(len(patterns_keys)):
    p_reduced = 0
    p_full = 0
    for x in data.patterns[patterns_keys[i]]:
        p_reduced += 1
        p_full += calc_variations(x)

    s_calculations_reduced += commonlib.calc_comb(p_reduced, 2)
    s_calculations_full += commonlib.calc_comb(p_full, 2)
    sx_calculations_reduced += p_reduced
    sx_calculations_full += p_full

result.append(('s_calculations_reduced', s_calculations_reduced))
result.append(('s_calculations_full', s_calculations_full))
result.append(('s_calculations_economy', (s_calculations_full - s_calculations_reduced) / s_calculations_full))
result.append(('sx_calculations_reduced', sx_calculations_reduced))
result.append(('sx_calculations_full', sx_calculations_full))
result.append(('sx_calculations_economy', (sx_calculations_full - sx_calculations_reduced) / sx_calculations_full))

#

if args.format == 'plain':
    for k, v in result:
        if isinstance(v, tuple) or isinstance(v, list):
            print("{0}:".format(k))
            commonlib.print_tables([[v]])
        else:
            print("{0}: {1}".format(k, v))
elif args.format == 'json':
    print(json.dumps({x[0]: x[1] for x in result}))

