import logging
from logging.handlers import TimedRotatingFileHandler


# Создаём именованные объекты-логгеры:
logger_general = logging.getLogger('msg')
logger_server = logging.getLogger('server')

# Создаём объект форматирования:
formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s")

# Возможные настройки для форматирования:
# -----------------------------------------------------------------------------
# | Формат         | Описание
# -----------------------------------------------------------------------------
# | %(name)s       | Имя регистратора.
# | %(levelno)s    | Числовой уровень важности.
# | %(levelname)s  | Символическое имя уровня важности.
# | %(pathname)s   | Путь к исходному файлу, откуда была выполнена запись в журнал.
# | %(filename)s   | Имя исходного файла, откуда была выполнена запись в журнал.
# | %(funcName)s   | Имя функции, выполнившей запись в журнал.
# | %(module)s     | Имя модуля, откуда была выполнена запись в журнал.
# | %(lineno)d     | Номер строки, откуда была выполнена запись в журнал.
# | %(created)f    | Время, когда была выполнена запись в журнал. Значением
# |                | должно быть число, такое как возвращаемое функцией time.time().
# | %(asctime)s    | Время в формате ASCII, когда была выполнена запись в журнал.
# | %(msecs)s      | Миллисекунда, когда была выполнена запись в журнал.
# | %(thread)d     | Числовой идентификатор потока выполнения.
# | %(threadName)s | Имя потока выполнения.
# | %(process)d    | Числовой идентификатор процесса.
# | %(message)s    | Текст журналируемого сообщения (определяется пользователем).
# -----------------------------------------------------------------------------

# Создаём файловый обработчик логгирования:
fh = logging.FileHandler("msg.log", encoding='utf-8')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)

# Создаем файловый обработчик с ежедневной ротацией лог-файлов (для сервера):
trfh = TimedRotatingFileHandler("server.log", when='midnight', encoding='utf-8')
trfh.setFormatter(formatter)
trfh.setLevel(logging.DEBUG)

# Добавляем в логгеры обработчики событий и устанавливаем уровень логгирования:
logger_general.addHandler(fh)
logger_general.setLevel(logging.DEBUG)
logger_server.addHandler(trfh)
logger_server.setLevel(logging.DEBUG)

# Возможные уровни логгирования:
# -----------------------------------------------------------------------------
# | Уровень важности | Использование
# -----------------------------------------------------------------------------
# | CRITICAL         | log.critical(fmt [, *args [, exc_info [, extra]]])
# | ERROR            | log.error(fmt [, *args [, exc_info [, extra]]])
# | WARNING          | log.warning(fmt [, *args [, exc_info [, extra]]])
# | INFO             | log.info(fmt [, *args [, exc_info [, extra]]])
# | DEBUG            | log.debug(fmt [, *args [, exc_info [, extra]]])
# -----------------------------------------------------------------------------


if __name__ == '__main__':
    # Создаём потоковый обработчик логгирования (по умолчанию sys.stderr):
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger_general.addHandler(console)
    # В логгирование передаем имя текущей функции и имя вызвавшей функции
    logger_general.info('Тестовый запуск логгирования')
