import sqlite3 as sql
import random
import uuid
import server


def add_room(db_name, room_name, room_description, room_addr, room_port, room_id=None, users=0, is_open=True, r_password=''):
    pw = r_password
    try:
        with sql.connect(db_name) as conn:
            c = conn.cursor()
            if not room_id:
                room_id = str(uuid.uuid4())
            room_id = str(room_id)
            c.execute('''
                INSERT INTO rooms (room_id, room_name, room_description, room_address, room_port, room_users, room_is_open, room_password      )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (room_id, room_name, room_description, room_addr,  room_port, users, is_open, pw))
            conn.commit()
        return True
    except Exception as e:
        print(f"ERROR in creatin room {room_name} -> {e}")


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
        print(f"round {i}")
        # Generate random room properties
        room_name = random.choice(sample_room_names) + ' ' + str(random.randint(1, 100))
        capacity = random.randint(1, 50)
        is_open = random.choice([True, False])

        # Add the randomly generated room to the database
        add_room(db_name, room_name, generate_random_description(), generate_random_ip(), 26354 + 4*i, room_id=uuid.uuid4(),users=capacity, is_open=is_open, r_password="1234")

for _ in range(2034):
    generate_random_rooms("databases/server/rooms.db", 10)
