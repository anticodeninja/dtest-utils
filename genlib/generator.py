#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

class Feature():
    kinds = ['constant', 'stable', 'common', 'random', 'alternative', 'dependent']
    
    def __init__(self, feature_type, minimal=0, maximal=1, absence_probability=0):
        self.feature_type = feature_type
        self.minimal = minimal
        self.maximal = maximal
        self.absence_probability = absence_probability

        if feature_type == 'constant':
            self.constant = random.randint(self.minimal, self.maximal)

    def generate(self, pattern):
        return FeatureGenerator(self, pattern)

class FeatureGenerator():
    def __init__(self, feature, pattern):
        self.__feature = feature
        self.feature_id = len(pattern.generators)
        
        if feature.feature_type == 'constant':
            self.minimal = feature.constant
            self.maximal = self.minimal
        elif feature.feature_type == 'stable':
            self.minimal = random.randint(feature.minimal, feature.maximal)
            self.maximal = self.minimal
        elif feature.feature_type == 'common':
            self.minimal = random.randint(feature.minimal, feature.maximal)
            self.maximal = random.randint(self.minimal, feature.maximal)
        elif feature.feature_type == 'random':
            self.minimal = feature.minimal
            self.maximal = feature.maximal
        elif feature.feature_type == 'alternative' or feature.feature_type == 'dependent':
            self.target = random.randint(0, len(pattern.generators) - 1)

            generator = pattern.generators[self.target]

            delta2_maximal = (feature.maximal - feature.minimal) - (generator.maximal - generator.minimal)
            if delta2_maximal < 0:
                delta2_maximal = 0
            
            delta_minimal = feature.minimal - generator.minimal
            delta_maximal = delta_minimal + delta2_maximal
            
            delta = random.randint(delta_minimal, delta_maximal)
            delta2 = 0
            
            values = []
            for i in range(generator.maximal - generator.minimal + 1):
                values.append(generator.minimal + delta + delta2)
                if delta2 < delta2_maximal and (feature.feature_type == 'alternative' or random.random() > 0.5):
                    delta2 += 1
                
            self.minimal = values[0]
            self.maximal = values[-1]
            
            if random.random() > 0.5:
                values.reverse()

            self.conv = {}
            for i in range(generator.maximal - generator.minimal + 1):
                self.conv[generator.minimal + i] = values[i]
        else:
            raise Exception('Unknown feature type: {0}'.format(feature.feature_type))

    def generate(self, result):
        if self.__feature.feature_type == 'constant':
            result[self.feature_id] = self.minimal
        elif self.__feature.feature_type == 'stable':
            result[self.feature_id] = self.minimal
        elif self.__feature.feature_type == 'common':
            result[self.feature_id] = random.randint(self.minimal, self.maximal)
        elif self.__feature.feature_type == 'random':
            result[self.feature_id] = random.randint(self.minimal, self.maximal)
        elif self.__feature.feature_type == 'alternative':
            result[self.feature_id] = self.conv[result[self.target]]
        elif self.__feature.feature_type == 'dependent':
            result[self.feature_id] = self.conv[result[self.target]]
        else:
            raise Exception('Unknown feature type: {0}'.format(self.__feature.feature_type))

    def finalize(self, result):
        if random.random() < self.__feature.absence_probability:
            result[self.feature_id] = '-'
        

class Pattern():
    def __init__(self, pattern, probability=1):
        self.pattern = pattern
        self.probability = probability

    def initialize(self, features):
        self.generators = []
        for x in features:
            self.generators.append(x.generate(self))

    def generate(self):
        result = [0] * len(self.generators)
        for x in self.generators:
            x.generate(result)
        for x in self.generators:
            x.finalize(result)
        return result

class Generator():
    def __init__(self):
        self.features = []
        self.patterns = []
        self.features_map = None
        self.patterns_length = None
        self.patterns_map = None
    
    def add_feature(self, feature):
        if len(self.patterns) > 0:
            raise Exception('Cannot append new feature when any pattern was append')
        self.features.append(feature)

    def get_feature_count(self):
        return len(self.features)

    def set_patterns_length(self, length):
        self.patterns_length = length

    def get_patterns_length(self):
        return self.patterns_length

    def add_pattern(self, pattern):
        if len(pattern.pattern) != self.patterns_length:
            raise Exception('Incorrect pattern count')
        self.patterns.append(pattern)

    def initialize(self, randomize_features=False):
        self.features_map = [x for x in range(0, len(self.features))]
        if randomize_features:
            random.shuffle(self.features_map)
            
        for pattern in self.patterns:
            pattern.initialize(self.features)

        total_probability = sum(x.probability for x in self.patterns)
        index = 0

        self.patterns_map = []
        for pattern in self.patterns:
            for i in range(int(1000 * pattern.probability / total_probability)):
                self.patterns_map.append(pattern)

    def generate(self, count):
        for i in range(count):
            pattern = random.choice(self.patterns_map)

            features = pattern.generate()
            features = [features[self.features_map[x]] for x in range(len(features))]

            yield (features, pattern.pattern)

