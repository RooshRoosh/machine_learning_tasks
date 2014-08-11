#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

import pymorphy2
import re

morph = pymorphy2.MorphAnalyzer()

cut_words = [
    u'гол',
    u'кг',
    u'г',
    u'л',
    u'мл',
    u'п',
    u'уп'
]

words = [
    u'головка',
    u"бутончик",
    u"чашка",
    u"стакан",
    u'штук',
    u'грамм',
    u'килограмм',
    u'милиграмм',
    u'литр',
    u'милилитр'
    u'банка',
    u'половина',
    u'половинка',
    u'пакетик',
    u'упаковка',
    u'горсть',
    {'w':u'ложка', 'pre':[u'чайная', u'ч', u'ч.', u'столовая', u'ст', u'ст.'],'post':[]},
    u'веточка',
    u'палочка',
    u'стручек',
    u'лист',
    u'щепотка',
    u'стебель',
    u'полоска',
    u'зубчик',
]

text = u'Съешь ещё головку чеснока, выпей чашку чая и стакан молока'

for word in words:
    if type(word) == str or type(word)== unicode:
        word_parse = morph.parse(word)
        for item in word_parse[0].lexeme:
            cut_words.append(item.word)
    else:
        phrase_scope = []
        word_parse = morph.parse(word['w'])
        for item in word_parse[0].lexeme:

            for pre_word in word['pre']: # слова
                phrase = u''
                pre_word_ = morph.parse(pre_word)[0].inflect(set([item.tag.case,item.tag.number]))
                if pre_word_:
                    phrase = pre_word_.word+' '+item.word
                else:
                    phrase = pre_word+' '+item.word

                for post_word in word['post']: # слова
                    post_word_ = morph.parse(post_word)[0].inflect(set([item.tag.case,item.tag.number]))
                    if post_word_:
                        phrase+=' ' + post_word_.word
                    else:
                        phrase+=' ' + post_word

                cut_words.append(phrase)

cut_words = list(set(cut_words))
cut_words.sort()

_UNITS = '(%s)' % '|'.join(cut_words)
# print _UNITS
CUT_UNITS = re.compile(ur'^({_UNITS}(\.|\s)\s*)?(?P<matched>.*)'.format(_UNITS=_UNITS), flags=re.X | re.I | re.U)




