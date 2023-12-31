import socket, json, threading
from comunication_enums import *

class User:
    def __init__(self, client_sock, server):
        self.clinet_sock = client_sock
        self.server_connection = server
        self.user_on = True

    def setup(self):
        try:
            return True
        except Exception as e:
            print(f"ERROR in user server initialisation -> {e}")
            return False


    def check_client_on(self):
        check_client_thread = threading.Thread(target=self.is_socket_closed)
        check_client_thread.daemon = True
        check_client_thread.start()

    def is_socket_closed(self) -> bool:
        while self.user_is_on:
            try:
                # this will try to read bytes without blocking and also without removing them from buffer (peek only)
                data = self.client_socket.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
                if len(data) == 0:
                    self.__del__()
                    self.user_is_on = False
                    print("recived empty data, closing")
                    break
            except BlockingIOError:
                continue
                # return False  # socket is open and reading from it would block
            except ConnectionResetError:
                self.__del__()
                self.user_is_on = False
                print("recived empty data, closing")
                break
                # return True  # socket was closed for some other reason
            except Exception as e:
                continue
                # return False

