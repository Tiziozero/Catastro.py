#!/usr/bin/env python3

import socket, threading, json, sys, datetime, random, string, uuid, struct
import sqlite3 as sql
from comunication_enums import *
from room import Room
from user import User

ROOMS_DATABASE_PATH = "databases/server/rooms.db"
RDP = ROOMS_DATABASE_PATH


def is_valid_password(password):
    if 8 < len(password) < 30:
        if re.search("[a-z]", password) and re.search("[A-Z]", password):
            if re.search("[0-9]", password):
                return True
    return False

def get_db_col_names(db_path, table_name):
    with sql.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(f"SELECT * from {table_name} LIMIT 0")
        col_names = [description[0] for description in c.description]
        # print(col_names)

def get_room(room_id):
    with sql.connect(RDP) as conn:
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
            data = c.fetchall()
            # print(data)
            return data[0]
        except Exception as e:
            print(f"ERROR in searching for database for room_id {room_id} -> {e}")
            return None

def create_room(server, user):
    data = json.loads(user.a.recv(1024).decode('ascii', errors='replace'))
    # to continue



def get_room_info(db_path, table_name, column_name, column_value):
    with sql.connect(db_path) as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name} WHERE {column_name} = ?"
        cursor.execute(query, (column_value,))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        # print(result)
        return result[0]

def get_password(user, rooms):
    print("room is closed")
    user.a.send(Password.PASS_NEEDED)
    while True:
        print("password:", rooms[7])
        password = user.a.recv(2048).decode('ascii', errors='replace')
        print(password)
        if password != rooms[7]:
            print("Wrong password")
            user.a.sendall(Password.PASS_NOT_GUESSED)
            print(user.a.recv(2048))
        elif password == rooms[7]:
            print("Password guessed")
            user.a.sendall(Password.PASS_GUESSED)
            return True

def join_room(user):
    while True:
        room_id = user.a.recv(1024).decode('ascii', errors='replace')
        print(room_id)
        print("calling get room")
        rooms = get_room(room_id)
        if rooms != None:
            user.a.send(Room_Enum.ROOM_FOUND)
            print("room is open:", rooms[6])
            if rooms[6] == 0:
                if get_password(user, rooms):
                    if user.a.recv(1024) == Room_Enum.REQUEST_ROOM:
                        json_data = {"address": rooms[4], "port": int(rooms[5])}
                        user.a.send(json.dumps(json_data).encode('ascii'))
            else:
                user.a.send(Password.PASS_NOT_NEEDED)
                if user.a.recv(1024) == Room_Enum.REQUEST_ROOM:
                    json_data = {"address": rooms[4], "port": int(rooms[5])}
                    user.a.send(json.dumps(json_data).encode('ascii'))

        else:
            user.a.send(Room_Enum.ROOM_NOT_FOUND)
            continue
    
def send_db(user, db_path, db_name):
    with sql.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(f"SELECT * FROM {db_name}")
        rooms = c.fetchall()
        data = []
        # print("length of rows in database to send:", len(rooms))
        for row in rooms:
            r = {}
            r["id"] = row[0]
            r["room_id"] = row[1]
            r["room_name"] = row[2]
            r["room_description"] = row[3]
            r["room_address"] = row[4]
            r["room_port"] = row[5]
            r["room_is_open"] = row[6]
            r["room_password"] = row[7]
            r["room_welcome_ascii_art"] = row[8]
            r["room_welcome_message"] = row[9]
            r["room_users"] = row[10]
            r["room_chat_db_name]"] = row[11]
            r["room_is_on"] = row[12]
            data.append(r)
        send_data = json.dumps(data)
        data = send_data.encode('ascii')
        # print("length of data:", len(data))
        length = struct.pack('>Q', len(data))
        user.a.sendall(length)
        user.a.sendall(data)

def get_whole_db(path, tname):
    with sql.connect(path) as db:
        c = db.cursor()
        c.execute(f"SELECT * FROM {tname}")
        data = c.fetchall()
        # for d in data: print(d)
        return data

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
                conn = sql.connect(RDP)
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS rooms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_id TEXT NOT NULL UNIQUE,
                        room_name TEXT NOT NULL,
                        room_description TEXT,
                        room_address TEXT NOT NULL,
                        room_port TEXT NOT NULL,
                        room_is_open BOOLEAN,
                        room_password TEXT,
                        room_welcome_ascii_art TEXT,
                        room_welcome_message TEXT,
                        room_users INTEGER,
                        room_chat_db_name TEXT,
                        room_is_on BOOLEAN
                    )
                ''')
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"ERROR in creating rooms database -> {e}")
                sys.exit()
                return
            print("made database rooms")
            try:
                room_data = {
                        "room_id": str(uuid.uuid4()),
                        "room_name": "room null",
                        "room_description": "description for room null",
                        "room_address": self.addr,
                        "room_port": 0,
                        "room_is_open": 0,
                        "room_password": "pasta",
                        "room_welcome_ascii_art": "ASCII welcome art",
                        "room_welcome_message": "Welcome to room null",
                        "room_users": 0,
                        "room_chat_db_name": "",
                        "room_is_on": True
                    }
                r = Room(room_data, True)
                self.rooms.append(r)
            except Exception as e:
                print(f"ERROR in creating room null -> {e}")
                sys.exit()
                return
            self.server_on = True
            get_db_col_names(RDP, "rooms")

        except Exception as e:
            print(f"ERROR in server setup -> {e}")

        self.load_rooms(RDP, "rooms")

    def load_rooms(self, db_path, table_name, col_name="room_id"):
        with sql.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(f"SELECT {col_name} FROM {table_name}")
            data = c.fetchall()
            # print(data)
            for d in data:
                room_data = get_room_info(db_path, table_name, col_name, d[0])
                print(room_data)
                r = Room(room_data, False)
                self.rooms.append(r)

    def run(self):
        while self.server_on:
            print("Server open for acceptions.")
            try:
                a, p = self.server.accept()
                print(f"Accepted connection from {a.getsockname()}")
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
                    case Action.ACT_REQUEST_ROOM: send_db(user, RDP, "rooms")
                    case Action.ACT_JOIN_ROOM: join_room(user)
                    case Action.ACT_CREATE_ROOM: create_room(self, user)
                    case _: print(f"Unrecognised action: {action}")
            except Exception as e:
                print(f"ERROR in user handle thread -> {e}")

if __name__ == '__main__':
    addrs = []
    with open("addr.txt", "r") as f:
        adrs = f.readlines()
        for a in adrs:
            a = a[:-1]
            print(a)
            addrs.append(a)

    ind = int(input("[0] localhost, [1] 139.162.200.195: "))
    s = Server(addrs[ind], 42039)
    s.run()
