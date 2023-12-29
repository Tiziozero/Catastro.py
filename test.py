import sqlite3
import random
import uuid

def insert_random_data(room_db_path, user_db_path):
    # Connect to the databases
    room_db = sqlite3.connect(room_db_path)
    user_db = sqlite3.connect(user_db_path)
    room_c = room_db.cursor()
    user_c = user_db.cursor()

    # Insert random data into the rooms table
    for _ in range(5):  # Adjust the range for the number of rows you want to insert
        room_c.execute("INSERT INTO rooms (room_name, room_id, users, active, room_address, room_ip, deacription) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (f"Room_{uuid.uuid4()}", str(uuid.uuid4()), random.randint(1, 10), random.randint(0, 1), f"Address_{random.randint(1, 100)}", random.randint(0, 255), "Random Description"))
    
    # Insert random data into the users table
    for _ in range(5):  # Adjust the range for the number of rows you want to insert
        user_c.execute("INSERT INTO users (user_name, user_id, active, deacription) VALUES (?, ?, ?, ?)",
                       (f"User_{uuid.uuid4()}", str(uuid.uuid4()), random.randint(0, 1), "Random Description"))

    # Commit changes and close connections
    room_db.commit()
    user_db.commit()
    room_db.close()
    user_db.close()

# Usage
insert_random_data('databases/rooms/rooms.db', 'databases/users/users.db')

