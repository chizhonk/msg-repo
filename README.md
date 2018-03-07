# Мессенджер

Репозиторий включает в себя клиент (client.py) и сервер (server.py).

Процедура запуска:
1) запустить сервер: python server.py
- по умолчанию слушает все доступные IP-адреса и использует порт 7777
- можно задать TCP-порт с помощью параметра -p <port>
- можно задать IP-адрес для прослушивания с помощью параметра -a <addr>
2) запустить клиент: python client.py localhost [7777]
- необходимо задать IP-адрес сервера первым аргументом командной строки
- можно задать TCP-порт сервера вторым аргументом командной строки (по умолчанию 7777)

Когда сервер поднят:
- при запуске клиента на сервер будет отправлено presence-сообщение (сообщение о присутствии клиента)
- сервер в ответ на presence-сообщение отправит клиенту сообщение 'OK'
- клиент примет сообщение 'OK' от сервера и закончит свою работу