#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Generator:

    def __init__(self, features_count):
        self.__features_count = features_count

    def __iter__(self):
        temp = [0] * self.__features_count

        while True:
            index = self.__features_count - 1
            while index > 0 and not (temp[index] == 1 and temp[index-1] == 0):
                index -= 1

            if index != 0:
                temp[index-1] = 1
                start = index
                next_step = self.__features_count - sum(temp[index+1:])
            else:
                start = 0
                next_step = self.__features_count - sum(temp) - 1
                if next_step == -1:
                    return

            for i in range(index, self.__features_count):
                temp[i] = 0 if i < next_step else 1
                
            yield temp
