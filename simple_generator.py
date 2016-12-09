#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import genlib
import random
import utils

parser = argparse.ArgumentParser()
parser.add_argument('output', help='output file')
parser.add_argument('objects', type=int, help='amount of objects')
parser.add_argument('patterns', type=int, help='amount of patterns')
parser.add_argument('features', type=int, help='amount of features')
parser.add_argument('-m', '--maximal', type=int, help='maximal value of feature', default=1)
parser.add_argument('-a', '--absence', type=float, help='maximal probability of absence', default=0)
args = parser.parse_args()

generator = genlib.Generator()

features_count = [0] * len(genlib.Feature.kinds)
for i in range(args.features):
    features_count[i % len(features_count)] += 1
    
for i in range(len(features_count)):
    for j in range(features_count[i]):
        generator.add_feature(genlib.Feature(
            genlib.Feature.kinds[i],
            maximal=args.maximal,
            absence_probability=random.random() * args.absence))

generator.set_patterns_length(1)
for i in range(args.patterns):
    generator.add_pattern(genlib.Pattern([i]))

generator.initialize(True)

features = []
pfeatures = []
for obj in generator.generate(args.objects):
    features.append(obj[0])
    pfeatures.append(obj[1])

utils.write_objects(args.output, features, pfeatures)

