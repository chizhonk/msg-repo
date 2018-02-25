# Для корректной работы необходимо передавать в командной строке значение localhost.

import client
import doctest

nfail, ntests = doctest.testmod(client, verbose=True)
