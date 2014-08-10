#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

import os

from means import FullScanModel, CoreModel, HybridModel
from fileutils import load_dat_file
from settings import TEMPLATES_DIR

def get_model(filename):
    data = load_dat_file(filename)

    model = HybridModel(10)
    # model = CoreModel()
    # model = FullScanModel(5)
    for item in data:
        model.add_point(item[:-1],item[-1])

    return model

def get_result_in_html(model, datafile, sourcefile='', test_mod=False):
    templatefile = os.path.join(TEMPLATES_DIR, 'outtable.html')
    datafile = datafile
    row_list =  load_dat_file(datafile)
    table_out = ''
    error_count = 0
    for row in row_list:
        row_out = ''

        for td in row:
            row_out+= '<td class="col-md-1">%s</td>' % td

        # В тестовых разбиениях так же присутствует метка класса
        # Но в боевой выборке она видимо должна отсутствовать?
        if test_mod: # Если мы проверяемся на тестовых данных, то мы подрезаем метку класса
            model_result = model.get_result(row[:-1])
        else: # Если мы работаем с боевым файлом то мы съедаем всю строку целиком
            model_result = model.get_result(row)

        if model_result == td: # в последней ячейке правильный класс
            r_td = 'class="success"'
        else:
            r_td = 'class="danger"'
            error_count +=1

        row_out += '<td %s>%s</td>' %  (r_td,model_result)

        table_out += '<tr>%s</tr>' % row_out

    table = '<table class="table">%s</table>' % table_out

    with open(templatefile,'r') as template:
        template = template.read().format(**{
            'row_count': len(row_list),
            'error_count': error_count,
            'table': table,
            'filedata': os.path.split(datafile)[1],
            'filemodel': os.path.split(sourcefile)[1]
        })
    return  template
