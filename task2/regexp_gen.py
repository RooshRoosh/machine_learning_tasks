#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

import re

def prematched_compiler(units):
    return re.compile(
        ur'^({units}(\.|\s)\s*)?(?P<matched>.*)'.format(units=units), flags=re.X | re.I | re.U
    )

def _get_value(config):

    string = ur''

    if type(config) == str or type(config) == unicode:
        string += config

    elif type(config) == list:
        for item in config:
            string += _get_value(item)

    elif type(config) == tuple:
        string += '|'.join([_get_value(i) for i in config])
        string = '(%s)' % string

    elif type(config) == dict:
        item =  config.get('value', None)
        req = config.get('require', None)
        group = config.get('group', None)
        if item:
            string += _get_value(item)
            if group:
                string = '(%s)' % string
            if req == False:
                string += '?'
        else:
            raise SyntaxError(u'Пустой литерал')
    else:
        raise TypeError
    return string

