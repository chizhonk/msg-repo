from .server_errors import ContactDoesNotExist


def test_str():
    e = ContactDoesNotExist('None')
    assert str(e) == "Contact None does not exist"
