#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

import os
import re
import cgi
import sys
from wsgiref.simple_server import make_server

from fileutils import unpack, clear_temp
from data_process import get_model, get_result_in_html

import settings

class DemoApp:

    def __init__(self, test_mod = False):

        self.test_mod = test_mod # режим работы демона
        self.model = None
        self.urls = [
            ('^$', self.index),
            ('^upload_tra$', self.upload_tra),
            ('^upload_tst$', self.upload_tst),
            ('^reset_model$', self.reset_model)
        ]

    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        path = environ.get('PATH_INFO', '').lstrip('/')

        for regex, callback in self.urls:
            match = re.search(regex, path)
            if match is not None:
                environ['myapp.url_args'] = match.groups()
                return [callback(environ, start_response)]

        return [self.not_found(environ, start_response)]

    def _get_model(self, filename):
        if self.model:
            model = self.model
        else:
            model = get_model(filename)
        return model

    def index(self, environ, start_response):
        '''
            Отдаём страничку для тренировки загрузки
        '''
        with open(os.path.join(settings.TEMPLATES_DIR,'loadmodel.html'),'r') as template:
            return template.read()

    def upload_tra(self, environ, start_response):
        '''
            Прямо в хендлере создаём модель, которую сохраним в.. инстансе приложения,
            Модель после загрузки сделаем неизменяемой - чтобы загрузить новую модель,
             не перезагружая приложение, нужно вызвать медот reset_model сделав запрос на '/reset_model'
            Если Демон запущен в тестовом режиме, то тут же проверим данные
        '''
        clear_temp(settings.TEMP_DIR)
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)

        try:
            fileitem = form['file']
        except KeyError:
            fileitem = None

        if fileitem.file:
            file_list = unpack(settings.TEMP_DIR, fileitem.file)
            file_list.sort()

            if self.test_mod:
                # Грузим все модели все проверяем выкатываем все результаты
                # Групируем тестовые и обучающие
                tra_tst_list, tra_tst = [], []
                for _file in file_list:
                    if len(tra_tst) < 2:
                        tra_tst.append(_file)
                    else:
                        tra_tst_list.append(tra_tst)
                        tra_tst = [_file]
                else:
                    tra_tst_list.append(tra_tst)

                inner_html = ''
                for pair in tra_tst_list:
                    # Отдаём имя файла с данными - получаем модель
                    self.model = self._get_model(pair[0])
                    # Отдаём модуль имя файла с тестовыми данными и модель - получаем html
                    inner_html += get_result_in_html(
                        model = self.model, # ?
                        datafile=pair[1],
                        sourcefile=pair[0],
                        test_mod=self.test_mod
                    )
                with open(os.path.join(settings.TEMPLATES_DIR,'result.html'),'r') as template:
                    message = template.read().format(**{'content': inner_html})
            else:
                # Грузим одну модель выкатываем приглашение загрузить тестовую
                self.model = self._get_model(file_list[0])
                with open(os.path.join(settings.TEMPLATES_DIR,'wellcome_test.html'),'r') as template:
                    message = template.read()
            return message
        else :
            message = 'please upload a file.'
            return message


    def upload_tst(self, environ, start_response):
        '''
            Чекаем есть ли модель, если есть даём результат
        '''
        if self.model:
            clear_temp(settings.TEMP_DIR)
            form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)

            try:
                fileitem = form['file']
            except KeyError:
                fileitem = None

            if fileitem.file:
                file_list = unpack(settings.TEMP_DIR, fileitem.file)
                inner_html = get_result_in_html(
                    model=self.model,
                    datafile=file_list[0],
                    test_mod=self.test_mod
                )
                with open(os.path.join(settings.TEMPLATES_DIR,'result.html'),'r') as template:
                    message = template.read().format(**{'content': inner_html})
                return message
            else:
                return 'Обязательно <a href="/">прикрепите файл</a>'
        else:
            return 'Сначала <a href="/">создайте модель, загрузив обучающую выборку</a>'

    def reset_model(self, environ, start_response):
        self.model = None
        return 'Модель сброшена, <a href="/">создайте новую, загрузив обучающую выборку</a>'

    def not_found(self, environ, start_response):
        return 'Страница не найдена, <a href="/">вернуться на главную</a>'

if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1].lower() == 'test':
        test_mod = True
        mod = 'test'
    else:
        test_mod = False
        mod = 'stage'

    httpd = make_server('', 8080, DemoApp(test_mod))
    print "Serving on port 8080... Mod: %s" % mod
    httpd.serve_forever()