#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import utils
import sys

from datafile import DataFile

parser = argparse.ArgumentParser()
parser.add_argument('input', help='input file for statistic calculation')
args = parser.parse_args()

data = DataFile(args.input)

#

skips = [0 for x in range(data.features_count)]
for obj in data.features:
    for i in range(data.features_count):
        if obj[i] is None:
            skips[i] += 1

skips_rates = [x / data.lset_len for x in skips]
skips_average_rate = sum(skips_rates) / data.features_count

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

umi_calculations_economy = (umi_calculations_full - umi_calculations_reduced) / umi_calculations_full

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

    s_calculations_reduced += utils.calc_comb(p_reduced, 2)
    s_calculations_full += utils.calc_comb(p_full, 2)
    sx_calculations_reduced += p_reduced
    sx_calculations_full += p_full

s_calculations_economy = (s_calculations_full - s_calculations_reduced) / s_calculations_full
sx_calculations_economy = (sx_calculations_full - sx_calculations_reduced) / sx_calculations_full

#

print("objects: {0}".format(data.lset_len))
print("features: {0}".format(data.features_count))
print("pfeatures: {0}".format(data.pfeatures_count))
print("patterns: {0}".format(len(data.patterns)))
print("minimal:     [{0}]".format(" ".join("{0:3}".format(x) for x in data.features_min)))
print("maximal:     [{0}]".format(" ".join("{0:3}".format(x) for x in data.features_max)))
print("skips rates: [{0}]".format(" ".join("{0:.2f}".format(x)[1:] for x in skips_rates)))
print("skips averate rate: {0:.3f}".format(skips_average_rate))
print("substitution strings count: {0}".format(substitution_strings_count))
print("umi calculations reduced: {0}".format(umi_calculations_reduced))
print("umi calculations full: {0}".format(umi_calculations_full))
print("umi calculations economy: {0}".format(umi_calculations_economy))
print("s calculations reduced: {0}".format(s_calculations_reduced))
print("s calculations full: {0}".format(s_calculations_full))
print("s calculations economy: {0}".format(s_calculations_economy))
print("sx calculations reduced: {0}".format(sx_calculations_reduced))
print("sx calculations full: {0}".format(sx_calculations_full))
print("sx calculations economy: {0}".format(sx_calculations_economy))
