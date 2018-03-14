from pytest import raises
from client import MsgTCPClient, client_type
import socket
from argparse import Namespace
from jim.config import JIMMsg, JIMResponse
from jim.utils import dict_to_bytes


def test_client_type():
    assert client_type(Namespace(addr='localhost', port='[7777]', r=False, w=True)) == 'w'
    assert client_type(Namespace(addr='localhost', port='[7777]', r=True, w=False)) == 'r'
    assert client_type(Namespace(addr='localhost', port='[7777]', r=False, w=False)) == 'r'
    with raises(Exception):
        client_type(Namespace(addr='localhost', port='[7777]', r=True, w=True))


class MySocket():
    ''' Класс-заглушка для операций с сокетом
    '''
    def __init__(self, sock_type=socket.AF_INET, sock_family=socket.SOCK_STREAM):
        self.data = b''

    def send(self, data):
        self.data = data
        return len(data)

    def recv(self, n):
        return dict_to_bytes(JIMMsg('msg', 'Hello!').msg)


class TestMsgTCPClient:

    def setup(self):
        self.clnt = MsgTCPClient('r')

    def teardown(self):
        del self.clnt

    def test_create_presence_message(self):
        assert self.clnt.create_presence_message()['action'] == 'presence'

    def test_create_chat_message(self):
        assert self.clnt.create_chat_message('HELLO!')['message'] == 'HELLO!'

    def test_send_message(self, monkeypatch):
        monkeypatch.setattr("socket.socket", MySocket)
        self.clnt.s = socket.socket()
        assert self.clnt.send_message({'message': 'HELLO!'}) == len({'message': 'HELLO!'})

    def test_get_message(self, monkeypatch):
        monkeypatch.setattr("socket.socket", MySocket)
        self.clnt.s = socket.socket()
        assert self.clnt.get_message()['message'] == 'Hello!'

    def test_resp_code_into_text(self):
        assert self.clnt.resp_code_into_text({'response': 100}) == 'BASIC_NOTICE'
        assert self.clnt.resp_code_into_text({'response': 200}) == 'OK'
        assert self.clnt.resp_code_into_text({'response': 202}) == 'ACCEPTED'
        assert self.clnt.resp_code_into_text({'response': 400}) == 'WRONG_REQUEST'
        assert self.clnt.resp_code_into_text({'response': 500}) == 'SERVER_ERROR'
        with raises(ValueError):
            self.clnt.resp_code_into_text({'response': 111})
        assert self.clnt.resp_code_into_text(JIMResponse(200).resp) == 'OK'
        assert self.clnt.resp_code_into_text(JIMResponse(400).resp) == 'WRONG_REQUEST'
        with raises(Exception):
            self.clnt.resp_code_into_text(JIMResponse(100).resp)
        with raises(Exception):
            self.clnt.resp_code_into_text(JIMResponse('abc').resp)

