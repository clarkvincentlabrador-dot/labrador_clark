
import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
''')

# Delete existing sample records
cursor.execute("DELETE FROM students")

# Five sample student records
students = [
    ('26-00123', 'Yvette Mahilum', 'BSIT', 1, 'A'),
    ('26-00124', 'Princess Pacardo', 'BSA', 1, 'B'),
    ('26-00125', 'Pedro Reyes', 'BSOA', 2, 'A'),
    ('26-00126', 'Ana Garcia', 'BSHM', 3, 'B'),
    ('26-00127', 'Carlos Mendoza', 'BSIT', 4, 'A')
]

cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
''', students)

conn.commit()
conn.close()

print("Database created successfully.")
print("Five student records added successfully.")
