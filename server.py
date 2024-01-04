#!/usr/bin/env python3

import socket, threading, json, sys, datetime, random, string, uuid, struct
import sqlite3 as sql
from comunication_enums import *
from room import Room
from user import User

def get_room(room_id):
    with sql.connect("databases/server/rooms.db") as conn:
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
            data = c.fetchall()
            print(data)
            for d in data[0]:
                print(d)
            return data[0]
        except Exception as e:
            print("ERROR in searching for database for room_id {room_id} -> {e}")
            return None


def create_room(user):
    data = json.loads(user.a.recv(1024).decode())

def get_password(user, rooms):
    print("room is closed")
    user.a.send(Password.PASS_NEEDED)
    while True:
        print(rooms[8])
        password = user.a.recv(2048).decode()
        print(password)
        if password != rooms[8]:
            print("Wrong password")
            user.a.sendall(Password.PASS_NOT_GUESSED)
        elif password == rooms[8]:
            print("Password guessed")
            user.a.sendall(Password.PASS_GUESSED)
            return True

def join_room(user):
    while True:
        room_id = user.a.recv(1024).decode()
        print(room_id)
        rooms = get_room(room_id)
        if rooms != None:
            user.a.send(Room_Enum.ROOM_FOUND)
            print(rooms[7])
            if rooms[7] == 0:
                if get_password(user, rooms):
                    if user.a.recv(1024) == Room_Enum.REQUEST_ROOM:
                        json_data = {"address": rooms[4], "port": int(rooms[5])}
                        user.a.send(json.dumps(json_data).encode())
        else:
            user.a.send(Room_Enum.ROOM_NOT_FOUND)
            continue
    
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
            r["room_id"] = row[1]
            r["room_name"] = row[2]
            r["room_description"] = row[3]
            r["room_address"] = row[4]
            r["room_port"] = row[5]
            r["room_users"] = row[6]
            r["room_is_open"] = row[7]
            r["room_password"] = row[8]
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
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_id TEXT NOT NULL UNIQUE,
                        room_name TEXT NOT NULL,
                        room_description TEXT,
                        room_address TEXT NOT NULL,
                        room_port TEXT NOT NULL,
                        room_users INTEGER,
                        room_is_open BOOLEAN,
                        room_password TEXT,
                        room_db_name TEXT,
                        room_is_on BOOEAN
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
                    self.rooms.append(Room('localhost', "room null", "room null", is_open=False, r_password='pasta', MAKE_NEW=True))
            except Exception as e:
                print(f"ERROR in creating room null -> {e}")
                sys.exit()
                return
            print("made database rooms")
            self.server_on = True

        except Exception as e:
            print(f"ERROR in server setup -> {e}")

    def run(self):
        while self.server_on:
            try:
                a, p = self.server.accept()
                a.send(b"Hello client!")
                u = User(a)
                user_thread = threading.Thread(target=self.handle_user, args=(u,))
                user_thread.daemon = True
                user_thread.start()
            except KeyboardInterrupt:
                print(f"KI. closing server accept method.")
                self.server_on = False
                break
            except Exception as e:
                print(f"ERROR in server run -> {e}")

    def handle_user(self, user):
        while self.server_on:
            try:
                action = user.a.recv(256)
                if action == Action.ACT_BLANK:
                    print("Received blank from user. Disconnecting.")
                    break
                print(action)
                match action:
                    case Action.ACT_REQUEST_ROOM: send_db(user, "databases/server/rooms.db", "rooms")
                    case Action.ACT_JOIN_ROOM: join_room(user)
                    case Action.ACT_CREATE_ROOM: create_room(user)
                    case _: print(f"Unrecognised action: {action}")
            except Exception as e:
                print(f"ERROR in client handle thread -> {e}")

if __name__ == '__main__':
    s = Server('localhost', 42069)
    s.run()
