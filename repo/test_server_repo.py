from pytest import raises
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .server_models import Base, Client, ClientContact
from .server_repo import Repo
from .server_errors import ContactDoesNotExist


class TestRepo:
    def setup(self):
        """
        Тестировать можно 2-мя способами:
        1. Использовать существующую базу, для неё у нас уже есть session
        + не надо создавать новую базу
        - можем забыть что нибудь удалить
        2. Создать тестовую базу желательно в памяти
        + изоляция базы
        Поэтому выбираем 2-ой вариант
        :return:
        """
        # создаем тестовую базу и сессию для работы
        # создаем движок
        # база данных в оперативной памяти
        engine = create_engine('sqlite:///:memory:', echo=False)
        # Не забываем создать структуру базы данных
        Base.metadata.create_all(engine)
        # Создаем сессию для работы
        Session = sessionmaker(bind=engine)
        session = Session()
        # Рекомендуется брать 1 сессию и передавать параметром куда нам надо
        self.session = session
        # далее создаем тестовые объекты
        # создаем 3-х клиентов
        c1 = Client('Max')
        session.add(c1)
        c2 = Client('Leo')
        session.add(c2)
        c3 = Client('Kate')
        session.add(c3)

        # добавляем Max 2 контакта
        obj = ClientContact(1, 2)
        session.add(obj)
        obj = ClientContact(1, 3)
        session.add(obj)
        # добавляем Leo 1 контакт
        obj = ClientContact(2, 3)
        session.add(obj)
        # у Kate нету контактов

        # создаем репозиторий, передаем сессию
        self.repo = Repo(session)

    def test_get_client_by_username(self):
        """
        Важный метод всегда будем работать с именами пользователей
        :return: Client
        """
        leo = self.repo.get_client_by_username('Leo')
        assert leo.Name == 'Leo'
        # что будет если клиента нет
        n = self.repo.get_client_by_username('None')
        # вернется None
        assert n is None

    def test_client_exist(self):
        # такой есть
        assert self.repo.client_exists('Leo')
        # такого нету
        assert not self.repo.client_exists('None')

    def test_add_client(self):
        self.repo.add_client('New')
        assert self.repo.client_exists('New')

    def test_get_contacts(self):
        # возьмем контакты Kate
        contacts = self.repo.get_contacts('Kate')
        assert len(contacts) == 0
        # контакты Leo
        contacts = self.repo.get_contacts('Leo')
        assert len(contacts) == 1
        assert contacts[0].Name == 'Kate'
        # контакты Max
        contacts = self.repo.get_contacts('Max')
        assert len(contacts) == 2
        # контакты неизвестного человека
        contacts = self.repo.get_contacts('None')
        assert [] == contacts

    def test_add_del_contact(self):
        # создадим нового пользователя
        self.repo.add_client('New')
        # добавим ему контакт
        self.repo.add_contact('New', 'Kate')
        # проверим
        contacts = self.repo.get_contacts('New')
        assert len(contacts) == 1
        assert contacts[0].Name == 'Kate'
        # добавим ему контакт которого нет в базе
        # что должно произойти, ошибка или ничего? скорее всего ошибка такого контакта нет в базе
        with raises(ContactDoesNotExist):
            self.repo.add_contact('New', 'None')
        # удалим контакт которого у него нет
        with raises(ContactDoesNotExist):
            self.repo.del_contact('New', 'None')

        # что будет если добавить контакт клиенту которого нет в базе?
        # такое поведение не должно быть возможно впринципе, поэтому проверять пока не будем


    def teardown(self):
        # не забываем удалить тестовые объекты и откатить измененея
        self.session.rollback()
