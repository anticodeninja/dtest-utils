#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import utils

parser = argparse.ArgumentParser()
parser.add_argument('input', help='input file')
parser.add_argument('output', help='output file')
parser.add_argument('-p', '--patterns', type=int, help='reduce amount of patterns')
parser.add_argument('-o', '--objects', type=int, help='reduce amount of objects')
args = parser.parse_args()

features, pfeatures = utils.read_objects(args.input)
features, pfeatures = utils.reduce_objects(features, pfeatures, args.patterns, args.objects)
utils.write_objects(args.output, features, pfeatures)
