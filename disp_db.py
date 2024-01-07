import sqlite3

def display_all_data(db_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # Get a list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Loop through all the tables and print their contents
    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")

        # Retrieve all data from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Print the rows
        for row in rows:
            print(row)

        print("\n")  # Print a newline for better readability

    # Close the connection
    conn.close()

# Replace 'your_database.db' with the path to your SQLite database file
database_file = 'databases/server/rooms.db'
display_all_data(database_file)

