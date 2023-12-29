#!/usr/bin/env python3

import socket, threading, json, sys, datetime, random, string
import sqlite3 as sql
from comunication_enums import *

def random_16_letter_string_generator():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

print(random_16_letter_string_generator())
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
        except Exception as e:
            print(f"ERROR in server database initialisation -> {e}")
        try:
            self.s.bind((self.addr, self.port))
            self.s.listen()
        except Exception as e:
            print(f"ERROR in server initialisation -> {e}")

    def user_authentication(self, data) -> bytes:
        return Auth_Enums.AUTH_NO_SUCH_USER

    def client_lobby(self, c):
        pass

    def run(self):
        while True:
            try:
                a, p = self.s.accept()
                print(f"Accepted connection from {a}, at port{p}")
                data = json.loads(a.recv(1024).decode())
                print(data)
                auth = self.user_authentication(data)
                if auth == Auth_Enums.AUTH_OK:
                    c = User(a, p, data)
                    th = threading.Thread(target=self.client_lobby, args=(c,))
                    th.daemon = True
                    th.start()
                else:
                    # print("sending authentication")
                    print(f"sending authentication: {auth}")
                    a.send(auth)
            except Exception as e:
                print(f"ERROR in server client acceptance -> {e}")

class User:
    def __init__(self, a, p, data):
        self.addr = a
        self.port = p
        self.user_name = data["user_name"]
        self.user_id = data["user_id"]
    def __del__(self):
        print(f"Deconstructed User with User ID: {self.user_id}.")

if __name__ == '__main__':
    s = Server('localhost', 42069)
    s.run()
