import sqlite3

def display_rooms(db_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Retrieve all rooms
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Print the rooms in a neat format
    print(f"{'ID':<5} {'Room Name':<20} {'Room ID':<40} {'Capacity':<10} {'Room Type':<15} {'Occupied':<10}")
    print("-" * 100)
    for room in rooms:
        id, name, room_id, capacity, room_type, is_occupied = room
        print(f"{id:<5} {name:<20} {room_id:<40} {capacity:<10} {room_type:<15} {is_occupied:<10}")

# Example usage
display_rooms("databases/server/rooms.db")
