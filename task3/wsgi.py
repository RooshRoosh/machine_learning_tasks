#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

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
        self.has_model = False
        self.count = 0
        self.urls = [
            ('^$', self.index),
            ('^upload_tra$', self.upload_tra),
            ('^upload_tst$', self.upload_tst)
        ]

    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        path = environ.get('PATH_INFO', '').lstrip('/')
        self.count +=1
        # print self.count
        flag = False
        for regex, callback in self.urls:
            match = re.search(regex, path)
            if match is not None:
                flag = True
                environ['myapp.url_args'] = match.groups()
                return [callback(environ, start_response)]
        if not flag:
            return [self.not_found(environ, start_response)]

    def index(self, environ, start_response):
        '''
            Отдаём страничку для тренировки загрузки
        '''
        with open('templates/loadmodel.html','r') as template:
            return template.read()

    def upload_tra(self, environ, start_response):
        '''
            Создаём таск который отвечает за генерацию модели
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
                    # Отдаём в модуль имя файла - получаем модель
                    model = get_model(pair[0])
                    # Отдаём модуль имя файла и модель - получаем html
                    inner_html += get_result_in_html(model=model, pair=pair)
                message = inner_html

                with open('templates/result.html','r') as template:
                    message = template.read().format(**{'content': inner_html})
            else:
                # Грузим одну модель выкатываем приглашение загрузить тестовую
                message = 'The file "' + fileitem.filename + '" was uploaded successfully'

            return message
        else :
            message = 'please upload a file.'
            return message


    def upload_tst(self, environ, start_response):
        '''
            Чекаем есть ли модель, если есть даём результат
        '''
        print self.has_model
        self.has_model = True
        return 'upload_tst'

    def reset_model(self, environ, start_response):
        pass

    def not_found(self, environ, start_response):
        return 'Страница не найдена'

if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1].lower() == 'test':
        test_mod = True
    else:
        test_mod = False


    httpd = make_server('', 8080, DemoApp(test_mod))
    print "Serving on port 8080... Mod: %s" % sys.argv[1]
    httpd.serve_forever()