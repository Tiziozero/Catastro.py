import sqlite3

def display_data_to_file(db_path, table_name, output_file):
    # Connect to the database
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    # Query to select all data from the table
    cursor.execute(f"SELECT * FROM {table_name}")

    # Fetch all rows
    rows = cursor.fetchall()

    # Find the maximum width of data in each column
    widths = []
    for idx, col in enumerate(cursor.description):
        column_width = max(len(col[0]), max([len(str(row[idx])) for row in rows], default=0))
        widths.append(column_width)

    with open(output_file, 'w') as file:
        # Print the headers
        header = "|".join([col[0].ljust(width) for col, width in zip(cursor.description, widths)])
        file.write(header + "\n")
        file.write("-" * len(header) + "\n")
        print(header)

        # Print the rows
        for row in rows:
            row_str = "|".join([str(cell).ljust(width) for cell, width in zip(row, widths)])
            file.write(row_str + "\n")
            print(row_str)

    # Close the connection
    db.close()

# Usage
display_data_to_file('databases/rooms/rooms.db', 'rooms', 'rooms_output.txt')
display_data_to_file('databases/users/users.db', 'users', 'users_output.txt')

