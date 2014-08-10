#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

import re

from regexp_gen import _get_value, prematched_compiler
from legacy import testdataset


__doc__ = '''

Строки базовый элемент, к строкам применим синтаксис регулярных выражений символы ( ) ? [ ] . +  -  etc
При необходимости экранирования, необходимо использовать символ "\":
    строка '\.?' - как и ранее будет интерпретироваться как "точка или ничего".

Строки сложенные в кортеж объединяются с условием "или" объединяясь в группу:
    ('', '2', '3', '5') => '(|2|3|5)'

Строки сложенные в список конкатенируются:
    ['', '2', '3', '5'] => '235'

При необходимости добавить условие "?" элемент необходимо обернуть в Словарь и добавить "'require': False":
    {'value': ('', '2', '3', '5'), 'require': False} => '(|2|3|5)?'

При необходиомости обособить группой произвольный набо символов необхоимо добавить к словарю "'group: True'"
    ['a', 'b', {'value':['1', ('А','Я'), '2'], group: True}] => 'ab(1(А|Я)2)'
    { 'value':[u'уп', {'value':[u'аков',(u'ки',u'ка',u'ок')],'require':False, group: True}]} => 'уп(аков(ки|ка|ок))?'

Для поиска по документу можно добавлять к элементам 'alias': <Имя эллемента>
'''

_UNITS = ur'(' \
         ur'(ст?(\.?|ол\.?|олов(ые|ых|ой))|ч(\.?|айн(ые|ых|ой)))?\s*л(ож(ек|ки|а))?|' \
         ur'шт(ук|уки)?|горст(ь|ей)|(к(ило)?)?г(р(амма?)?)?|(м(илли)?)?л(итра?)?|' \
         ur'уп(аков(ки|ка|ок))?|п(акетик(|ов|а))?|чашк(а|и)|' \
         ur'стакан(а|ов)?|банк(а|и)|половинк?(ы|а|и)|' \
         ur'лист(ьев|ов|а)?|(вето|пало|стру)(чек|чка|чки)|' \
         ur'бутон(чик|чика|чиков)|зубчик(а|ов)?|полос(ок|ка)|стеб(лей|ель)|щепотк(а|и|ок)|' \
         ur'гол(овк(у|а|и))?' \
         ur')'

CUT_UNITS = re.compile(ur'^({_UNITS}(\.|\s)\s*)?(?P<matched>.*)'.format(_UNITS=_UNITS), flags=re.X | re.I | re.U)

_UNITS2 = (
    {
        'value':[
            {
                'value':(
                    {
                        'value':[u'ст?', (u'\.?', u'ол\.?', [u'олов', (u'ые',u'ых',u'ой')])],'alias': u'столовые'
                    },
                    {
                        'value':[u'ч', (u'\.?',[u'айн',(u'ые',u'ых',u'ой')])],'alias':u'чайные'
                    }
                ),'require':False
            },
            ur'\s*',
            {
                'value':[ u'л',{'value':[u'ож',(u'ек',u'ки',u'а')],'group':True}],
                'require':False,
                'alias':'ложки'
            }
        ]
    },
    {
        'value':[u'шт',{'value':(u'ук',u'уки'),u'require':False},], 'alias': "штуки"
    },
    {
        'value':[u'горст',(u'ь',u'ей')], 'alias':'горстей'
    },
    {
        'value':[
            {
                'value':[u'к',{'value':u'ило','group':True,'require':False}],
                'group':True,'require':False
            },
            {'value': [
                u'г',
                {'value': [
                    u'р',
                    {'value':u'амма?','require':False,'group':True}
                ],
                 'require':False,
                 'group':True}
            ],
             }
        ],'alias':'килограммы'
    },
    {
        'value':[
            {
                'value': [u'м',{'value':u'илли','group': True,'require': False}],
                'group': True, 'require': False
            },
            {
                'value': [u'л',{'value': u'итра', 'group':True, 'require': False}],
                'require': False
            }
        ], 'alias':'миллилитры'
    },
    {
        'value':[u'уп', {'value':[u'аков',(u'ки',u'ка',u'ок')],'require':False, 'group':True}], 'alias': 'упаковки'
    },
    {
        'value': [u'п',{'value':[u'акетик',('',u'ов',u'а')],'require':False, 'group':True}], 'alias': 'пакетики'
    },
    {
        'value': [u'чашк',(u'а',u'и')]
    },
    {
        'value': [u'стакан',{'value':(u'а',u'ов'),'require': False}], 'alias': 'стакан'
    },
    {
        'value': [u'банк',(u'а',u'и')], 'alias':'банки'
    },
    {
        'value': [u'половинк?',(u'ы',u'а',u'и')], 'alias': 'половинки'
    },
    {
        'value':[
            u'лист',
            {'value':
                 (u'ьев',u"ов",u"а"),
             'require': False
            }
        ],
        'alias': "листьев"
    },
    {
        'value': [
            {'value':(u'вето',u'пало',u'стру')},
            {'value':(u'чек',u'чка',u'чки')}
        ],'alias': 'веточки палочки стручки'
    },
    {
        'value': [u'бутон', (u'чик', u'чика', u'чиков')], 'alias':'бутончик'
    },
    {
        'value': [u'зубчик',{'value':(u'а',u'ов'), 'require': False}],'alias':'зубчиков'
    },
    {
        'value': [u'полос', (u'ок', u'ка')], 'alias': 'полосок'
    },
    {
        'value': [u'стеб', (u'лей', u'ель')], 'alias': 'стеблей'
    },
    {
        'value': [u'щепотк', (u'а', u'и', u'ок')], 'alias': 'щепотка'
    },
    {
        'value': [u'гол', {'value':[u'овк', (u'у', u'а', u'и')], 'group':True, 'require': False}]
    }
)

if __name__ == '__main__':
    ITEM = ' UNIT'
    new_regexp = prematched_compiler(_get_value(_UNITS2))
    old_regexp = CUT_UNITS
    for item in test:
        new = re.match(new_regexp, item+ITEM).groupdict().get('matched','')
        old = re.match(old_regexp, item+ITEM).groupdict().get('matched','')
        # print new, '|', old, '|', new==old

    # print _UNITS
    # print _get_value(_UNITS2)


