from server import MsgTCPServer
import socket
from pytest import raises
from jim.config import JIMMsg
from jim.utils import dict_to_bytes

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


class TestMsgTCPServer:

    def setup(self):
        self.serv = MsgTCPServer(('', 7777))

    def teardown(self):
        del self.serv

    def test_read_requests(self, monkeypatch):
        monkeypatch.setattr("socket.socket", MySocket)
        sock = socket.socket()

        self.serv.clients.append(sock)
        assert self.serv.read_requests(self.serv.clients)[sock]['message'] == 'Hello!'

        self.serv.clients.remove(sock)
        assert self.serv.read_requests(self.serv.clients) == {}

    def test_write_responses(self, monkeypatch):
        monkeypatch.setattr("socket.socket", MySocket)
        requests = {}
        sock_r = socket.socket()  # сокет для словаря requests

        requests[sock_r] = JIMMsg('msg', 'Hello!').msg
        sock_w = socket.socket()  # сокет для приема сообщений
        self.serv.clients.append(sock_w)
        assert self.serv.write_responses(requests, self.serv.clients) == len(requests[sock_r])

        requests[sock_r] = JIMMsg('presence').msg
        with raises(Exception):
            self.serv.write_responses(requests, self.serv.clients)

        requests = {}
        assert self.serv.write_responses(requests, self.serv.clients) == len('')

        requests[sock_r] = JIMMsg('msg', 'Hello!').msg
        self.serv.clients.remove(sock_w)
        assert self.serv.write_responses(requests, self.serv.clients) == len('')
