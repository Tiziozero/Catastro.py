#!/usr/bin/env python3

import socket, threading, json, sys, datetime, struct
from comunication_enums import *
class NoDataException(Exception):
    def __init__(self, message):
        super().__init__(message)

class Client:
    def __init__(self, addr, port):
        try:
            self.addr, self.port = addr, port
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.room_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.addr, self.port))
            print(self.server.recv(1023).decode())
        except Exception as e:
            print(f"ERROR in setting up connection with server -> {e}")

    def get_rooms(self):
        bs = self.server.recv(8)
        if len(bs) == 0:
            print("connection closed")
        (length,) = struct.unpack('>Q', bs)
        # print(length)
        # print(f"data len: {bs}")
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += self.server.recv(
                4096 if to_read > 4096 else to_read)
        data = json.loads(data.decode())
        return data

    def run(self):
        rooms = self.get_rooms()
        print(f'[ {str("no."): <3}][ {"room name": <30} | {"description": <60} | {"open": >5} ]')
        for i, room in enumerate(rooms):
            string = f'[ {str(i): <3}][ {room["name"]: <30} | {room["description"]: <60} | {str(room["is_open"]): >5} ]'
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
                data = data.encode()
                length = struct.pack('>Q', len(data))
                
                room_conn.sendall(length)
                room_conn.sendall(data)
            except Exception as e:
                self.in_room = True
                print(f"ERROR in sending data -> {e}")
    
    def __del__(self):
        self.server.close()
        print("Closed connection to server")

if __name__ == '__main__':
    c = Client('localhost', 42069)
    # c.in_room('localhost', 44567)
    c.run()

