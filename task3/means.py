#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

from distance_utils import euclidean_distance, get_probability_class

class FullScanModel(object):
    '''
    Будем учитывать количество соседей из классов
    '''
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
        # Будем отдавать наиболее часто встречаюшегося соседа
        fav_class_items.sort(key = lambda x:x[1])
        return fav_class_items[-1][0]


class CoreModel(FullScanModel):
    '''
    Будем учитывать расстояние до центра масс класса
    '''
    def __init__(self):
        super(CoreModel, self).__init__(self)
        self.ready_model = False
        self.class_table = {}

    def eval(self):

        index = 0

        while index < len(self.point_list):
            self.class_table.setdefault(self.class_list[index], [])
            self.class_table[self.class_list[index]].append(self.point_list[index])
            index+=1

        for (key,item) in self.class_table.items():
            centre = [0 for i in self.class_table[key][0]]
            count = 0
            for point in self.class_table[key]:
                centre = [i+j for (i,j) in zip(centre,point)]
                count+=1
            centre = [i/count for i in centre]
            self.class_table[key] = centre

        self.ready_model = True

    def get_result(self, point):
        distance_list = {}
        if not self.ready_model:
            self.eval()

        for (_class, centre) in self.class_table.items():
            distance_list[_class] = euclidean_distance(centre, point)

        fav_class_items = distance_list.items()

        # Будем отдавать класс с наиболее близким центром
        fav_class_items.sort(key = lambda x:x[1])
        return fav_class_items[0][0]

        # Будем считать расстояние до центра весом - плохая идея
        # fav_distance = [i[1] for i in fav_class_items]
        # return fav_class_items[fav_distance.index(get_probability_class(fav_distance))][0]

class HybridModel(CoreModel):
    '''
    Будем учитывать не только количество ближайших соседей,
    но и близость эти соседей к центру-масс класса
    '''

    def __init__(self, k):
        super(HybridModel, self).__init__()
        self.k = k

    def get_result(self, point):

        if not self.ready_model:
            self.eval()

        distance_list = []
        index = 0

        while index < len(self.point_list):
            w_distance = euclidean_distance(self.point_list[index], point)+\
                       euclidean_distance(self.point_list[index], self.class_table[self.class_list[index]])
            distance_list.append({
                'class': self.class_list[index],
                'distance': w_distance
            })
            index+=1

        distance_list.sort(key = lambda x: x['distance'])
        fav = distance_list[:self.k]
        fav_class = {}
        for item in fav:
            fav_class.setdefault(item['class'], 0)
            fav_class[item['class']]+=1

        fav_class_items = fav_class.items()
        # Будем отдавать наиболее часто встречаюшегося соседа
        fav_class_items.sort(key = lambda x:x[1])
        return fav_class_items[-1][0]

        # Результаты для максимума и для вероятностного подхода практически не отличаются
        # fav_distance = [i[1]**4 for i in fav_class_items]
        # return fav_class_items[fav_distance.index(get_probability_class(fav_distance))][0]

