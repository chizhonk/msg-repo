# Для корректной работы данного файла в командной строке аргументы не передаются.

import server
import doctest

nfail, ntests = doctest.testmod(server, verbose=True)
