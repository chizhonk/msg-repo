# Программа сервера мессенджера с функциями:
# 1) принимает presence-сообщения клиентов и отправляет в ответ 'OK',
# 2) читает запросы клиентов-писалетей на запись в чат,
# 3) отправляет клиентам-получателям сообщения клиентов-писателей.
#
# Параметры командной строки для запуска: server.py -p <port> -a <host>

from os import path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import log_config
import argparse
from socket import socket, AF_INET, SOCK_STREAM
import select
from jim.config import JIMResponse, JIMMsg
import json
from repo.server_models import Client, ClientContact, Base
from repo.server_repo import Repo

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
        self.clients = {} # словарь сокет-username клиентов, подключенных к чату
        self.dwh = None # объект хранилища (инициализируется в процессе работы метода create_db_session)

    def create_db_session(self):
        """ Создает сессию подключения к базе данных

        :return:
        """
        # Путь до папки где лежит этот модуль
        SERVER_PATH = path.dirname(path.abspath(__file__))
        # Путь до файла базы данных
        DB_PATH = path.join(SERVER_PATH, 'repo/server.db')
        # Создаем движок
        engine = create_engine('sqlite:///{}'.format(DB_PATH), echo=False)
        # Создаем структуру базы данных
        Base.metadata.create_all(engine)
        # Создаем сессию для работы
        Session = sessionmaker(bind=engine)
        session = Session()

        self.dwh = Repo(session)

        return session

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
                    self.clients.pop(sock)
                elif data['action'] == 'msg' or data['action'] == 'add_contact':
                    responses[sock] = data
                else:
                    raise Exception('Сообщение должно иметь action "msg" или "add_contact"!')
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                self.clients.pop(sock)

        return responses

    def write_responses(self, requests, w_clients):
        """ Отправляет клиентам-читателям запросы клиентов-писателей.
        Удаляет клиента из списка всех клиентов при отключении.

        :param requests: словарь с запросами клиентов-писателей
        :param w_clients: список клиентов-читателей
        :return: суммарная длина отправленных сообщений (нужно только для тестирования)
        """
        test_len = 0
        for sock in requests:
            if requests[sock]['action'] == 'add_contact':
                add_status = self.dwh.add_contact(self.clients[sock], requests[sock]['user']['account_name'])
                if add_status == 0:
                    resp = JIMResponse(response_code=200).resp
                    # print('Добавляем контакт', requests[sock]['user']['account_name'], ' клиенту ', self.clients[sock])
                    sock.send(json.dumps(resp).encode('utf-8'))
                else:
                    resp = JIMResponse(response_code=500).resp
                    sock.send(json.dumps(resp).encode('utf-8'))
            elif requests[sock]['action'] == 'msg':
                for w_sock in w_clients:
                    if sock != w_sock:
                        try:
                            resp = JIMMsg(action='msg', message=requests[sock]['message']).msg
                            test_len += len(resp)
                            w_sock.send(json.dumps(resp).encode('utf-8'))
                        except:
                            print('Клиент {} {} отключился'.format(w_sock.fileno(), w_sock.getpeername()))
                            w_sock.close()
                            self.clients.pop(w_sock)
            else:
                raise Exception('Сообщение должно иметь action "msg" или "add_contact"!')
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

        self.create_db_session() # создание сессии для работы с БД

        while True:
            try:
                conn, addr = self.s.accept()  # Проверка подключений
            except OSError as e:
                pass  # timeout вышел
            else:
                print("Получен запрос на соединение с %s" % str(addr))
                # self.clients.append(conn)
                self.clients[conn] = ''
                # Принятие presence-сообщения клиента
                received_msg = json.loads(conn.recv(1024).decode('utf-8'))
                # Формирование ответа клиенту
                if received_msg['action'] == 'presence':
                    username = received_msg['user']['account_name']
                    self.clients[conn] = username
                    if not self.dwh.client_exists(username):
                        self.dwh.add_client(username)
                        print('Клиент добавлен в базу: ', self.dwh.get_client_by_username(username))
                    else:
                        print('Клиент уже есть в базе: ', self.dwh.get_client_by_username(username))
                    self.dwh.add_logon(username, addr[0])
                    # self.dwh.get_logon_history(username)
                    response = JIMResponse(200).resp
                    # Отправка ответа клиенту
                    conn.send(json.dumps(response).encode('utf-8'))

                    received_msg_get_contacts = json.loads(conn.recv(1024).decode('utf-8'))
                    if received_msg_get_contacts['action'] == 'get_contacts':
                        contacts = self.dwh.get_contacts(username)
                        accept = JIMResponse(response_code=202, quantity=len(contacts)).resp
                        conn.send(json.dumps(accept).encode('utf-8'))
                        # for i in range(accept['quantity']):
                        #    contact = JIMMsg(action='contact_list', login=contacts[i].Name).msg
                        #    conn.send(json.dumps(contact).encode('utf-8'))
                else:
                    raise Exception('Первым сообщением должен быть presence!')
            finally:
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients.keys(), self.clients.keys(), [], wait)
                except Exception as e:
                   pass

                requests = self.read_requests(r)  # Сохраним запросы клиентов на отправку сообщений
                self.write_responses(requests, w)  # Выполним отправку сообщений клиентам


if __name__ == '__main__':
    # Создаем парсер, вычитываем аргументы командной строки и формируем адрес
    parser = create_parser()
    namespace = parser.parse_args()
    address = (namespace.a, int(namespace.p))
    print(address)

    # Создаем сервер и запускаем его основной цикл
    serv = MsgTCPServer(address)
    serv.mainloop()


