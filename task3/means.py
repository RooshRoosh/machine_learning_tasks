#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

from distance_utils import euclidean_distance

import pprint

class Model():

    def __init__(self, k):
        self.point_list = []
        self.class_list = []
        self.k = k

    def add_point(self, point, _class):
        self.point_list.append(point)
        self.class_list.append(_class)

    def eval(self):
        pass

    def get_result(self, point):
        distance_list = []
        index = 0

        while index < len(self.point_list):
            distance = euclidean_distance(self.point_list[index], point)
            distance_list.append({
                'class': self.class_list[index],
                'distance': distance
            })
            index+=1

        distance_list.sort(key = lambda x: x['distance'])
        fav = distance_list[:self.k]
        fav_class = {}
        for item in fav:
            fav_class.setdefault(item['class'], 0)
            fav_class[item['class']]+=1

        fav_class_items = fav_class.items()

        fav_class_items.sort(key = lambda x:x[1])
        return fav_class_items#[-1][0]

