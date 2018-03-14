# Для корректной работы данного файла в командной строке аргументы не передаются.

from server import create_response_200, create_response_400, create_answer
import unittest


# Модульные тесты
class TestCreateResponse200(unittest.TestCase):
    def test_create_response_200(self):
        response = create_response_200()
        self.assertEqual(response['response'], 200)


class TestCreateResponse400(unittest.TestCase):
    def test_create_response_400(self):
        response = create_response_400()
        self.assertEqual(response['response'], 400)


class TestCreateAnswer(unittest.TestCase):
    def test_create_answer_presence(self):
        answer = create_answer({'action': 'presence'})
        self.assertEqual(answer['response'], 200)

    def test_create_answer_whatever(self):
        answer = create_answer({'action': 'whatever'})
        self.assertEqual(answer['response'], 400)


# Запустить тестирование
if __name__ == '__main__':
    unittest.main()
