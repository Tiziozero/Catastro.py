#!/usr/bin/env python3

import socket, threading, json, sys, datetime, random, string, uuid
import sqlite3 as sql
from comunication_enums import *
from user import User

MAX_CONNECTIONS = 16
def random_16_letter_string_generator():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))


class Server:
    def __init__(self, addr, port):
        self.addr, self.port = addr, port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.room_db = sql.connect('databases/rooms/rooms.db')
            self.room_c = self.room_db.cursor()
            self.room_c.execute('''CREATE TABLE IF NOT EXISTS rooms (
                   id INTEGER PRIMARY KEY,
                   room_name TEXT,
                   room_id TEXT,
                   users INTEGERS,
                   active INTEGER,
                   room_address TEXT,
                   room_ip INTEGER,
                   deacription TEXT)''')
            self.room_db.commit()
            self.user_db = sql.connect('databases/users/users.db')
            self.user_c = self.user_db.cursor()
            self.user_c.execute('''CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY,
                   user_name TEXT,
                   user_id TEXT,
                   active INTEGER,
                   deacription TEXT)''')
            self.user_db.commit()
            self.room_db.close()
            self.user_db.close()

        except Exception as e:
            print(f"ERROR in server database initialisation -> {e}")
        try:
            self.s.bind((self.addr, self.port))
            self.s.listen()
        except Exception as e:
            print(f"ERROR in server connection initialisation -> {e}")

    def run(self):
        port = 1111
        user_addr = "localhost"
        while True:
            try:
                a, p = self.s.accept()
                data = json.dumps({"addr": 'localhost', "port": port}).encode()
                a.send(data)
                print(f"Accepted connection from {a}, at port{p}")
                u = User(a, self.s)
                client_thread = threading.Thread(target=self.lobby, args=(u,))
                client_thread.daemon = True
                client_thread.start()
                port += 1
            except Exception as e:
                print(f"ERROR in server connection initialisation -> {e}")

    def lobby(self, client: User):
        self.check_client_on(client)
        while True:
            try:
                action = client.recv()
                match action:
                    case Action.ACT_JOIN_ROOM: self.client_join_room(client)

            except Exception as e:
                print(f"ERROR in client action selection -> {e}")

    def check_client_on(self, client):
        check_client_thread = threading.Thread(target=self.is_socket_closed, args=(client,))
        check_client_thread.daemon = True
        check_client_thread.start()

    def is_socket_closed(self, client):
        while client.user_is_on:
            try:
                # this will try to read bytes without blocking and also without removing them from buffer (peek only)
                data = client.server_connection.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
                if len(data) == 0:
                    self.__del__()
                    client.user_is_on = False
                    print("recived empty data, closing")
                    break
            except BlockingIOError:
                continue
                # return False  # socket is open and reading from it would block
            except ConnectionResetError:
                client.__del__()
                client.user_is_on = False
                print("recived empty data, closing")
                break
                # return True  # socket was closed for some other reason
            except Exception as e:
                continue
                # return False


if __name__ == '__main__':
    s = Server('localhost', 42069)
    s.run()
