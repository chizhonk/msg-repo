# Перед запуском теста необходимо закомментрировать код client.py начиная с s = socket(AF_INET, SOCK_STREAM).

from pytest import raises
from client import create_presence_message, srv_code_into_answer

# Модульные тесты
def test_create_presence_msg():
    assert create_presence_message()['action'] == 'presence'

def test_srv_code_into_answer():
    with raises(ValueError):
        srv_code_into_answer(101)
    assert srv_code_into_answer(200) == 'OK'
    assert srv_code_into_answer(400) == 'WRONG_REQUEST'
