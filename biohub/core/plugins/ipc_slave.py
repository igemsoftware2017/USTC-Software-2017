import os
import time
import queue
import socket
import select
import logging
import threading

import msgpack
from django.core.signals import Signal

logger = logging.getLogger('biohub.core.plugins.ipc_slave')
ipc_data_received = Signal(providing_args=['data'])


class Bridge:

    def __init__(self):
        self.__terminated = False
        self.__thread_object = None
        self.__socket_object = None
        self.__registered = False
        self.__message_queue = queue.Queue()

    @classmethod
    def __new__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(Bridge, cls).__new__(*args, **kwargs)

            return cls.__instance

    def send(self, data):
        self.__message_queue.put(msgpack.packb(data))

    def __terminate(self, *args, **kwargs):
        self.__terminated = True

    def register(self):
        if 'IPC' not in os.environ or self.__registered:
            return

        try:
            import uwsgi
            import uwsgidecorators
        except ModuleNotFoundError:
            no_uwsgi = True
        else:
            no_uwsgi = False

        if no_uwsgi:
            import atexit
            import signal
            from channels.signals import worker_process_ready

            atexit.register(self.__terminate)

            worker_process_ready.connect(self.__channel_worker_start_thread)

            signal.signal(signal.SIGTERM, self.__terminate)
            signal.signal(signal.SIGINT, self.__terminate)
        else:
            uwsgi.atexit = self.__terminate

            @uwsgidecorators.postfork
            def postfork_handler():
                self.__start_thread()

        self.__registered = True

    def __start_thread(self):

        if self.__thread_object and self.__thread_object.is_alive():
            return

        self.__thread_object = threading.Thread(target=self.__target)
        self.__thread_object.start()

    def __channel_worker_start_thread(self, sender, **kw):
        self.__start_thread()

    def __dispatch(self, data):
        ipc_data_received.send(self, data=data)

    def __target(self):

        self.__socket_object = None

        while True:

            if self.__terminated:
                break

            if self.__socket_object is None:
                self.__socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    self.__socket_object.connect(('localhost', 4869))
                except socket.error as exc:
                    logging.warn('Error while establishing IPC connection {}.'.format(exc))
                    self.__socket_object = None
                    time.sleep(3)
                    continue

            readable, writable, __ = select.select([self.__socket_object], [self.__socket_object], [], 5)

            if self.__terminated:
                break

            if readable:

                data = self.__socket_object.recv(1024)

                if not data:
                    self.__socket_object.close()
                    self.__socket_object = None
                    continue

                try:
                    if data.endswith(b'\r\n'):
                        data = data[:-2]
                    unpacked_data = msgpack.unpackb(data)
                except (msgpack.exceptions.UnpackException, msgpack.exceptions.ExtraData):
                    continue

                self.__dispatch(unpacked_data)

            if writable:
                try:
                    data = self.__message_queue.get_nowait()
                except queue.Empty:
                    continue

                self.__socket_object.send(data)


bridge = Bridge()

__all__ = ['bridge', 'ipc_data_received']
