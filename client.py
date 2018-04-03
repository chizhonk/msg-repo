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
import sys
from PyQt5.QtWidgets import QApplication, QWidget, qApp
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QThread, QEvent
import chatform
import addcontact
import delcontact
from threading import Thread
import time


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


class ClientHandler():
    ''' Базовый класс для работы с сокетом
    '''

    @log
    def __init__(self, client):
        self.client = client
        self.is_alive = False

    @log
    def __call__(self):
        ''' Класс-наследник должен выставить флаг is_alive = True '''
        raise NotImplemented

    @log
    def stop(self):
        self.is_alive = False


class ConsoleHandler(ClientHandler):
    ''' Обработчик ввода из консоли
    '''

    def __call__(self):
        while True:
            msg = input('Ваше сообщение: ')
            self.client.send_message(self.client.create_chat_message(msg))


class Receiver(ClientHandler):
    ''' Класс-получатель информации из сокета
    '''

    def __call__(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            response = self.client.get_message()
            if response['message']:
                print(response['message'])
            else:
                pass


class ContactList:
    @log
    def __init__(self, client):
        self.client = client

    @log
    def get_client_contacts(self):
        get_contacts_msg = JIMMsg(action='get_contacts').msg
        utils.send_message(self.client.s, get_contacts_msg)
        accept = utils.get_message(self.client.s)
        contacts = utils.get_message(self.client.s)['message']
        # if accept['quantity']:
        #    print('Ваши контакты: ')
        #    for i in range(accept['quantity']):
        #        print(utils.get_message(self.client.s)['user']['account_name'])
        return contacts

    @log
    def add_contact(self, contact_username):
        add_contact_msg = JIMMsg(action='add_contact', login=contact_username).msg
        #print(add_contact_msg)
        utils.send_message(self.client.s, add_contact_msg)
        #resp = utils.get_message(self.client.s)
        #return resp

    @log
    def del_contact(self, contact_username):
        del_contact_msg = JIMMsg(action='del_contact', login=contact_username).msg
        #print(del_contact_msg)
        utils.send_message(self.client.s, del_contact_msg)
        #resp = utils.get_message(self.client.s)
        #return resp


class User:
    @log
    def __init__(self, username, password=None):
        self.username = username
        self.password = password


class MsgTCPClient:
    @log
    def __init__(self, type, address=None):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.type = type
        if address: # для возможности тестирования без подключения к серверу
            self.s.connect(address)
        # self.login = ''
        self.user = User(None)

    @log
    def create_presence_message(self):
        """ Создает словарь/json presence-сообщения.

        :return: словарь/json presence-сообщения
        """
        return JIMMsg(action='presence', login=self.user.username).msg

    @log
    def create_chat_message(self, message):
        """ Создает словарь/json сообщения для последующей отправки в чат.

        :param message: сообщение для заполнения поля message в json
        :return: словарь/json сообщения
        """
        #print('**' + message + '**')
        return JIMMsg(action='msg', message=message).msg

    @log
    def send_message(self, jsonmsg, group=None):
        """ Отправляет сообщения на сервер.

        :param jsonmsg: отправляемое сообщение
        :return: длина отправленного сообщения (для тестирования)
        """
        utils.send_message(self.s, jsonmsg, group)
        return len(jsonmsg)

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
        login = input('Ваш логин (латиницей): ')
        self.user = User(username=login)

        self.send_message(self.create_presence_message())
        response = self.get_message()
        print(self.resp_code_into_text(response))

        #contact_list = ContactList(self)
        #print(contact_list.get_client_contacts())

        app = QApplication(sys.argv)
        window = MyWindow(self)
        window.show()
        sys.exit(app.exec_())

        """
        if self.type == 'r':
            while True:
                response = self.get_message()
                print(response['message'])
        else:
            print('Возможные действия:')
            print('- "add"  - добавить контакт')
            print('- "msg"  - ввести сообщение')
            print('- "exit" - выйти из программы')
            while True:
                action = input('Выберите действие: ')
                if action == 'add':
                    login = input('Введите логин добавляемого контакта: ')
                    contact_list.add_contact(login)
                    pass
                elif action == 'msg':
                    msg = input('Ваше сообщение: ')
                    if msg == 'exit':
                        break
                    else:
                        self.send_message(self.create_chat_message(msg))
                elif action == 'exit':
                    print('Выход из программы!')
                    break
                else:
                    print('Выбрано неизвестное действие. Попробуйте еще раз!')
        

        listener = Receiver(self)
        th_listen = Thread(target=listener)
        th_listen.daemon = True

        sender = ConsoleHandler(self)
        th_sender = Thread(target=sender)
        th_sender.daemon = True

        th_listen.start()
        th_sender.start()

        th_listen.join()
        th_sender.join()

#        while True:
#            if not th_listen.is_alive:
#                break
#            if not th_sender.is_alive:
#                break

        self.s.close()
        """


class ReceiveHandler(QObject):
    ''' Обработчик входящего сетевого соединения
    '''
    gotData = pyqtSignal(str)

    @log
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.client.s.settimeout(0.2)

    @log
    def poll(self):
        self.is_active = True
        while self.is_active:
            try:
                response = self.client.get_message()
                if response == b'':
                    print('Получено пустое соообщение!')
                    break
                elif 'message' in response.keys():
                    self.gotData.emit(' >> ' + response['message'])
                elif 'response' in response.keys():
                    if response['response'] == 500:
                        print('contact was not added as it does not exist')
            except OSError as e:
                pass  # timeout вышел
        print('receiver successfully finished')


class MyWindow(QWidget):

    sentData = pyqtSignal(str)
    sendMsg = pyqtSignal(int)
    updateCL = pyqtSignal(int)

    @log
    def __init__(self, client, parent=None):
        QWidget.__init__(self, parent)
        self.ui = chatform.Ui_Form()
        self.ui.setupUi(self)

        self.receiver = None
        self.thread = None
        self.clnt = client
        self.is_active = False

        self.contacts = ContactList(self.clnt).get_client_contacts()
        self.updateCL.connect(self.show_contact_list)

        #self.show_contact_list()
        self.ui.pushAdd.clicked.connect(self.show_add_contact_form)
        self.ui.pushDelete.clicked.connect(self.show_del_contact_form)

        self.show_contact_list()
        self.start_chat()

    @log
    def closeEvent(self, event):
        print('window closed')
        self.receiver.is_active = False
        self.thread.quit()
        self.thread.wait()

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            self.sendMsg.emit(0)

    @log
    @pyqtSlot(str)
    def update_chat(self, data):
        msg = str(time.ctime()) + data
        self.ui.textBrowser.append(msg)

    @log
    def start_chat(self):
        self.is_active = True

        self.receiver = ReceiveHandler(self.clnt)
        self.receiver.gotData.connect(self.update_chat)
        self.sentData.connect(self.update_chat)

        # Создание потока и помещение объекта-получателя в этот поток
        self.thread = QThread(self)
        self.receiver.moveToThread(self.thread)

        # ---------- Важная часть - связывание сигналов и слотов ----------
        # При запуске потока будет вызван метод poll получателя
        self.thread.started.connect(self.receiver.poll)

        # Отправка сообщения
        self.ui.pushSend.clicked.connect(self.send_msg_to_socket)
        self.sendMsg.connect(self.send_msg_to_socket)

        # Запуск потока
        self.thread.start()

    def send_msg_to_socket(self):
        text = self.ui.lineEdit.text()
        self.clnt.send_message(self.clnt.create_chat_message(text))
        self.sentData.emit(' << ' + text)
        #self.ui.textBrowser.append(self.clnt.user.username + ': ' + text)
        self.ui.lineEdit.clear()
        return text

    def show_contact_list(self):
        self.ui.listWidget.addItems(self.contacts)

    def show_add_contact_form(self):
        self.add_contact_form = AddContactForm(client=self.clnt, window=self)
        self.add_contact_form.show()

    def show_del_contact_form(self):
        self.del_contact_form = DelContactForm(client=self.clnt, window=self)
        self.del_contact_form.show()


class AddContactForm(QWidget):
    @log
    def __init__(self, client, window, parent=None):
        QWidget.__init__(self, parent)
        self.ui = addcontact.Ui_Form()
        self.ui.setupUi(self)
        self.clnt = client
        self.mainwindow = window
        self.ui.pushAdd.clicked.connect(self.add_contact_to_list)

    def add_contact_to_list(self):
        contact = self.ui.lineEdit.text()
        contact_list = ContactList(self.clnt)
        contact_list.add_contact(contact)
        self.ui.lineEdit.clear()
        # self.mainwindow.updateCL.emit(0)
        # self.mainwindow.ui.listWidget.addItem(contact)
        # self.mainwindow.ui.listWidget.addItems(ContactList(self.clnt).get_client_contacts())
        self.close()


class DelContactForm(QWidget):
    @log
    def __init__(self, client, window, parent=None):
        QWidget.__init__(self, parent)
        self.ui = delcontact.Ui_Form()
        self.ui.setupUi(self)
        self.clnt = client
        self.mainwindow = window
        self.ui.pushDelete.clicked.connect(self.del_contact_from_list)

    def del_contact_from_list(self):
        contact = self.ui.lineEdit.text()
        contact_list = ContactList(self.clnt)
        contact_list.del_contact(contact)
        self.ui.lineEdit.clear()
        # self.mainwindow.ui.listWidget.addItem(contact)
        # self.mainwindow.ui.listWidget.addItems(ContactList(self.clnt).get_client_contacts())
        self.close()

if __name__ == '__main__':
    # Создаем парсер, вычитываем аргументы командной строки, формируем адрес и тип клиента
    namespace = create_parser()
    address = (namespace.addr, int(namespace.port[1:-1]))
    type = client_type(namespace)

    # Создаем клиента и присоединяем его к чату
    clnt = MsgTCPClient(type, address)
    clnt.chat_client()









