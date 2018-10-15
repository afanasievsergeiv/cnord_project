# -*- coding: utf-8 -*-
import logging
from tornado import gen
from tornado.options import options
from tornado.ioloop import IOLoop
from tornado.tcpclient import TCPClient
from settings import LISTENER__PORT, ENCODING


class ClientListener:
 
    __clients = set()

    def __init__(self, stream):
        self.stream = stream

    @staticmethod
    @gen.coroutine
    def run_client():
        stream = yield TCPClient().connect('127.0.0.1', LISTENER__PORT)
        try:
            while True:
                reply = yield stream.read_until(b"\r\n")
                reply = reply.decode(ENCODING).rstrip('\r\n')
                logging.info('Response from server: %s' % reply)
        except KeyboardInterrupt:
            stream.close()


if __name__ == '__main__':
    options.parse_command_line()
    IOLoop.instance().run_sync(ClientListener.run_client)
