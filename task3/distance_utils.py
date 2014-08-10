#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'
from math import sqrt

def euclidean_distance(point1, point2):
    return sqrt(sum([(i-j)**2 for (i,j) in zip(point1,point2)]))