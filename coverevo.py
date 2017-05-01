#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from deap import algorithms, base, creator, tools
import os
import random
import sys

import commonlib
import coverlib

def calc_cover(individual, covering):
    global input_file
    coverStr = 0

    for row in input_file.uim:
        cover = 0
        for i in range(len(individual)):
            if individual[i] and row[i] != 0:
                cover += 1

        if cover >= covering:
            coverStr += 1
            
    return coverStr

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

feature_count_penalty_koef = 1.0 / (input_file.features_count-args.covering+1)
covering_penalty_koef = 1.0 - feature_count_penalty_koef
def fitness(individual):
    res = 1 - (sum(individual)-1)/(input_file.features_count-1) * feature_count_penalty_koef\
            - (input_file.uim_count - calc_cover(individual, args.covering)) / input_file.uim_count * covering_penalty_koef
    return res,

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=input_file.features_count)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", fitness)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selNSGA2)

population = toolbox.population(n=256)

NGEN=32
for gen in range(NGEN):
    offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
    fits = toolbox.map(toolbox.evaluate, offspring)
    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
    population = toolbox.select(offspring, k=len(population))

results = coverlib.ResultSet(args.results_limit)
for individual in population:
    if calc_cover(individual, args.covering) == input_file.uim_count:
        results.append(coverlib.Result([x for x in individual]))
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
