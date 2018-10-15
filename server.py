# -*- coding: utf-8 -*-
import logging
from tornado.options import options
from tornado import gen
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from tornado.netutil import bind_sockets
from client_listener import ClientListener
from client_source import ClientSource
from settings import SOURCE_PORT, LISTENER__PORT, ENCODING, SOURCES_LIST, MESSAGE_MAX_SIZE, STATUS_VALUES, HEADER_SERVER_RESPONSE
from message import Message
from tornado.iostream import StreamClosedError
from datetime import datetime


class TcpServer(TCPServer):

    # TODO: __slots__

    __sources = set()
    __clients = set()

    @gen.coroutine
    def handle_stream(self, stream, address):
        """Установка соединения от слушателей и источников и 'переписка' c ними"""
        port = stream.fileno().getsockname()[1]
        if port == SOURCE_PORT:
            logging.info('New source')
            new_source = ClientSource(stream)
            new_source.field = []
            self.__sources.add(new_source)
            try:
                while True:
                    try:
                        new_message = yield stream.read_bytes(MESSAGE_MAX_SIZE)
                        source_message = Message(new_message)
                        unpacked_message = source_message.parse_source_msg()
                    except Exception as ex:
                        # TODO: выяснить какие эксепшены могут быть и перехватывать, чтобы убрать проверку на исключ
                        # TODO: понизить вложенность
                        if ex.__class__.__name__ != 'StreamClosedError':
                            logging.info('Unable to unpack source message')
                            answer = {
                                'header': HEADER_SERVER_RESPONSE['Error'],
                                'message_number': 0x00
                            }
                    else:
                        logging.info('New incoming message has been successfully unpacked')
                        logging.info('Unpacked message: %s', unpacked_message)
                        new_source.msg_number, new_source.id = unpacked_message[1], unpacked_message[2]
                        new_source.field, new_source.status = unpacked_message[5], STATUS_VALUES[unpacked_message[3]]
                        new_source.last_msg_time = datetime.now()
                        answer = {
                            'header': HEADER_SERVER_RESPONSE['Success'],
                            'message_number': unpacked_message[1]
                        }
                        listener_msg = source_message.prepare_listener_msg(unpacked_message[2], unpacked_message[5])
                        for item in self.__clients:
                            yield item.stream.write(listener_msg.encode(ENCODING))
                    finally:
                        s_m = Message(answer)
                        server_msg = s_m.prepare_server_msg()
                        yield stream.write(server_msg)
            except StreamClosedError:
                self.__sources.remove(new_source)
                logging.info('Source has left')
        elif port == LISTENER__PORT:
            try:
                logging.info('New client')
                new_client = ClientListener(stream)
                stream.set_close_callback(self.close_client)
                self.__clients.add(new_client)
                sources_info = self.response_to_listener()
                yield stream.write(sources_info.encode(ENCODING))

            except StreamClosedError:
                logging.info('Client has left')
                self.__clients.remove(new_client)

    def run_server(self, source_socket, listener_socket):
        logging.info('Starting server')
        source, listener = bind_sockets(source_socket), bind_sockets(listener_socket)
        self.add_sockets(source)
        self.add_sockets(listener)
        IOLoop.current().start()

    def response_to_listener(self):
        """Сообщение сервера слушателю при подключении. Проверяем,
        было ли успешно отправлено по меньшей одно сообщение от источника.
        Если не было, то сведения об источнике не отправляем,
        в ином случае - отправляем.
        """
        # TODO: Возможно, стоит перенести в Message
        sources = ''.join(SOURCES_LIST.format(item.id, str(item.msg_number), str(item.status),
                                              str((datetime.now() - item.last_msg_time).seconds * 1000))
                          for item in self.__sources if 'id' in item.__dict__
                          )
        return sources or 'No connected sources\r\n'

    def close_client(self):
        """Callback на закрытие стрима слушателя"""
        stream_for_remove = None
        for item in self.__clients:
            if item.stream.closed():
                stream_for_remove = item
        if stream_for_remove:
            self.__clients.remove(stream_for_remove)
            logging.info('Client has left')


if __name__ == '__main__':
    options.parse_command_line()
    TcpServer().run_server(SOURCE_PORT, LISTENER__PORT)


