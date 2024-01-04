#!/usr/bin/env python3

# Add create new room and add restoring rooms from databases in databases/rooms
# Fix up code cuz it's a mess

import socket, threading, json, sys, datetime, struct
from comunication_enums import *
class NoDataException(Exception):
    def __init__(self, message):
        super().__init__(message)

class Client:
    def __init__(self, addr, port):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.addr, self.port = addr, port
            self.room_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(self.server.recv(1023).decode())
        except Exception as e:
            print(f"ERROR in setting up connection with server -> {e}")

    def get_rooms(self):
        print("get start")
        bs = self.server.recv(8)
        if len(bs) == 0:
            print("connection closed")
        (length,) = struct.unpack('>Q', bs)
        print("get len", length)
        print(length)
        print(f"data len: {bs}")
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += self.server.recv(
                4096 if to_read > 4096 else to_read)
        data = json.loads(data.decode())
        print("get end")
        return data

    def run(self):
        while True:
            try:
                try:
                    print(self.addr)
                    print(self.port)
                    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.server.connect((self.addr, self.port))
                    print(self.server.recv(1024).decode())
                except Exception as e:
                    print(f"ERROR connecting to server -> {e}")
                print("[0] request room")
                print("[1] join room")
                print("[2] create room")
                print("[9] to quit")

                action = int(input("action: "))
                match action:
                    case 0: self.request_room()
                    case 1: self.join_room()
                    case 2: self.create_room()
                    case 9: return
                    case _: raise ValueError(f"{action} is not a valid action")
            except Exception as e:
                print(f"ERROR in client lobby -> {e}")

    def send_action(self, conn, action):
        conn.send(action)
    def join_room(self):
        self.send_action(self.server, Action.ACT_JOIN_ROOM)
        try:
            while True:
                try:
                    room_name = input("Room id: ")
                    self.server.send(room_name.encode())
                except Exception as e:
                    print(f"ERROR -> {e}")
                    continue

                if self.server.recv(1025) != Room_Enum.ROOM_FOUND:
                    print(f"room {room_name} not found.")
                    return Room_Enum.ROOM_FOUND

                if self.server.recv(512) == Password.PASS_NEEDED:
                    while True:
                        password = input("Password: ")
                        self.server.send(password.encode())

                        if self.server.recv(512) != Password.PASS_GUESSED:
                            self.server.send(Room.WRONG_PASSWORD)
                            print("Password is incorrect.")
                            continue
                        break
                    self.server.send(Room_Enum.REQUEST_ROOM)
                    data = json.loads(self.server.recv(4096))
                    print(f"Joining room {data}")
                    self.in_room(data["address"], data["port"])
                    return

        except Exception as e:
            print(f"ERROR in client join room request -> {e}")

    def request_room(self):
        self.send_action(self.server, Action.ACT_REQUEST_ROOM)
        rooms = self.get_rooms()
        print(f'[ {str("no."): <10} ][ {"room name temp pw": <30} | {"id": <60} | {"open": >5} ]')
        for i, room in enumerate(rooms):
            string = f'[ {str(i): >10} ][ {room["room_password"]: <30} | {room["room_id"]: <59} | {str(room["room_is_open"]): >5} ]'
            print(string)
            

    def in_room(self, room_addr, room_port):
        self.in_room = False
        self.server.close()
        try:
            self.room_server.connect((room_addr, room_port))
            print(f"received [[ {self.room_server.recv(1024).decode()} ]]")
            self.in_room = True

            r_t = threading.Thread(target=self.room_recv, args=(self.room_server,))
            s_t = threading.Thread(target=self.room_send, args=(self.room_server,))
            r_t.daemon = True
            s_t.daemon = True

            r_t.start()
            s_t.start()

            r_t.join()
            s_t.join()
            self.room_server.close()
            print("Both receiving thread and sending thread ended")

        except Exception as e:
            print(f"ERROR in connection with room at {room_addr}, {room_port} -> {e}")

    def room_recv(self, room_conn):
        while self.in_room:
            try:
                bs = room_conn.recv(8)
                if len(bs) == 0:
                    self.close_server_conection(a)
                    raise NoDataException("Division by zero is not allowed.")
                    break
                (length,) = struct.unpack('>Q', bs)
                # print(f"data len: {bs}")
                data = b''
                while len(data) < length:
                    to_read = length - len(data)
                    data += room_conn.recv(
                        4096 if to_read > 4096 else to_read)
                data = data.decode()
                print(data)
            except Exception as e:
                self.in_room = False
                print(f"ERROR in receiving data -> {e}")


    def room_send(self, room_conn):
        while self.in_room:
            try:
                data = input("[ message ]: ")
                if data == "QUIT!":
                    l = struct.pack('>Q', len(Room_Action.ROOM_ACT_QUIT))
                    room_conn.sendall(l)
                    room_conn.sendall(Room_Action.ROOM_ACT_QUIT)
                    self.in_room = False
                data = data.encode()
                length = struct.pack('>Q', len(data))
                room_conn.sendall(length)
                room_conn.sendall(data)
            except Exception as e:
                self.in_room = True
                print(f"ERROR in sending data -> {e}")
    
    def __del__(self):
        self.server.close()
        self.room_server.close()
        print("Closed connection to server")

if __name__ == '__main__':
    c = Client('localhost', 42069)
    # c.in_room('localhost', 44567)
    c.run()

