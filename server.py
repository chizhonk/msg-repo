# Программа сервера с функциями:
# 1) принять сообщение клиента,
# 2) сформировать ответ клиенту,
# 3) отправить ответ клиенту.
#
# Параметры командной строки: client.py -p <port> -a <host>

from socket import *
import argparse
import time
from jim import utils


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


# Создание сокета TCP
s = socket(AF_INET, SOCK_STREAM)

# Присвоение порта (по умолчанию - 7777)
parser = create_parser()
namespace = parser.parse_args()
s.bind((namespace.a, int(namespace.p)))

# Переход в режим ожидания запросов (одновременное обслуживание не более 5 запросов)
s.listen(5)


while True:
    # Принятие запроса на соединение
    client, addr = s.accept()
    print("Получен запрос на соединение от %s" % str(addr))

    # Принятие сообщения клиента
    received_msg = utils.get_message(client)

    # Формирование ответа клиенту
    answer = create_answer(received_msg)

    # Отправка ответа клиенту
    utils.send_message(client, answer)
    client.close()


