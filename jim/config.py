import time


code_dict = {
            100: 'BASIC_NOTICE',
            200: 'OK',
            202: 'ACCEPTED',
            400: 'WRONG_REQUEST',
            500: 'SERVER_ERROR'
        }


class JIMMsg:
    def __init__(self, action, message=None):
        self.msg = {'action': '',
                    'time': '',
                    'message': ''}
        if action in ['presence', 'msg']:
            self.msg['action'] = action
        else:
            raise Exception('Недопустимое значение поля action!')
        self.msg['time'] = time.time()
        self.msg['message'] = message


class JIMResponse:
    def __init__(self, response_code):
        self.resp = {'response': '',
                     'time': '',
                     'error': ''}
        if type(response_code) is int:
            if response_code in [200, 400]:
                self.resp['response'] = response_code
            else:
                raise Exception('Недопустимое значение поля response_code!')
        else:
            raise Exception('Недопустимый формат поля response_code!')
        self.resp['time'] = time.time()
        if response_code == 400:
            self.resp['error'] = 'Недопустимый запрос / JSON-объект!'


"""Константы для jim протокола, настройки"""

# Ключи
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
RESPONSE = 'response'
ERROR = 'error'

# Значения
PRESENCE = 'presence'

# Коды ответов (будут дополняться)
BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400  # неправильный запрос/json объект
SERVER_ERROR = 500

# Кортеж из кодов ответов
RESPONSE_CODES = (BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR)









