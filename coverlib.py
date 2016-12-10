#!/usr/bin/env python
# -*- coding: utf-8 -*-

def calc_cost(mask):
    return sum(mask)

class Result:
    def __init__(self, mask):
        self.mask = mask
        self.cost = calc_cost(mask)

    def __repr__(self):
        return "{0}|{1}".format(
            " ".join("{0:2}".format(x) for x in self.mask),
            "{0:2}".format(self.cost))

    def is_include(self, other):
        if self.cost > other.cost:
            return False
        
        for i in range(len(self.mask)):
            if self.mask[i] > other.mask[i]:
                return False

        return True

class ResultSet:
    def __init__(self, limit):
        self.results = []
        self.limit = limit

    def __iter__(self):
        for result in self.results:
            yield result

    def __len__(self):
        return len(self.results)

    def __getitem__(self, index):
        return self.results[index]

    def append(self, result):
        for i in range(len(self.results)):
            if self.results[i].is_include(result):
                return

        index = len(self.results)
        for i in range(len(self.results)):
            if result.cost < self.results[i].cost:
                index = i
                break

        if index is not None and index < self.limit:
            self.results.insert(index, result)

            if len(self.results) > self.limit:
                self.results = self.results[:self.limit]
        else:
            index = None    

        return index

    def is_fulfilled(self):
        return len(self.results) == self.limit

