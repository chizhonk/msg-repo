# Перед запуском теста необходимо закомментрировать код client.py начиная с s = socket(AF_INET, SOCK_STREAM).

from server import create_response_200, create_response_400, create_answer


# Модульные тесты
def test_create_response_200():
    assert create_response_200()['response'] == 200

def test_create_response_400():
    assert create_response_400()['response'] == 400

def test_create_answer():
    assert create_answer({'action': 'presence'})['response'] == 200
    assert create_answer({'action': 'whatever'})['response'] == 400

