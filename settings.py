# -*- coding: utf-8 -*-
SOURCE_PORT = 8888
LISTENER__PORT = 8889
ENCODING = 'utf-8'
MESSAGE_MAX_SIZE = 3074
HEADER_VALUES = (0x01, )
HEADER_SERVER_RESPONSE = {'Success': 0x11, 'Error': 0x12}
STATUS_VALUES = {0x01: 'IDLE', 0x02: 'ACTIVE', 0x03: 'RECHARGE'}
MESSAGE = {
    'header': 0x01,
    'message_number': 9,
    'id': b'ay_017',
    'status': 0x02,
    'numfields': 6,
    'fields': [
        (b'first', 21),
        (b'second', 100),
        (b'third', 74),
        (b'fourth', 123),
        (b'unite', 41),
        (b'temp', 22),
    ]
}
SOURCE_FORMAT = "!Bh8sBB3060pB"
SERVER_FORMAT = "!BhB"
FIELDS_FORMAT = "8sI"
SOURCES_LIST = "[{0}] {1} | {2} | {3}\r\n"
LISTENER_CONNECT_MESSAGE = "[{0}] {1} | {2}\r\n"
