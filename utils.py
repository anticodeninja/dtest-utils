#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import math

class PatternGroup:
    def __init__(self, pfeature):
        self.pfeature = pfeature
        self.features = []

def file_wrapper(file_obj):
    for line in file_obj:
        for word in line.split():
            yield word

def calc_key(pobj):
    return " ".join(pobj)

def calc_variations(obj, minimal, maximal):
    multiplier = 1
    for i in range(len(obj)):
        if obj[i] == '-':
            multiplier *= maximal[i] - minimal[i] + 1
    return multiplier

def read_objects(filename):
    with open(filename, 'r') as input_file:
        input_wrapper = file_wrapper(input_file)

        objects_count = int(next(input_wrapper))

        features_count = int(next(input_wrapper))
        features = []
        for i in range(objects_count):
            features.append([next(input_wrapper) for j in range(features_count)])
        
        pfeatures_count = int(next(input_wrapper))
        pfeatures = []
        for i in range(objects_count):
            pfeatures.append([next(input_wrapper) for j in range(pfeatures_count)])

    for obj in features:
        for i in range(features_count):
            if obj[i] != '-':
                obj[i] = int(obj[i])
                
    return features, pfeatures

def write_objects(filename, features, pfeatures):
    with open(filename, 'w') as output_file:
        output_file.write('{0}\n'.format(len(features)))

        output_file.write('\n{0}\n'.format(len(features[0])))
        for feature in features:
            output_file.write('{0}\n'.format(' '.join(str(x) for x in feature)))

        output_file.write('\n{0}\n'.format(len(pfeatures[0])))
        for pfeature in pfeatures:
            output_file.write('{0}\n'.format(' '.join(str(x) for x in pfeature)))

def group_pattern(features, pfeatures):
    result = {}

    for i in range(len(features)):
        key = calc_key(pfeatures[i])
        if key in result:
            pattern = result[key]
        else:
            pattern = PatternGroup(pfeatures[i])
            result[key] = pattern
        pattern.features.append(features[i])

    return result

def reduce_objects(features, pfeatures, patterns_take, objects_take):
    patterns = group_pattern(features, pfeatures)
    keys = [(key, len(value.features)) for key, value in patterns.items()]
    keys.sort(key=lambda x: x[1], reverse=True)

    if patterns_take:
        keys = keys[:patterns_take]

    objects_count = sum(x[1] for x in keys)
    if not objects_take:
        objects_take = objects_count

    patterns_count = [0] * len(keys)
    for i in range(len(keys)):
        patterns_count[i] = objects_take * keys[i][1] // len(features)
    for i in reversed(range(len(keys))):
        patterns_count[i] = min(keys[i][1], patterns_count[i] + objects_take - sum(patterns_count))

    if sum(patterns_count) < objects_take:
        raise Exception('objects is not enough')

    result = []
    for i in range(len(keys)):
        pattern = patterns[keys[i][0]]
        random.shuffle(pattern.features)
        for j in range(patterns_count[i]):
            result.append([pattern.features[j], pattern.pfeature])
    random.shuffle(result)

    return [x[0] for x in result], [x[1] for x in result]

def calc_comb(n, k):
    if k > n:
        return 0

    return math.factorial(n) // math.factorial(k) // math.factorial(n - k)
