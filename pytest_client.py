from pytest import raises
from client import create_presence_message, srv_code_into_answer, recv_msg_from_server, send_msg_to_server
import socket


# Модульные тесты
def test_create_presence_msg():
    assert create_presence_message()['action'] == 'presence'

def test_srv_code_into_answer():
    with raises(ValueError):
        srv_code_into_answer(101)
    assert srv_code_into_answer(200) == 'OK'
    assert srv_code_into_answer(400) == 'WRONG_REQUEST'


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

def test_recv_msg_from_server(monkeypatch):
    monkeypatch.setattr("socket.socket", MySocket)
    sock = socket.socket()
    assert recv_msg_from_server(sock) == 'Hello'

def test_send_msg_to_server(monkeypatch):
    monkeypatch.setattr("socket.socket", MySocket)
    sock = socket.socket()
    assert send_msg_to_server(sock, 'Hey!') == len('Hey!')
