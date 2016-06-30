import logging
import socket
from socket import error as socket_error

from ... exceptions import ConnectionError


logger = logging.getLogger(__name__)


class TCPConnection(object):
    """ A TCP socket connection
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self):
        self._connect()
        self._upgrade()
        self.connected = True

    def _connect(self):
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug(
            'establishing connection to %s:%s', self.host, self.port)

        try:
            _socket.connect((self.host, self.port))
        except socket_error as exc:
            if exc.errno == 61:
                logger.warning(
                    'unable to connect to %s:%s', self.host, self.port)
            logger.error(exc)
            raise
        else:
            logger.debug('connected to %s:%s', self.host, self.port)

        self.socket = _socket

    def _upgrade(self):
        pass

    def receive_message(self, bufsize=1024):
        try:
            bytes = self.socket.recv(bufsize)
        except socket.timeout as e:
            message = str(e)
            raise ConnectionError('timeout: "{}"'.format(message))

        return bytes

    def recv(self):
        received_bytes = bytearray()

        while True:
            bytes = self.receive_message()
            if not bytes:
                break

            received_bytes.extend(bytes)

        return received_bytes

    def send(self, message):
        self.socket.sendall(message)
