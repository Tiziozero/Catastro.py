import sqlite3
import random
import uuid
import server


def add_room(db_name, room_name, room_uuid, room_desctiption, room_addr, room_port, users, is_open):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Generate a unique UUID for the room_id
    room_uuid = str(uuid.uuid4())
    """
      48                      CREATE TABLE IF NOT EXISTS rooms (
    1                         room_id TEXT NOT NULL UNIQUE,
    2                         id INTEGER PRIMARY KEY AUTOINCREMENT,
    3                         room_name TEXT NOT NULL,
    4                         room_description TEXT,
    5                         room_addr TEXT NOT NULL,
    6                         room_port TEXT NOT NULL,
    7                         users INTEGER,
    8                         is_open BOOLEAN
    # oInsert a new room
    """
    cursor.execute('''
        INSERT INTO rooms (room_name, room_id, room_description, room_addr, room_port, users, is_open)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (room_name, room_uuid, room_desctiption, room_addr, room_port, users, is_open))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
def generate_random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

def generate_random_description():
    subjects = ["The cat", "A dog", "This tool", "The system", "Our team"]
    verbs = ["jumps", "runs", "excels", "operates", "collaborates"]
    adverbs = ["quickly", "efficiently", "smoothly", "slowly", "steadily"]
    objects = ["over the fence", "in the field", "with agility", "at all times", "under pressure"]

    return f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(adverbs)} {random.choice(objects)}."


def generate_random_rooms(db_name, number_of_rooms):
    # List of sample room names and types for random selection
    sample_room_names = ['Conference Room', 'Meeting Room', 'Office', 'Lounge', 'Auditorium']
    sample_room_types = ['Conference', 'Meeting', 'Private', 'Public', 'Event']

    for i in range(number_of_rooms):
        # Generate random room properties
        room_name = random.choice(sample_room_names) + ' ' + str(random.randint(1, 100))
        capacity = random.randint(1, 50)
        is_open = random.choice([True, False])

        # Add the randomly generated room to the database
        add_room(db_name, room_name, uuid.uuid4(), generate_random_description(), generate_random_ip(), 26354 + 4*i, capacity, is_open)

generate_random_rooms("databases/server/rooms.db", 8234579)
