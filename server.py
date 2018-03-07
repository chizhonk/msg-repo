# Программа сервера мессенджера с функциями:
# 1) принимает presence-сообщения клиентов и отправляет в ответ 'OK',
# 2) читает запросы клиентов-писалетей на запись в чат,
# 3) отправляет клиентам-получателям сообщения клиентов-писателей.
#
# Параметры командной строки для запуска: server.py -p <port> -a <host>

import select
from socket import socket, AF_INET, SOCK_STREAM
import argparse
import time
from jim import utils
import logging
import log_config


# Получаем ссылку на объект getLogger('server')
logger = logging.getLogger('server')

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
    """ Возвращает парсер двух аргуметов командной строки: порт и IP-адрес.
    Оба аргумента необязательные (по умолчанию порт задается как 7777, IP-адреса прослушиваются все).

    Следующий тест сработает, если в командной строке ничего не передавать.
    >>> create_parser().parse_args()
    Namespace(a='', p='7777')

    :return: парсер двух аргументов (адрес - обязательный, порт - необязательный)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default='7777')
    parser.add_argument('-a', default='')
    return parser


@log
def create_response_200():
    """ Создает словарь/json ответа сервера с HTTP-кодом ошибки 200.

    >>> create_response_200()['response']
    200

    :return: словарь/json ответа с кодом 200
    """
    response_200 = {
        'response': 200,
        'time': time.time()
    }
    return response_200


@log
def create_response_400():
    """ Создает словарь/json ответа сервера с HTTP-кодом ошибки 400.

    >>> create_response_400()['response']
    400

    :return: словарь/json ответа с кодом 400
    """
    response_400 = {
        'response': 400,
        'time': time.time(),
        'error': 'Wrong request / JSON object!'
    }
    return response_400


@log
def create_answer(received_msg):
    """ В ответ на presence-сообщение клиента формирует ответ с HTTP-кодом ошибки 200 (OK).
    В ответ на любое другое сообщение клиента формирует ответ с HTTP-кодом ошибки 400 (WRONG_REQUEST).

    >>> create_answer({'action': 'presence'})['response']
    200

    >>> create_answer({'action': 'whatever'})['response']
    400

    :param received_msg: словрь/json сообщения клиента
    :return: ответ сервера с HTTP-кодом ошибки
    """
    if received_msg['action'] == 'presence':
        return create_response_200()
    else:
        return create_response_400()


@log
def new_listen_socket(address):
    """ Создает новый экземпляр класса socket с IP-адресом и портом, переданными в качестве аргумента.
    Устанавливается таймаут для операций с сокетом.

    :param address: IP-адрес и порт
    :return: сокет
    """
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(address)
    sock.listen(5)
    sock.settimeout(0.2)
    return sock


def read_requests(r_clients, all_clients):
    """ Читает запросы клиентов-писателей на запись в чат и возвращает словарь {сокет: запрос}.
    Удаляет из списка клиентов отключившегося клиента
    (при отключении клиента он по умолчанию попадает в список писателей и пытается писать в чат '').

    :param r_clients: список клиентов-писателей
    :param all_clients: список всех клиентов
    :return: словарь {сокет: данные}
    """
    responses = {}

    for sock in r_clients:
        try:
            data = sock.recv(1024).decode('utf-8')
            responses[sock] = data
            if data == '':
                all_clients.remove(sock)
        except:
            print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
            all_clients.remove(sock)

    return responses


def write_responses(requests, w_clients, all_clients):
    """ Отправляет клиентам-читателям запросы клиентов писателей.
    Удаляет клиента из списка всех клиентов при отключении.

    :param requests: словарь с запросами клиентов-писателей
    :param w_clients: список клиентов-читателей
    :param all_clients: список всех клиентов
    :return: суммарная длина отправленных сообщений (нужно только для тестирования)
    """
    test_len = 0
    for w_sock in w_clients:
        for sock in requests:
            if sock != w_sock:
                try:
                    resp = requests[sock].encode('utf-8')
                    test_len += w_sock.send(resp)
                except:
                    print('Клиент {} {} отключился'.format(w_sock.fileno(), w_sock.getpeername()))
                    w_sock.close()
                    all_clients.remove(w_sock)
    return test_len


@log
def mainloop():
    """ Основная функция:
    - создает экземпляр класса socket с заданным IP-адресом и портом
    - в цикле:
        - если новый клиент подключился, добавляет его в список клиентов, принимает presence-сообщение и отвечает 'OK'
        - делит всех клиентов на писателей и читателей
        - сохраняет запросы клиентов-писателей с помощью функции read_requests
        - отправляет сообщения клиентам-читателям с помощью функции write_responses

    :return: None
    """
    clients = []

    parser = create_parser()
    namespace = parser.parse_args()
    address = (namespace.a, int(namespace.p))
    s = new_listen_socket(address)

    while True:
        try:
            conn, addr = s.accept()  # Проверка подключений
        except OSError as e:
            pass  # timeout вышел
        else:
            print("Получен запрос на соединение с %s" % str(addr))
            clients.append(conn)
            # Принятие presence-сообщения клиента
            received_msg = utils.get_message(conn)
            # Формирование ответа клиенту
            answer = create_answer(received_msg)
            # Отправка ответа клиенту
            utils.send_message(conn, answer)
        finally:
            wait = 0
            r = []
            w = []
            try:
                r, w, e = select.select(clients, clients, [], wait)
            except Exception as e:
                pass

            requests = read_requests(r, clients)  # Сохраним запросы клиентов на отправку сообщений
            write_responses(requests, w, clients)  # Выполним отправку сообщений клиентам


if __name__ == '__main__':
    mainloop()
