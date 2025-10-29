import socket
import threading


class SafeSocket(socket.socket):
    def __init__(self, family=-1, type=-1, proto=-1, fileno=None):
        super().__init__(family, type, proto, fileno)
        self.lock = threading.RLock()
        self.recv = self.secure(self.recv)
        self.recv_into = self.secure(self.recv_into)
        self.recvfrom = self.secure(self.recvfrom)
        self.sendall = self.secure(self.sendall)
        self.send = self.secure(self.send)
        self.sendto = self.secure(self.sendto)
        self.sendfile = self.secure(self.sendfile)

    def secure(self, func):
        def wrapper(*args, **kwargs):
            self.lock.acquire()
            try:
                ret = func(*args, **kwargs)
            except:
                raise
            finally:
                self.lock.release()
            return ret

        return wrapper
