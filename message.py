# -*- coding: utf-8 -*-
from settings import SOURCE_FORMAT, FIELDS_FORMAT, ENCODING, HEADER_VALUES, STATUS_VALUES, SERVER_FORMAT, \
    LISTENER_CONNECT_MESSAGE, SOURCES_LIST
from struct import pack, unpack
from functools import reduce


class UnpackException(Exception):
    pass


class Message:

    # TODO: __slots__

    def __init__(self, message):
        self.message = message

    def prepare_source_message(self):
        """Упаковка сообщения от источника """
        message = self.message
        header = message.get('header')
        message_number = message.get('message_number')
        source_id = message.get('id')
        status = message.get('status')
        numfields = message.get('numfields')
        fields = message.get('fields')
        if None in (header, message_number, source_id, status, numfields, fields):
            raise UnpackException
        packed_field = b''.join([pack('!' + FIELDS_FORMAT, k, v) for k, v in fields])
        temp_list = [
            header,
            message_number,
            source_id,
            status,
            numfields,
            packed_field
        ]
        msg = pack(SOURCE_FORMAT[:-1], *temp_list)
        msg += pack(SOURCE_FORMAT[-1], self.message_xor(msg))
        return msg

    def parse_source_msg(self):
        """Распаковка сообщения от источника"""
        header, message_number, source_id, status, numfields, fields, xor = unpack(SOURCE_FORMAT, self.message)
        source_id = source_id.decode(ENCODING).rstrip('\x00')
        unpacked_fields = unpack('!' + FIELDS_FORMAT * numfields, fields)
        encoded_fields = []
        temp_str = ''
        if header not in HEADER_VALUES or status not in STATUS_VALUES:
            raise UnpackException
        for count, item in enumerate(unpacked_fields):
            if count % 2 == 0:
                temp_str = item.decode(ENCODING).rstrip('\x00')
            else:
                encoded_fields.append((temp_str, item, ))
        parsed_msg = (header, message_number, source_id, status, numfields, encoded_fields, xor, )
        self.parsed_msg = parsed_msg
        return parsed_msg

    def prepare_server_msg(self):
        """Подготовка ответа сервера источнику"""
        message = self.message
        header = message.get('header')
        message_number = message.get('message_number')
        packed_msg = pack(SERVER_FORMAT[:-1], header, message_number)
        packed_msg += pack(SERVER_FORMAT[-1], self.message_xor(packed_msg))
        return packed_msg

    def parse_server_msg(self):
        header, message_number, xor = unpack(SERVER_FORMAT, self.message)
        return (header, message_number, xor, )


    @staticmethod
    def prepare_listener_msg(source_id, fields):
        sources = ''.join(LISTENER_CONNECT_MESSAGE.format(source_id, x, str(y))
                          for x, y in fields)
        return sources

    @staticmethod
    def message_xor(msg):
        return reduce(lambda x, y: x ^ y, msg)
