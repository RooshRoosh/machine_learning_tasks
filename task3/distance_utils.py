#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'
from math import sqrt
import random

def euclidean_distance(point1, point2):
    return sqrt(sum([(i-j)**2 for (i,j) in zip(point1,point2)]))


def get_probability_class(distribution):

    summury = sum(distribution)
    value = 0
    master = []

    for i in distribution:
        master.append(value)
        value+=i/float(summury)
    master.append(1)
    result = random.random()
    index = 0

    while index < len(master)-1:
        if master[index]<= result < master[index+1]:
            return distribution[index]
        index +=1