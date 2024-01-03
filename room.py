import socket, threading, uuid, struct, logging
import sqlite3 as sql
from user import User
class Room:
    def __init__(self, room_addr, room_name, room_description, room_id=None, room_port=0, is_open=True):
        self.addr = room_addr
        self.port = room_port
        self.room_name = room_name
        self.room_description = room_description
        self.room_id = room_id
        self.is_open = is_open
        self.users = []
        if not self.room_id:
            self.room_id = uuid.uuid4()
        print(f"port = {self.port}")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.addr, self.port))
        port = self.server.getsockname()
        print(f"Room under {self.room_id}: {port}")
        self.port = port[1]
        self.server.listen()
        try:
            with sql.connect(f"databases/rooms/{self.room_name}_{self.room_id}.db") as db_conn:
                c = db_conn.cursor()
                c.execute("""
                    CREATE TABLE IF NOT EXISTS chat (
                        id INTEGER PRIMARY KEY,
                        time TEXT,
                        user_addr TEXT,
                        message TEXT
                    )
                """)
                c.close()
        except Exception as e:
            print(f"ERROR in room {self.room_id} database setup -> {e}")
        self.add_room("databases/server/rooms.db",
                      self.room_name,
                      self.room_description,
                      self.addr, self.port,
                      self.room_id,
                      is_open=self.is_open)
        self.on = True

    def add_room(self, db_name, room_name, room_description, room_addr, room_port, room_id=None, users=0, is_open=True):
        try:
            with sql.connect(db_name) as conn:
                c = conn.cursor()
                if not room_id:
                    room_id = str(uuid.uuid4())
                room_id = str(room_id)
                c.execute('''
                    INSERT INTO rooms (room_id, room_name, room_description, room_address, room_port, room_users, room_is_open)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (room_id, room_name, room_description, room_addr,  room_port, users, is_open))
                conn.commit()
            return True
        except Exception as e:
            print(f"ERROR in creatin room {room_name} -> {e}")

    def accept(self):
        while self.on:
            try:
                a, p = self.server.accept()
                u = User(a)
                a.send(f"welcome in {self.room_name}".encode())
                self.handle_client(u)
            except Exception as e:
                print(f"ERROR in room {self.room_id} user acceptance -> {e}")
        

    def handle_client(self, u):
        self.users.append(u)
        client_recv_thread = threading.Thread(target=self.client_recv, args=(u,))
        client_recv_thread.daemon = True
        client_recv_thread.start()

    def client_recv(self, u):
        while self.on:
            try:
                bs = u.a.recv(8)
                if len(bs) == 0:
                    self.close_client_conection(u)
                    break
                (length,) = struct.unpack('>Q', bs)
                print(f"data len: {bs}")
                data = b''
                while len(data) < length:
                    to_read = length - len(data)
                    data += u.a.recv(
                        4096 if to_read > 4096 else to_read)
                data = data.decode()
                print(f"received {data}")
                self.send_data_to_all(u, data)
            except ValueError as e:
                print(f"ValueError in room {self.room_id} client receive method -> {e}")
            except Exception as e:
                print(f"Other error in room {self.room_id} client receive method -> {e}")
        print(f"Closed receiiving thread with {u.a}")

    def send_data_to_all(self, u, data):
        for user in self.users:
            if user != u:
                data = f"[ {u.name} ]::< {data} >"
                data = data.encode()
                length = struct.pack('>Q', len(data))
                try:
                    user.a.sendall(length)
                    user.a.sendall(data)
                except Exception as e:
                    print(f"ERROR in trying to send data to all ({user.a}) -> {e}")

    def close_client_conection(self, u):
        if u in self.users:
            self.users.remove(u)
            u.a.close()
            print(f"closed connection with {u.a}")
        for user in self.users:
            print(user)

    def close(self, error=None):
        for c in self.users:
            c.close()
        self.server.close()
        if error:
            print(f"Server closed with error -> {error}.")
        else:
            print("Server closed without any appearing errors.")

    def __del__(self):
        self.server.close()

if __name__ == "__main__":
    import uuid
    r = Room("localhost", "Silly people room", "room for silly people", room_port=44567)
    r.accept()
