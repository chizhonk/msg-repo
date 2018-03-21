from .server_models import Client, ClientContact, LogonHistory
from .server_errors import ContactDoesNotExist
import datetime


class Repo:
    """Серверное хранилище"""

    def __init__(self, session):
        """
        Запоминаем сессию, чтобы было удобно с ней работать
        :param session:
        """
        self.session = session

    def add_client(self, username, info=None):
        """Добавление клиента"""
        new_item = Client(username, info)
        self.session.add(new_item)
        self.session.commit()

    def client_exists(self, username):
        """Проверка, что клиент уже есть"""
        result = self.session.query(Client).filter(Client.Name == username).count() > 0
        return result

    def get_client_by_username(self, username):
        """Получение клиента по имени"""
        client = self.session.query(Client).filter(Client.Name == username).first()
        return client

    def add_contact(self, client_username, contact_username):
        """Добавление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = ClientContact(client_id=client.ClientId, contact_id=contact.ClientId)
                self.session.add(cc)
                self.session.commit()
                return 0
            else:
                # raise NoneClientError(client_username)
                return 1
        else:
            print('Контакт', contact_username, 'не существует и не будет добавлен пользователю', client_username)
            return 2
            # raise ContactDoesNotExist(contact_username)

    def del_contact(self, client_username, contact_username):
        """Удаление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = self.session.query(ClientContact).filter(
                    ClientContact.ClientId == client.ClientId).filter(
                    ClientContact.ContactId == contact.ClientId).first()
                self.session.delete(cc)
            else:
                # raise NoneClientError(client_username)
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def get_contacts(self, client_username):
        """Получение контактов клиента"""
        client = self.get_client_by_username(client_username)
        result = []
        if client:
            # Тут нету relationship поэтому берем запросом
            contacts_clients = self.session.query(ClientContact).filter(ClientContact.ClientId == client.ClientId)
            for contact_client in contacts_clients:
                contact = self.session.query(Client).filter(Client.ClientId == contact_client.ContactId).first()
                result.append(contact)
        return result

    def add_logon(self, client_username, client_ip):
        """Добавление записи с временем входа клиента"""
        client = self.get_client_by_username(client_username)
        if client:
            lh = LogonHistory(client_id=client.ClientId, logon_time=datetime.datetime.now(), client_ip=client_ip)
            self.session.add(lh)
            self.session.commit()
        else:
            pass

    def get_logon_history(self, username):
        """Получение истории входов клиента"""
        client = self.get_client_by_username(username)
        result = {}
        if client:
            logons = self.session.query(LogonHistory).filter(LogonHistory.ClientId == client.ClientId).all()
            for logon in logons:
                result[logon.LogonTime] = logon.ClientIP
                print(logon.LogonTime, logon.ClientIP)
        return result

