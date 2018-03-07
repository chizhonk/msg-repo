from server import create_response_200, create_response_400, create_answer, new_listen_socket, read_requests, write_responses
import socket
from pytest import raises


# Модульные тесты
def test_create_response_200():
    assert create_response_200()['response'] == 200

def test_create_response_400():
    assert create_response_400()['response'] == 400

def test_create_answer():
    assert create_answer({'action': 'presence'})['response'] == 200
    assert create_answer({'action': 'whatever'})['response'] == 400

def test_new_listen_socket():
    assert new_listen_socket(('', 7777)).getsockname() == ('0.0.0.0', 7777)
    assert new_listen_socket(('127.0.0.1', 8888)).getsockname() == ('127.0.0.1', 8888)
    with raises(socket.gaierror):
        new_listen_socket(('abc', 0))


# Интеграционные тесты
class MySocket():
    ''' Класс-заглушка для операций с сокетом
    '''
    def __init__(self, sock_type=socket.AF_INET, sock_family=socket.SOCK_STREAM):
        self.data = b''

    def send(self, data):
        self.data = data
        return len(data)

    def recv(self, n):
        return b'Hello'

def test_read_requests(monkeypatch):
    monkeypatch.setattr("socket.socket", MySocket)
    clients = []
    sock = socket.socket()
    clients.append(sock)
    assert read_requests(clients, clients) == {sock: 'Hello'}
    clients.remove(sock)
    assert read_requests(clients, clients) == {}

def test_write_responses(monkeypatch):
    monkeypatch.setattr("socket.socket", MySocket)
    requests = {}
    sock_r = socket.socket() # сокет для словаря requests
    requests[sock_r] = 'Hey!'
    clients = []
    sock_w = socket.socket() # сокет для приема сообщений
    clients.append(sock_w)
    assert write_responses(requests, clients, clients) == len('Hey!')
    clients.remove(sock_w)
    assert write_responses(requests, clients, clients) == len('')

