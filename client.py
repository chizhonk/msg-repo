# Программа клиента с функциями:
# 1) сформировать​​ presence-сообщение,
# 2) отправить​​ сообщение ​​серверу,
# 3) получить​​ ответ ​​сервера,
# 4) разобрать​​ сообщение ​​сервера.
#
# Параметры командной строки: client.py <host> [<port>]

from socket import *
import argparse
import time
from jim import utils


def create_parser():
    """ Возвращает парсер двух аргуметов командной строки: IP-адрес и порт.
    IP-адрес - обязательный аргумент. Порт - необязательный (по умолчанию задается как [7777]).

    Следующий тест сработает при передаче в качестве в командной строке одного аргумента localhost.
    >>> create_parser()
    Namespace(addr='localhost', port='[7777]')

    :return: парсер двух аргументов (адрес - обязательный, порт - необязательный)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr')
    parser.add_argument('port', nargs='?', default='[7777]')
    return parser.parse_args()


def create_presence_message():
    """ Создает словарь/json presence-сообщения.

    >>> create_presence_message()['action']
    'presence'

    :return: словарь/json presence-сообщения
    """
    presence = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': 'C0deMaver1ck',
            'status': 'Yep, I am here!'
        }
    }
    return presence


def srv_code_into_answer(code):
    """ Принимает на вход числовой HTTP-код ошибки и дает его расшифровку.

    >>> srv_code_into_answer(200)
    'OK'

    >>> srv_code_into_answer(400)
    'WRONG_REQUEST'

    >>> srv_code_into_answer(101)
    Traceback (most recent call last):
        ...
    ValueError: Unknown error code!


    :param code: ответ сервера в виде HTTP-кода ошибки
    :return: ответ сервера в виде строки
    """
    code_dict = {
        100: 'BASIC_NOTICE',
        200: 'OK',
        202: 'ACCEPTED',
        400: 'WRONG_REQUEST',
        500: 'SERVER_ERROR'
    }
    if code in code_dict.keys():
        return code_dict[code]
    else:
        raise ValueError('Unknown error code!')


# Создание сокета TCP
s = socket(AF_INET, SOCK_STREAM)

# Соединение с сервером
namespace = create_parser()
s.connect((namespace.addr, int(namespace.port[1:-1])))

# Формирование presence-сообщения
presence_message = create_presence_message()

# Отправка presence-сообщения серверу
utils.send_message(s, presence_message)

# Получение ответа сервера
srv_response = utils.get_message(s)
s.close()

# Разбор ответа сервера
srv_answer = srv_code_into_answer(srv_response['response'])
print(srv_answer)
