import socket, threading, uuid, struct, logging, datetime
import sqlite3 as sql
from user import User
from comunication_enums import *
class Room:
    def __init__(self, room_data, MAKE_NEW):
        # print(f"Room data received: {room_data}")
        try:
            self.room_id =                  room_data["room_id"]
            self.room_name =                room_data["room_name"]
            self.room_description =         room_data["room_description"]
            self.room_address =             room_data["room_address"]
            self.room_port =                0
            self.room_is_open =             room_data["room_is_open"]
            self.room_password =            room_data["room_password"]
            self.room_welcome_ascii_art =   room_data["room_welcome_ascii_art"]
            self.room_welcome_message =     room_data["room_welcome_message"]
            self.room_users =               room_data["room_users"]
            self.room_chat_db_name =        room_data["room_chat_db_name"]
            self.room_is_on =               room_data["room_is_on"]
            self.users = []
            self.room_chat_db_name = f"databases/rooms/{self.room_name}_{self.room_id}.db"
            # Check if room id is not provided, then make one
            if not self.room_id:
                self.room_id = uuid.uuid4()
            # print("passed test")

            
            try:
                # Set up room server
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.bind((self.room_address, self.room_port))
                self.server.listen()
                # Updata port
                port = self.server.getsockname()
                print(f"Room under {self.room_id}: {port}")
                self.room_port = port[1]
            except Exception as e:
                print(f"ERROR in creating server connection -> {e}")

            # Update database to contain new port in room already existed
            try:
                with sql.connect("databases/server/rooms.db") as conn:
                    c = conn.cursor()
                    c.execute(f"SELECT * FROM rooms WHERE room_id = ?", (self.room_id,))
                    if len(c.fetchall()) == 0:
                        c.execute(f"""INSERT INTO rooms (
                                  room_id,
                                  room_name,
                                  room_description,
                                  room_address,
                                  room_port,
                                  room_is_open,
                                  room_password,
                                  room_welcome_ascii_art,
                                  room_welcome_message,
                                  room_users,
                                  room_chat_db_name,
                                  room_is_on)
                                  values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (
                                  self.room_id,
                                  self.room_name,
                                  self.room_description,
                                  self.room_address,
                                  self.room_port,
                                  self.room_is_open,
                                  self.room_password,
                                  self.room_welcome_ascii_art,
                                  self.room_welcome_message,
                                  self.room_users,
                                  self.room_chat_db_name,
                                  self.room_is_on)
                                  )
                        print(f"Created row in rooms.db for room wuth room_id: {self.room_id}")
                    else:
                        c.execute("UPDATE rooms SET room_port = ? WHERE room_id = ?", (self.room_port, self.room_id))
                        print(f"Updated database for {self.room_id}: set port to {self.room_port}")
                    conn.commit()
            except Exception as e:
                print(f"ERROR in adding to room -> {e}")
            # Create room chat database
            try:
                with sql.connect(self.room_chat_db_name) as db_conn:
                    c = db_conn.cursor()
                    c.execute("""
                        CREATE TABLE IF NOT EXISTS chat (
                            id INTEGER PRIMARY KEY,
                            time TEXT,
                            user_addr TEXT,
                            name TEXT,
                            message TEXT
                        )
                    """)
                    conn.commit()
                    c.close()
            except Exception as e:
                print(f"ERROR in room {self.room_id} database setup -> {e}")

            self.on = True
            th = threading.Thread(target=self.accept)
            th.daemon = True
            th.start()
        except Exception as e:
            print(f"ERROR in room setup -> {e}")

    def add_room(self, db_name, room_name, room_description, room_address, room_port, room_id=None, users=0, is_open=True, r_password=''):
        pw = r_password
        try:
            with sql.connect(db_name) as conn:
                c = conn.cursor()
                if not room_id:
                    room_id = str(uuid.uuid4())
                room_id = str(room_id)
                c.execute('''
                    INSERT INTO rooms (room_id, room_name, room_description, room_address, room_port, room_users, room_is_open, room_password)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (room_id, room_name, room_description, room_address,  room_port, users, is_open, pw))
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

    def add_message_to_chat_db(self, user_address, name, message):
        with sql.connect(self.room_chat_db_name) as db_conn:
            c = db_conn.cursor()
            sqlval = """
            INSERT INTO chat (time, user_address, name, message)
            VALUES (?, ?, ?, ?)
            """
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(sqlval, (current_time, user_address, name, message))
            db_conn.commit()

    def client_recv(self, u):
        while self.on:
            try:
                bs = u.a.recv(8)
                if len(bs) == 0:
                    self.close_client_conection(u)
                    break
                (length,) = struct.unpack('>Q', bs)
                # print(f"data len: {bs}")
                data = b''
                while len(data) < length:
                    to_read = length - len(data)
                    data += u.a.recv(
                        4096 if to_read > 4096 else to_read)
                if data == Room_Action.ROOM_ACT_QUIT:
                    self.close_client_conection(u)
                    self.send_data_to_all(u, f"user {u.name} disconnected")
                    return
                data = data.decode()
                try:
                    self.add_message_to_chat_db(u.a.getsockname()[0], u.name, data)
                except Exception as e:
                    print(f"ERROR in adding user message to chat database -> {e}")
                # print(f"received {data}")
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
            c.a.close()
        self.server.close()
        if error:
            print(f"Server closed with error -> {error}.")
        else:
            print("Server closed without any appearing errors.")

    def __del__(self):
        print(f"Closing database with id {self.room_id}")
        """with sql.connect("databases/server/rooms.db") as conn:
            c = conn.cursor()
            try:
                sqlv = "DELETE FROM rooms WHERE room_id = ?"
                c.execute(sqlv, (self.room_id,))
                conn.commit()
            except sql.Error as e:
                print(f"An error occurred: {e}")
            finally:
                conn.close()
        """

        self.server.close()

if __name__ == "__main__":
    import uuid
    # r = Room("localhost", "Silly people room", "room for silly people", room_port=44567)
    # r.accept()
