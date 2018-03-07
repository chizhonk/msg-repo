# Программа клиента с функциями:
# 1) отправить presence-сообщение серверу и получить от него ответ 'OK',
# 2) в зависимости от указания ключа -r/-w клиент является читателем/писателем:
#   -r: получить сообщения от клиентов-писателей и вывести в чат
#   -w: отправить сообщения в чат
#
# Параметры командной строки: client.py -r -w <host> [<port>]

from socket import *
import argparse
import time
from jim import utils
import logging
import log_config


logger = logging.getLogger('msg')

def log(func):
    """ Декорирует функцию func для логгирования ее имени и аргументов согласно настройкам объекта logger.

    :param func: имя декорируемой функции
    :return: имя декорирующей функции
    """
    def decorated(*args, **kwargs):
        logger.info('{}({}, {})'.format(func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return decorated


@log
def create_parser():
    """ Возвращает парсер четырех аргуметов командной строки: -r, -w, IP-адрес и порт.
    IP-адрес - обязательный аргумент. Порт - необязательный (по умолчанию задается как [7777]).
    -r - признак клиента-читателя. -w - признак клиента-писателя.

    Следующий тест сработает при передаче в качестве в командной строке одного аргумента localhost.
    >>> create_parser()
    Namespace(addr='localhost', port='[7777]', r=False, w=False)

    :return: парсер четырех аргументов (-r, -w, адрес - обязательный, порт - необязательный)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', action='store_const', const=True, default=False)
    parser.add_argument('-w', action='store_const', const=True, default=False)
    parser.add_argument('addr')
    parser.add_argument('port', nargs='?', default='[7777]')
    return parser.parse_args()


@log
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
            'status': 'Yep, I am here!'
        }
    }
    return presence


@log
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


@log
def recv_msg_from_server(s):
    """ Получает сообщения от сервера.

    :param s: сокет
    :return: None
    """
    data = s.recv(1024).decode('utf-8')
    print('Message: ', data)
    return data


@log
def send_msg_to_server(s, msg):
    """ Отправляет сообщения на сервер.

    :param s: сокет
    :param msg: отправляемое сообщение
    :return: длина отправленного сообщения (для тестирования)
    """
    test_len = s.send(msg.encode('utf-8'))
    return test_len


@log
def chat_client():
    """ Основная функция.
    - создает экземпляр класса socket с заданным IP-адресом и портом для соединения с сервером
    - формирует presence-сообщение, отправляет на сервер и получает в ответ 'OK'
    - если читатель: в цикле получает сообщения на экран
    - если писатель: в цикле отправляет сообщения на сервер

    :return: None
    """
    # Создание сокета TCP
    with socket(AF_INET, SOCK_STREAM) as s:
        # Соединение с сервером
        namespace = create_parser()
        s.connect((namespace.addr, int(namespace.port[1:-1])))

        # Формирование presence-сообщения
        presence_message = create_presence_message()
        # Отправка presence-сообщения серверу
        utils.send_message(s, presence_message)
        # Получение ответа сервера
        srv_response = utils.get_message(s)
        # Разбор ответа сервера
        srv_answer = srv_code_into_answer(srv_response['response'])
        print(srv_answer)

        if namespace.w == False:
            while True:
                recv_msg_from_server(s)
        elif namespace.r == False and namespace.w == True:
            while True:
                msg = input('Ваше сообщение: ')
                if msg == 'exit':
                    break
                else:
                    send_msg_to_server(s, msg)

        else:
            print('Вы можете указать либо чтение, либо запись!')


if __name__ == '__main__':
    chat_client()
