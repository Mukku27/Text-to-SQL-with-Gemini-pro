import sqlite3
import random
from faker import Faker

# Connect to the SQLite database
connection = sqlite3.connect("student.db")

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Drop the existing STUDENT table if it exists
cursor.execute("DROP TABLE IF EXISTS STUDENT")

# Create the STUDENT table with additional columns
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(50),
    AGE INTEGER,
    GENDER VARCHAR(10),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    GPA REAL,
    EMAIL VARCHAR(50),
    ADDRESS VARCHAR(100)
);
"""
cursor.execute(table_info)

# Generate sample data using Faker
fake = Faker()

def generate_student_data(num_students):
    student_data = []
    for _ in range(num_students):
        name = fake.name()
        age = random.randint(14, 18)
        gender = random.choice(['Male', 'Female', 'Other'])
        class_ = random.choice(['9th', '10th', '11th', '12th'])
        section = random.choice(list('ABCDEFGHIJKLM'))
        gpa = round(random.uniform(2.0, 4.0), 2)
        email = fake.email()
        address = fake.address().replace('\n', ', ')
        student_data.append((name, age, gender, class_, section, gpa, email, address))
    return student_data

# Insert initial sample data into the STUDENT table
initial_students = generate_student_data(1000)

# Insert the generated data into the table
cursor.executemany("""
    INSERT INTO STUDENT (NAME, AGE, GENDER, CLASS, SECTION, GPA, EMAIL, ADDRESS) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
""", initial_students)

# Commit the changes and close the connection
connection.commit()
connection.close()

# Now, let's retrieve and print a few rows from the STUDENT table to verify the data
# Re-establish the connection and cursor
re_connection = sqlite3.connect("student.db")
re_cursor = re_connection.cursor()

select_data = "SELECT * FROM STUDENT LIMIT 10;"
re_cursor.execute(select_data)

# Fetch all rows from the result
rows = re_cursor.fetchall()

# Print each row
for row in rows:
    print(row)

# Close the re-established connection
re_connection.close()
