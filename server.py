# Программа сервера мессенджера с функциями:
# 1) принимает presence-сообщения клиентов и отправляет в ответ 'OK',
# 2) читает запросы клиентов-писалетей на запись в чат,
# 3) отправляет клиентам-получателям сообщения клиентов-писателей.
#
# Параметры командной строки для запуска: server.py -p <port> -a <host>

import logging
import log_config
import argparse
from socket import socket, AF_INET, SOCK_STREAM
import select
from jim.config import JIMResponse, JIMMsg
import json


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


class MsgTCPServer():
    @log
    def __init__(self, address):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind(address)
        self.s.listen(5)
        self.s.settimeout(0.2)
        self.clients = [] # список клиентов, подключенных к чату

    def read_requests(self, r_clients):
        """ Читает запросы клиентов-писателей на запись в чат и возвращает словарь {сокет: запрос}.
        Удаляет из списка клиентов отключившегося клиента
        (при отключении клиента он по умолчанию попадает в список писателей и пытается писать в чат '').

        :param r_clients: список клиентов-писателей
        :return: словарь {сокет: данные}
        """
        responses = {}

        for sock in r_clients:
            try:
                data = json.loads(sock.recv(1024).decode('utf-8'))
                if data == '':
                    print('yes!!!')
                    self.clients.remove(sock)
                elif data['action'] == 'msg':
                    responses[sock] = data
                else:
                    raise Exception('Сообщение должно иметь action MSG!')
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                self.clients.remove(sock)

        return responses

    def write_responses(self, requests, w_clients):
        """ Отправляет клиентам-читателям запросы клиентов-писателей.
        Удаляет клиента из списка всех клиентов при отключении.

        :param requests: словарь с запросами клиентов-писателей
        :param w_clients: список клиентов-читателей
        :return: суммарная длина отправленных сообщений (нужно только для тестирования)
        """
        test_len = 0
        for w_sock in w_clients:
            for sock in requests:
                if sock != w_sock:
                    try:
                        if requests[sock]['action'] == 'msg':
                            resp = JIMMsg('msg', requests[sock]['message']).msg
                            test_len += len(resp)
                            w_sock.send(json.dumps(resp).encode('utf-8'))
                        else:
                            raise Exception('Сообщение должно иметь action MSG!')
                    except:
                        print('Клиент {} {} отключился'.format(w_sock.fileno(), w_sock.getpeername()))
                        w_sock.close()
                        self.clients.remove(w_sock)
        return test_len

    @log
    def mainloop(self):
        """ Основная функция:
        - в цикле:
            - если новый клиент подключился, добавляет его в список клиентов, принимает presence-сообщение и отвечает 'OK'
            - делит всех клиентов на писателей и читателей
            - сохраняет запросы клиентов-писателей с помощью функции read_requests
            - отправляет сообщения клиентам-читателям с помощью функции write_responses

        :return: None
        """
        while True:
            try:
                conn, addr = self.s.accept()  # Проверка подключений
            except OSError as e:
                pass  # timeout вышел
            else:
                print("Получен запрос на соединение с %s" % str(addr))
                self.clients.append(conn)
                # Принятие presence-сообщения клиента
                received_msg = json.loads(conn.recv(1024).decode('utf-8'))
                # Формирование ответа клиенту
                if received_msg['action'] == 'presence':
                    response = JIMResponse(200).resp
                    # Отправка ответа клиенту
                    conn.send(json.dumps(response).encode('utf-8'))
                else:
                    raise Exception('Первым сообщением должен быть presence!')
            finally:
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except Exception as e:
                   pass

                requests = self.read_requests(r)  # Сохраним запросы клиентов на отправку сообщений
                self.write_responses(requests, w)  # Выполним отправку сообщений клиентам


if __name__ == '__main__':
    # Создаем парсер, вычитываем аргументы командной строки и формируем адрес
    parser = create_parser()
    namespace = parser.parse_args()
    address = (namespace.a, int(namespace.p))

    # Создаем сервер и запускаем его основной цикл
    serv = MsgTCPServer(address)
    serv.mainloop()


