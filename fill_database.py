import sqlite3
import random
import uuid
import server


def add_room(db_name, room_name, capacity=None, room_type=None, is_occupied=False):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Generate a unique UUID for the room_id
    room_uuid = str(uuid.uuid4())

    # Insert a new room
    cursor.execute('''
        INSERT INTO rooms (room_name, room_id, capacity, room_type, is_occupied)
        VALUES (?, ?, ?, ?, ?)
    ''', (room_name, room_uuid, capacity, room_type, is_occupied))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()


def generate_random_rooms(db_name, number_of_rooms):
    # List of sample room names and types for random selection
    sample_room_names = ['Conference Room', 'Meeting Room', 'Office', 'Lounge', 'Auditorium']
    sample_room_types = ['Conference', 'Meeting', 'Private', 'Public', 'Event']

    for _ in range(number_of_rooms):
        # Generate random room properties
        room_name = random.choice(sample_room_names) + ' ' + str(random.randint(1, 100))
        capacity = random.randint(1, 50)
        room_type = random.choice(sample_room_types)
        is_occupied = random.choice([True, False])

        # Add the randomly generated room to the database
        add_room(db_name, room_name, capacity, room_type, is_occupied)

generate_random_rooms("databases/server/rooms.db", 1)
