#!/usr/bin/env python3

import socket, threading, json, sys, datetime, random, string, uuid
import sqlite3 as sql
from comunication_enums import *
from room import Room

def generate_random_rooms(db_name, number_of_rooms):
    # List of sample room names and types for random selection
    sample_room_names = ['Conference Room', 'Meeting Room', 'Office', 'Lounge', 'Auditorium']
    sample_room_types = ['Conference', 'Meeting', 'Private', 'Public', 'Event']

    for _ in range(number_of_rooms):
        # Generate random room properties
        room_name = random.choice(sample_room_names) + ' ' + str(random.randint(0, 100))
        capacity = random.randint(0, 50)
        room_type = random.choice(sample_room_types)
        is_occupied = random.choice([True, False])

        # Add the randomly generated room to the database
        Server.add_room(db_name, room_name, capacity, room_type, is_occupied)


def send_db(user, db_path, db_name):
    with sql.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(f"SELECT * FROM {db_name}")
        rooms = c.fetchall()
        for row in rooms:
            print(row)
        

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
                user_thread = threading.Thread(target=self.handle_user, args=(a,))
                user_thread.daemon = True
                user_thread.start()
            except Exception as e:
                print(f"ERROR in server run -> {e}")

    def handle_user(self, user):
        while True:
            try:
                send_db(user, "databases/server/rooms.db", "rooms")
                

            except Exception as e:
                print(f"ERROR in client handle thread -> {e}")

if __name__ == '__main__':
    s = Server('localhost', 42069)
    s.run()
