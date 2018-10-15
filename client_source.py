# -*- coding: utf-8 -*-
from tornado import gen
from tornado.options import options
from tornado.ioloop import IOLoop
from tornado.tcpclient import TCPClient
from message import Message
from settings import SOURCE_PORT, ENCODING, MESSAGE
import logging


class ClientSource:
 
    def __init__(self, stream):
        self.stream = stream

    @staticmethod
    @gen.coroutine
    def run_client():
        stream = yield TCPClient().connect('127.0.0.1', SOURCE_PORT)
        try:
            while True:
                input('<Press Enter To Send Message>').encode(ENCODING)
                initial_message = Message(MESSAGE)
                source_message = initial_message.prepare_source_message()
                yield stream.write(source_message)
                server_message = yield stream.read_bytes(4)
                msg = Message(server_message)
                unpacked_message = msg.parse_server_msg()
                logging.info('Response from server: %s', unpacked_message)
        except KeyboardInterrupt:
            stream.close()


if __name__ == '__main__':
    options.parse_command_line()
    IOLoop.instance().run_sync(ClientSource.run_client)
