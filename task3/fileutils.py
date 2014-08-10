#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'


# from zipfile import ZipFile
import settings
import os
import numpy
from array import array
from zipfile import ZipFile

def unpack(outpath, zipfile):
    filelist = []
    with ZipFile(zipfile, 'r') as myzip:
        for name in myzip.namelist():
            myzip.extract(name, settings.TEMP_DIR)
            filelist.append(os.path.join(settings.TEMP_DIR, name))
    return filelist

def clear_temp(temp=settings.TEMP_DIR):
    for the_file in os.listdir(temp):
        file_path = os.path.join(temp, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            print e

def load_dat_file(filename):
    '''
    Загрузчик файла с данными, исключительно под данную задачу
    '''
    data = []
    with open(filename,'rb') as dat_file:
        for line in dat_file:
            if line[0] == '@':
                continue
            row = [float(i) for i in line.replace('\r\n','').split(',')]
            row[-1] = int(row[-1])
            data.append(row)
    return data
