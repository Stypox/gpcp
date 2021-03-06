from .utils.utils import sendAll, HEADER
import socket

class Client:

    def __init__(self, default_handler=None):
        """if default_handler is specified all responses to all requests will be handled by this callable"""

        if default_handler is not None:
            if not callable(default_handler):
                raise ValueError(f"invalid option '{default_handler}' for default_handler, must be callable")
        self.default_handler = default_handler

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        """connect to a server"""

        if not isinstance(host, str):
                raise ValueError(f"invalid option '{host}' for host, must be string")
        if not isinstance(port, int):
                raise ValueError(f"invalid option '{port}' for port, must be integer")

        self.socket.connect( (host, port) )

    def request(self, request, handler=None):
        """if handler is specified it will overwrite temporairly the default_handler"""

        if handler is not None and not callable(handler):
            raise ValueError(f"invalid option '{handler}' for handler, must be callable")

        sendAll(self.socket, request)

        head = self.socket.recv(HEADER) #read the header from a buffered request

        if head:
            byteCount = int(head)
            data = self.socket.recv(byteCount) #read the actual message of len head

            while len(data) < byteCount:
                data += self.socket.recv( byteCount - len(data) )

            if handler is not None:
                handler(self.socket, data)
            elif self.default_handler is not None:
                self.default_handler(self.socket, data)
            else:
                return data

    def closeConnection(self, mode = "RW"):
        """closes the connection to the server, RW = read and write, R = read, W = write"""
        if mode == "RW":
            self.socket.shutdown(socket.SHUT_RDWR)
        elif mode == "R":
            self.socket.shutdown(socket.SHUT_RD)
        elif mode == "W":
            self.socket.shutdown(socket.SHUT_WR)
        else:
            raise ValueError("close mode must be 'R' or 'W' or 'RW'")

        self.socket.close()

