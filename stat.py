#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import utils
import sys

parser = argparse.ArgumentParser()
parser.add_argument('input', help='input file for statistic calculation')
args = parser.parse_args()

features, pfeatures = utils.read_objects(args.input)

objects_count = len(features)
features_count = len(features[0])
pfeatures_count = len(pfeatures[0])
    
minimal = [sys.maxsize for x in range(features_count)]
maximal = [0 for x in range(features_count)]
skips = [0 for x in range(features_count)]
substitution_strings_count = 0

#

for obj in features:
    for i in range(features_count):
        if obj[i] != '-' and minimal[i] > obj[i]:
            minimal[i] = obj[i]
        if obj[i] != '-' and maximal[i] < obj[i]:
            maximal[i] = obj[i]
        if obj[i] == '-':
            skips[i] += 1

skips_rates = [x / objects_count for x in skips]
skips_average_rate = sum(skips_rates) / features_count

#
            
def calc_variations(obj):
    multiplier = 1
    for i in range(features_count):
        if obj[i] == '-':
            multiplier *= maximal[i] - minimal[i] + 1
    return multiplier

for obj in features:
    substitution_strings_count += calc_variations(obj) - 1

#
    
patterns = utils.group_pattern(features, pfeatures)
patterns_keys = [x for x in patterns.keys()]
patterns_count = len(patterns_keys)

#

umi_calculations_reduced = 0
umi_calculations_full = 0

for i in range(patterns_count - 1):
    for j in range(i + 1, patterns_count):
        p1_reduced = 0
        p1_full = 0
        for x in patterns[patterns_keys[i]].features:
            p1_reduced += 1
            p1_full += calc_variations(x)

        p2_reduced = 0
        p2_full = 0
        for x in patterns[patterns_keys[i]].features:
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

for i in range(patterns_count):
    p_reduced = 0
    p_full = 0
    for x in patterns[patterns_keys[i]].features:
        p_reduced += 1
        p_full += calc_variations(x)

    s_calculations_reduced += utils.calc_comb(p_reduced, 2)
    s_calculations_full += utils.calc_comb(p_full, 2)
    sx_calculations_reduced += p_reduced
    sx_calculations_full += p_full

s_calculations_economy = (s_calculations_full - s_calculations_reduced) / s_calculations_full
sx_calculations_economy = (sx_calculations_full - sx_calculations_reduced) / sx_calculations_full

#

print("objects: {0}".format(objects_count))
print("features: {0}".format(features_count))
print("pfeatures: {0}".format(pfeatures_count))
print("patterns: {0}".format(patterns_count))
print("minimal:     [{0}]".format(" ".join("{0:3}".format(x) for x in minimal)))
print("maximal:     [{0}]".format(" ".join("{0:3}".format(x) for x in maximal)))
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
