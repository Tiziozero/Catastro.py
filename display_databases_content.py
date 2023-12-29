import sqlite3

def display_data(db_path, table_name):
    # Connect to the database
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    # Query to select all data from the table
    cursor.execute(f"SELECT * FROM {table_name}")

    # Fetch all rows
    rows = cursor.fetchall()

    # Find the maximum width of data in each column
    widths = []
    for col in cursor.description:
        widths.append(max(len(col[0]), max([len(str(row[1])) for row in rows], default=0)))

    # Print the headers
    header = "|".join([col[0].ljust(width) for col, width in zip(cursor.description, widths)])
    print(header)
    print("-" * len(header))

    # Print the rows
    for row in rows:
        print("|".join([str(cell).ljust(width) for cell, width in zip(row, widths)]))

    # Close the connection
    db.close()

# Usage
display_data('databases/rooms/rooms.db', 'rooms')
display_data('databases/users/users.db', 'users')

