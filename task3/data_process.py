#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

import os

from net import Net
from means import Model
from fileutils import load_dat_file
from settings import TEMPLATES_DIR

def get_model(filename):
    data = load_dat_file(filename)
    input_size = 7
    # model = Net(input_size)
    model = Model(10)
    for item in data:
        model.add_point(item[:-1],item[-1])
        # model.trainquery(item[:-1], item[-1:], item[-1])

    return model

def get_result_in_html(model, pair):
    templatefile = os.path.join(TEMPLATES_DIR, 'outtable.html')
    filedata = pair[0]
    row_list =  load_dat_file(filedata)
    table_out = ''
    error_count = 0
    for row in row_list:
        row_out = ''

        for td in row:
            row_out+= '<td class="col-md-1">%s</td>' % td
        model_result = model.get_result(row[:-1])

        if model_result == td:
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
            'filedata': os.path.split(pair[1])[1],
            'filemodel': os.path.split(pair[0])[1]
        })
    return  template
