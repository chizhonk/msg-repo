# Для корректной работы данного файла в командной строке аргументы не передаются.
# Перед запуском данного файла необходимо задокументировать в server.py блок кода while True.

import server
import doctest

nfail, ntests = doctest.testmod(server, verbose=True)
