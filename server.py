#!/usr/bin/env python3

import socket, threading, json, sys, datetime, random, string, uuid
import sqlite3 as sql
from comunication_enums import *

def send_db(user, db_name):
    pass

class Server:
    def __init__(self, addr, port):
        try:
            self.addr = addr
            self.port = port
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.addr, self.port))
            self.server.listen()
            conn = sql.connect("databases/server/rooms.db")
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_name TEXT NOT NULL,
                    room_id TEXT NOT NULL UNIQUE,
                    capacity INTEGER,
                    room_type TEXT,
                    is_occupied BOOLEAN
                )
            ''')
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"ERROR in server setup -> {e}")

    def run(self):
        while True:
            try:
                a, p = self.server.accept()
                a.send(b"Hello client!")
                user_thread = threading.Thread(targer=self.handle_user, args=(a,))
                user_thread.daemon = True
                user_thread.start()
            except Exception as e:
                print(f"ERROR in server run -> {e}")

    def handle_user(self, user):
        while True:
            try:
                send_room(user, db)
                

            except Exception as e:
                print(f"ERROR in client handle thread -> {e}")

if __name__ == '__main__':
    s = Server('localhost', 42069)
    s.run()
