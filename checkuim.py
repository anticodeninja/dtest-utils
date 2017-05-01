#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

import commonlib

parser = argparse.ArgumentParser()
parser.add_argument('input', help='file for check')
parser.add_argument('reference', help='file with reference uim')
args = parser.parse_args()

input_file = commonlib.DataFile()
input_file.load(args.input)
reference_file = commonlib.DataFile()
reference_file.load(args.reference)

if input_file.features_count != reference_file.features_count:
    print("feature_count differs")
    sys.exit(1)

if input_file.uim_count != reference_file.uim_count:
    print("uim_count differs")
    sys.exit(1)

if input_file.uim_weights:
    if input_file.uim_weights != reference_file.uim_weights:
        print("uim_weights differs")
        sys.exit(1)

input_set = set(tuple(row) for row in input_file.uim)
reference_set = set(tuple(row) for row in reference_file.uim)

if input_set != reference_set:
    print("uim_weights differs")
    sys.exit(1)

print("uims equal")
sys.exit(0)
