# Для корректной работы необходимо передавать в командной строке значение localhost.

from client import create_presence_message, srv_code_into_answer
import unittest


# Модульные тесты
class TestCreatePresenceMessage(unittest.TestCase):
    def test_create_presence_msg(self):
        msg = create_presence_message()
        self.assertEqual(msg['action'], 'presence')


class TestSrvCodeIntoAnswer(unittest.TestCase):
    def test_srv_code_200(self):
        answer = srv_code_into_answer(200)
        self.assertEqual(answer, 'OK')

    def test_srv_code_400(self):
        answer = srv_code_into_answer(400)
        self.assertEqual(answer, 'WRONG_REQUEST')

    def test_srv_code_101(self):
        with self.assertRaises(ValueError):
            srv_code_into_answer(101)


# Запустить тестирование
if __name__ == '__main__':
    unittest.main(argv=['addr'])
