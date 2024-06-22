import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect("student.db")

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Create the STUDENT table if it doesn't already exist
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT (
    NAME VARCHAR(50),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25)
);
"""
cursor.execute(table_info)

# Insert initial sample data into the STUDENT table
initial_insert_data = """
INSERT INTO STUDENT (NAME, CLASS, SECTION) VALUES ('John Doe', '10th', 'A');
INSERT INTO STUDENT (NAME, CLASS, SECTION) VALUES ('Jane Smith', '11th', 'B');
INSERT INTO STUDENT (NAME, CLASS, SECTION) VALUES ('Alice Johnson', '12th', 'C');
"""
cursor.executescript(initial_insert_data)

# Add 10 more students
additional_students = [
    ('Bob Brown', '9th', 'D'),
    ('Charlie Davis', '10th', 'E'),
    ('David Evans', '11th', 'F'),
    ('Emily Foster', '12th', 'G'),
    ('Frank Gordon', '10th', 'H'),
    ('Grace Harris', '9th', 'I'),
    ('Henry Ingram', '11th', 'J'),
    ('Isabella Jackson', '12th', 'K'),
    ('Kevin Lewis', '9th', 'L'),
    ('Mia Nelson', '10th', 'M')
]

for name, class_, section in additional_students:
    cursor.execute("""
        INSERT INTO STUDENT (NAME, CLASS, SECTION) VALUES (?,?,?);
    """, (name, class_, section))

# Commit the changes and close the connection
connection.commit()
connection.close()

# Now, let's retrieve and print the data from the STUDENT table
# Re-establish the connection and cursor
re_connection = sqlite3.connect("student.db")
re_cursor = re_connection.cursor()

select_data = "SELECT * FROM STUDENT;"
re_cursor.execute(select_data)

# Fetch all rows from the result
rows = re_cursor.fetchall()

# Print each row
for row in rows:
    print(row)

# Close the re-established connection
re_connection.close()