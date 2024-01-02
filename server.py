#!/usr/bin/env python3

import socket, threading, json, sys, datetime, random, string, uuid, struct
import sqlite3 as sql
from comunication_enums import *
from room import Room
from user import User

def send_db(user, db_path, db_name):
    with sql.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(f"SELECT * FROM {db_name}")
        rooms = c.fetchall()
        data = []
        print(len(rooms))
        for row in rooms:
            r = {}
            r["id"] = row[0]
            r["primary_db_key_uuid"] = row[1]
            r["name"] = row[2]
            r["description"] = row[3]
            r["address"] = row[4]
            r["port"] = row[5]
            r["users"] = row[6]
            r["is_open"] = row[7]
            data.append(r)
        send_data = json.dumps(data)
        data = send_data.encode()
        print(len(data))
        length = struct.pack('>Q', len(data))
        user.a.sendall(length)
        user.a.sendall(data)

class Server:
    def __init__(self, addr, port):
        try:
            self.addr = addr
            self.port = port
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.addr, self.port))
            self.server.listen()
            self.rooms = []
            self.users = []
            try:
                conn = sql.connect("databases/server/rooms.db")
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS rooms (
                        room_id TEXT NOT NULL UNIQUE,
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_name TEXT NOT NULL,
                        room_description TEXT,
                        room_addr TEXT NOT NULL,
                        room_port TEXT NOT NULL,
                        users INTEGER,
                        is_open BOOLEAN
                    )
                ''')
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"ERROR in creating rooms database -> {e}")
                sys.exit()
                return
            try:
                if len(self.rooms) <= 0:
                    self.rooms.append(Room('localhost', "room null", "room null"))
            except Exception as e:
                print(f"ERROR in creating room null -> {e}")
                sys.exit()
                return
            print("made database rooms")

        except Exception as e:
            print(f"ERROR in server setup -> {e}")


    def run(self):
        while True:
            try:
                a, p = self.server.accept()
                a.send(b"Hello client!")
                u = User(a)
                user_thread = threading.Thread(target=self.handle_user, args=(u,))
                user_thread.daemon = True
                user_thread.start()
            except Exception as e:
                print(f"ERROR in server run -> {e}")

    def handle_user(self, user):
        # while True:
            try:
                send_db(user, "databases/server/rooms.db", "rooms")
                

            except Exception as e:
                print(f"ERROR in client handle thread -> {e}")

if __name__ == '__main__':
    s = Server('localhost', 42069)
    s.run()
