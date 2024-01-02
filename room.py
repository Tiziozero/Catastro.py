import socket, threading, uuid, struct, logging
import sqlite3 as sql
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

        self.add_room("databases/server/rooms.db", self.room_name, self.room_description, self.addr, self.port, self.room_id, is_open=self.is_open)
        self.on = True

    def add_room(self, db_name, room_name, room_description, room_addr, room_port, room_id=None, users=0, is_open=True):
        try:
            with sql.connect(db_name) as conn:
                c = conn.cursor()
                if not room_id:
                    room_id = str(uuid.uuid4())
                room_id = str(room_id)
                c.execute('''
                    INSERT INTO rooms (room_id, room_name, room_description, room_addr, room_port, users, is_open)
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
                print(f"")
                a.send(f"welcome in {self.room_name}".encode())
                self.handle_client(a)
            except Exception as e:
                print(f"ERROR in room {self.room_id} user acceptance -> {e}")
        

    def handle_client(self, a):
        self.users.append(a)
        client_recv_thread = threading.Thread(target=self.client_recv, args=(a,))
        client_recv_thread.daemon = True
        client_recv_thread.start()

    def client_recv(self, a):
        while self.on:
            try:
                bs = a.recv(8)
                if len(bs) == 0:
                    self.close_client_conection(a)
                    break
                (length,) = struct.unpack('>Q', bs)
                print(f"data len: {bs}")
                data = b''
                while len(data) < length:
                    to_read = length - len(data)
                    data += a.recv(
                        4096 if to_read > 4096 else to_read)
                data = data.decode()
                print(f"received {data}")
                self.send_data_to_all(a, data)
            except ValueError as e:
                print(f"ValueError in room {self.room_id} client receive method -> {e}")
            except Exception as e:
                print(f"Other error in room {self.room_id} client receive method -> {e}")

        print(f"Closed receiiving thread with {a}")

    def send_data_to_all(self, a, data):
        for user in self.users:
            if user != a:
                data = data.encode()
                length = struct.pack('>Q', len(data))
                user.sendall(length)
                user.sendall(data)

    def close_client_conection(self, a):
        if a in self.users:
            self.users.remove(a)
            a.close()
            print(f"closed connection with {a}")
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
        self.close()

if __name__ == "__main__":
    import uuid
    r = Room("localhost", "Silly people room", "room for silly people")
    r.accept()
