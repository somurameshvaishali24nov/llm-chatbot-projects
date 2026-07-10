import sqlite3

## Connect to SQLite
connection = sqlite3.connect('student.db')

## Create a cursor object to inser record, creae table, retrieve results
cursor = connection.cursor()

## Create the table
table_info = """
    CREATE TABLE IF NOT EXISTS students (
        name VARCHAR(25),
        class VARCHAR(25),
        section VARCHAR(25),
        MARKS INT
    );
"""

cursor.execute(table_info)

## Insert some more records
insert_query = """
    INSERT INTO students (name, class, section, MARKS)
    VALUES
        ('John Doe', '10th', 'A', 85),
        ('Jane Smith', '10th', 'B', 90),
        ('Alice Johnson', '11th', 'A', 78),
        ('Bob Brown', '11th', 'B', 92),
        ('Charlie Davis', '12th', 'A', 88),
        ('Diana Evans', '12th', 'B', 95);
"""
cursor.execute(insert_query)

## Display all the records
print("All records in the students table:")
select_query = "SELECT * FROM students;"
data = cursor.execute(select_query)

for row in data:
    print(row)

## Close the connection
connection.commit()
connection.close()