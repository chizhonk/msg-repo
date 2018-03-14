# Программа клиента с функциями:
# 1) отправить presence-сообщение серверу и получить от него ответ 'OK',
# 2) в зависимости от указания ключа -r/-w клиент является читателем/писателем:
#   -r: получить сообщения от клиентов-писателей и вывести в чат
#   -w: отправить сообщения в чат
#
# Параметры командной строки: client.py -r -w <host> [<port>]

import logging
import log_config
import argparse
from socket import socket, AF_INET, SOCK_STREAM
from jim import utils
from jim.config import JIMMsg, code_dict


# Получаем ссылку на объект getLogger('msg')
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
def client_type(namespace):
    """ Возвращает тип клинта (r или w) в зависимости от содержания namespace.

    :param namespace: параметры командной строки
    :return: тип клиента (r - читатель, w - писатель)
    """
    if namespace.w == False:
        return 'r'
    elif namespace.r == False and namespace.w == True:
        return 'w'
    else:
        raise Exception('Клиент может создаваться либо на чтение, либо на запись!')


class MsgTCPClient:
    @log
    def __init__(self, type, address=None):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.type = type
        if address: # для возможности тестирования без подключения к серверу
            self.s.connect(address)

    @log
    def create_presence_message(self):
        """ Создает словарь/json presence-сообщения.

        :return: словарь/json presence-сообщения
        """
        return JIMMsg('presence').msg

    @log
    def create_chat_message(self, message):
        """ Создает словарь/json сообщения для последующей отправки в чат.

        :param message: сообщение для заполнения поля message в json
        :return: словарь/json сообщения
        """
        return JIMMsg('msg', message).msg

    @log
    def send_message(self, jsonmsg):
        """ Отправляет сообщения на сервер.

        :param jsonmsg: отправляемое сообщение
        :return: длина отправленного сообщения (для тестирования)
        """
        utils.send_message(self.s, jsonmsg)
        return len(jsonmsg)

    @log
    def get_message(self):
        """ Получает сообщения от сервера.

        :return: словарь / json-сообщение
        """
        return utils.get_message(self.s)

    @log
    def resp_code_into_text(self, srv_response):
        """ Принимает на вход словарь-response с числовым HTTP-кодом ошибки и дает его расшифровку.

        :param srv_response: ответ сервера в виде HTTP-кода ошибки
        :return: ответ сервера в виде строки
        """
        if srv_response['response'] in code_dict.keys():
            return code_dict[srv_response['response']]
        else:
            raise ValueError('Неизвестный код ошибки!')

    @log
    def chat_client(self):
        """ Основная функция.
        - формирует presence-сообщение, отправляет на сервер и получает в ответ 'OK'
        - если читатель: в цикле получает сообщения на экран
        - если писатель: в цикле отправляет сообщения в чат

        :return: None
        """
        self.send_message(self.create_presence_message())
        response = self.get_message()
        print(self.resp_code_into_text(response))

        if self.type == 'r':
            while True:
                response = self.get_message()
                print(response['message'])
        else:
            while True:
                msg = input('Ваше сообщение: ')
                if msg == 'exit':
                    break
                else:
                    self.send_message(self.create_chat_message(msg))


if __name__ == '__main__':
    # Создаем парсер, вычитываем аргументы командной строки, формируем адрес и тип клиента
    namespace = create_parser()
    address = (namespace.addr, int(namespace.port[1:-1]))
    type = client_type(namespace)

    # Создаем клиента и присоединяем его к чату
    clnt = MsgTCPClient(type, address)
    clnt.chat_client()









