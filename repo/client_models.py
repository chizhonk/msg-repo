import datetime
import os
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class ClientContact(Base):
    """Связка контакт-клиент для хранения списка контактов"""
    # Название таблицы
    __tablename__ = 'ClientContact'
    # Первичный ключ
    ClientContactId = Column(Integer, primary_key=True)
    # id клиента
    ClientId = Column(Integer, ForeignKey('Client.ClientId'))
    # id контакта клиента
    ContactId = Column(Integer, ForeignKey('Client.ClientId'))

    def __init__(self, client_id, contact_id):
        self.ClientId = client_id
        self.ContactId = contact_id


class Client(Base):
    """Клиент"""
    # Название таблицы
    __tablename__ = 'Client'
    # Первичный ключ
    ClientId = Column(Integer, primary_key=True)
    # Имя клиента
    Name = Column(String, unique=True)
    # Информация не обязательное поле
    Info = Column(String, nullable=True)

    def __init__(self, name, info=None):
        self.Name = name
        if info:
            self.Info = info

    def __repr__(self):
        return "<Client ('%s')>" % self.Name

    def __eq__(self, other):
        # Клиенты равны если равны их имена
        return self.Name == other.Name


class MsgHistory(Base):
    """История сообщений клиента"""
    __tablename__ = 'MsgHistory'
    # Первичный ключ
    MsgHistoryId = Column(Integer, primary_key=True)
    # id клиента
    ClientId = Column(Integer, ForeignKey('Client.ClientId'))
    # Сообщение клиента
    Message = Column(String, nullable=False)
    # Время сообщения
    MsgTime = Column(DateTime, nullable=False)

    def __init__(self, client_id, message, msg_time):
        self.ClientId = client_id
        self.Message = message
        self.MsgTime = msg_time

