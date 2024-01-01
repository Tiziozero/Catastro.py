import socket, threading, struct, logging
import sqlite3 as sql
class Room:
    def __init__(self, room_addr, room_port, room_name, room_description, room_id):
        self.addr, self.port, self.room_name, self.room_description, self.room_id = room_addr, room_port, room_name, room_description, room_id
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.addr, self.port))
        self.server.listen()
        self.users = []
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
        self.on = True

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
        client_recv_thread = threading.Thread(target=self.client_recv, args=(a,))
        client_recv_thread.daemon = True
        client_recv_thread.start()

    def client_recv(self, a):
        while self.on:
            try:
                bs = a.recv(8)
                if len(bs) == 0:
                    self.close_client_conection(a)
                (length,) = struct.unpack('>Q', bs)
                print(f"data len: {bs}")
                data = b''
                while len(data) < length:
                    to_read = length - len(data)
                    data += a.recv(
                        4096 if to_read > 4096 else to_read)
                data = data.decode()
                print(f"received {data}")
            except ValueError as e:
                print(f"ValueError in room {self.room_id} client receive method -> {e}")
            except Exception as e:
                print(f"Other error in room {self.room_id} client receive method -> {e}")


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
    r = Room("localhost", 2222, "Silly people room", "room for silly people", f"{uuid.uuid4()}")
    r.accept()
