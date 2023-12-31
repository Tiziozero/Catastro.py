#!/usr/bin/env python3

# Add create new room and add restoring rooms from databases in databases/rooms
# Fix up code cuz it's a mess

import socket, threading, json, sys, datetime, struct, re, logging, pyfiglet, ast
from comunication_enums import *

def clear_screen():
    for _ in range(120):
        print()

def is_valid_password(password):
    if 8 < len(password) < 30:
        if re.search("[a-z]", password) and re.search("[A-Z]", password):
            if re.search("[0-9]", password):
                return True
    return False
class NoDataException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.timestamp = datetime.now()
        logging.error(f"{detetime.now()}: NoDataError: No data in file decypher.")

class Client:
    def __init__(self, addr, port):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.addr, self.port = addr, port
            self.room_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(self.server.recv(1023).decode('ascii', errors='replace'))
        except Exception as e:
            print(f"ERROR in setting up connection with server -> {e}")

    def get_rooms(self):
        bs = self.server.recv(8)
        if len(bs) == 0:
            print("connection closed")
        (length,) = struct.unpack('>Q', bs)
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += self.server.recv(
                4096 if to_read > 4096 else to_read)
        data = json.loads(data.decode('ascii', errors='replace'))
        return data

    def run(self):
        while True:
            try:
                try:
                    print(self.addr)
                    print(self.port)
                    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.server.connect((self.addr, self.port))
                    print(self.server.recv(1024).decode('ascii', errors='replace'))
                except Exception as e:
                    clear_screen()
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
                clear_screen()
                print(f"ERROR in client lobby -> {e}")

    def send_action(self, conn, action):
        conn.send(action)

    def join_room(self):
        self.send_action(self.server, Action.ACT_JOIN_ROOM)
        try:
            while True:
                try:
                    room_name = input("Room id: ")
                    self.server.send(room_name.encode('ascii'))
                except Exception as e:
                    print(f"ERROR -> {e}")
                    continue

                if self.server.recv(1025) != Room_Enum.ROOM_FOUND:
                    print(f"room {room_name} not found.")
                    return Room_Enum.ROOM_FOUND

                if self.server.recv(512) == Password.PASS_NEEDED:
                    while True:
                        password = input("Password: ")
                        if len(password) >= 40:
                            print("Password too long")
                            continue
                        self.server.send(password.encode('ascii'))
                        pass_guessed = self.server.recv(512)
                        print(pass_guessed)
                        if pass_guessed != Password.PASS_GUESSED:
                            self.server.send(Room_Enum.WRONG_PASSWORD)
                            print("Password is incorrect.")
                            continue
                        break
                self.server.send(Room_Enum.REQUEST_ROOM)
                bs = self.server.recv(8)
                (length, ) = struct.unpack(">Q", bs)
                data = b""
                while len(data) < length:
                    to_read = length - len(data)
                    data += self.server.recv(
                        4096 if to_read > 4096 else to_read)
                data = json.loads(data.decode('ascii', errors='replace'))
                self.in_room(data["address"], data["port"], data)
                return

        except Exception as e:
            print(f"ERROR in client join room request -> {e}")

    def request_room(self):
        clear_screen()
        self.send_action(self.server, Action.ACT_REQUEST_ROOM)
        rooms = self.get_rooms()

        print(f'┌{"":─<12}┬{"":─<32}┬{"":─<62}┬{"":─<8}┐')
        print(f'│ {"no.": <10} │ {"room name temp pw": <30} │ {"id": <60} │ {"open": >6} │')
        print(f'├{"":─<12}┼{"":─<32}┼{"":─<62}┼{"":─<8}┤')
        for i, room in enumerate(rooms):
            string = f'│ {str(i): >10} │ {room["room_password"]: <30} │ {room["room_id"]: <60} │ {str(room["room_is_open"]): >6} │'
            string2 = f'│ {"": >10} │ {room["room_description"]: <102} │'
            print(string)
            print(string2)
            print(f'├{"":─<12}┼{"":─<32}┼{"":─<62}┼{"":─<8}┤')
        print(f'└{"":─<12}┴{"":─<32}┴{"":─<62}┴{"":─<8}┘')
        input("Press ENTER to continue...")
        clear_screen()

    def create_room(self):
        clear_screen()
        room_data = {"room_name": "",
                     "room_description": "",
                     "room_is_open": 1,
                     "room_password": "",
                     "room_welcome_ascii_art": [],
                     "room_welcome_message": ""}
        while True:
            name = input("Name [ Max 25 characters ]:")
            name = name.strip()
            if name.strip() == "" or name.replace(" ", "") == "" or len(name) <= 2 or len(name) > 25:
                clear_screen()
                print("Invalid name [ Min 3 characters ]")
            else:
                room_data["room_name"] = name
                clear_screen()
                break
        while True:
            desc = input("description (optional) [ Max 55 characters ]:")
            desc = desc.strip()
            if len(desc) >= 56:
                clear_screen()
                print("Description too long")
            else:
                room_data["room_description"] = desc
                break
        clear_screen()
        while True:
            try:
                i_o = int(input("Open or Private [ 1 / 0 ]: "))
                print(i_o)
                if i_o not in [1, 0]:
                    clear_screen()
                    print("Value must be 1 or 0")
                    raise ValueError("Value must be 1 or 0")
                else:
                    room_data["room_is_open"] = i_o
                    break
            except Exception as e:
                clear_screen()
                print(f"ERROR in creating room -> {e}")
        if room_data["room_is_open"] == 0:
            clear_screen()
            while True:
                pw = input("Password [ Min 3 characters ]:")
                if is_valid_password(pw):
                    room_data["room_password"] = pw
                    break
                clear_screen()
                print("Invalid password. Password must contain:")
                print("    -Uppercase and Lowercase letters")
                print("    -Numbers")
        else: pass
        clear_screen()
        while True:
            welcome_message = input("Welcome message (optional): ")
            if welcome_message == "":
                break
            room_data["room_welcome_message"] = welcome_message
            break
        clear_screen()
        while True:
            path = input("Welcome ascii art (optional): ")
            if len(path) == 0:
                break
            else:
                try:
                    with open(path, "r") as f:
                        lines = f.readlines()
                        if 0 < len(lines) <= 120:
                            room_data["room_welcome_ascii_art"] = lines
                            break
                        else:
                            raise ValueError("File must contain 0 to 120 lines")
                except Exception as e:
                    clear_screen()
                    print(e)
                    continue

        print(room_data)
        input()
        clear_screen()
        self.server.sendall(Action.ACT_CREATE_ROOM)
        data = json.dumps(room_data).encode('ascii')
        self.server.sendall(struct.pack('>Q', len(data)))
        self.server.sendall(data)

            

    def in_room(self, room_addr, room_port, room_data):
        self.room_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("enter in room")
        self.is_in_room = False
        self.server.close()
        print(room_data)
        try:
            try:
                self.room_server.connect((room_addr, room_port))
                for _ in range(120):
                    print()
            except Exception as e:
                print(f"ERROR in connecting to {room_addr}, {room_port} -> {e}.")
            
             # with open("ascii_art.txt", "r") as f:
            #     data = f.readlines()
            #     for r in data:
            #         print(r, end=room_data["welcome art"]"")
            # print(room_data["welcome art"])

            try:
                ascii_art = ast.literal_eval(room_data["welcome art"])
                for r in ascii_art:
                    print(r, end="")
                print()
            except Exception as e:
                print("Invalid ascii art")


            message = self.room_server.recv(1024).decode('ascii', errors='replace')
            message = room_data["welcome message"]

            # print(f" ---[[ {message} ]]---")
            msg = message
            data = pyfiglet.figlet_format(msg)
            print(data)
            self.is_in_room = True

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
        finally:
            self.is_in_room = False

    def room_recv(self, room_conn):
        while self.is_in_room:
            try:
                bs = room_conn.recv(8)
                if len(bs) == 0:
                    raise NoDataException("no data received from server.")
                    self.is_in_room = False
                    break
                (length,) = struct.unpack('>Q', bs)
                # print(f"data len: {bs}")
                data = b''
                while len(data) < length:
                    to_read = length - len(data)
                    data += room_conn.recv(
                        4096 if to_read > 4096 else to_read)
                data = data.decode('ascii', errors='replace')
                print(data)
            except Exception as e:
                self.is_in_room = False
                print(f"ERROR in receiving data -> {e}")


    def room_send(self, room_conn):
        while self.is_in_room:
            try:
                data = input("[ message ]: ")
                if data == "QUIT!":
                    self.is_in_room = False
                    l = struct.pack('>Q', len(Room_Action.ROOM_ACT_QUIT))
                    room_conn.sendall(l)
                    room_conn.sendall(Room_Action.ROOM_ACT_QUIT)
                    self.is_in_room = False
                data = data.encode('ascii')
                length = struct.pack('>Q', len(data))
                room_conn.sendall(length)
                room_conn.sendall(data)
            except Exception as e:
                self.is_in_room = True
                print(f"ERROR in sending data -> {e}")
        clear_screen()
    
    def __del__(self):
        self.server.close()
        self.room_server.close()
        print("Closed connection to server")

if __name__ == '__main__':
    addrs = []
    with open("addr.txt", "r") as f:
        adrs = f.readlines()
        for a in adrs:
            a = a[:-1]
            print(a)
            addrs.append(a)

    ind = int(input("[0] localhost, [1] 139.162.200.195: "))
    for _ in range(120):
        print()

    c = Client(addrs[ind], 42039)
    c.run()
