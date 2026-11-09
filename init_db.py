
import sqlite3

# Connect to database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
''')

# Check if source column exists
cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

# Add source column if missing
if 'source' not in columns:
    cursor.execute("""
        ALTER TABLE students
        ADD COLUMN source TEXT DEFAULT 'Local'
    """)

# Delete existing sample records
cursor.execute("DELETE FROM students")

# Five sample student records
students = [
    ('26-00123', 'Yvette Mahilum', 'BSIT', 1, 'A', 'Local'),
    ('26-00124', 'Princess Pacardo', 'BSA', 1, 'B', 'Local'),
    ('26-00125', 'Pedro Reyes', 'BSOA', 2, 'A', 'Local'),
    ('26-00126', 'Ana Garcia', 'BSHM', 3, 'B', 'Local'),
    ('26-00127', 'Carlos Mendoza', 'BSIT', 4, 'A', 'Local')
]

# Insert student records
cursor.executemany('''
INSERT INTO students
(student_id, name, program, year, section, source)
VALUES (?, ?, ?, ?, ?, ?)
''', students)

# Save changes
conn.commit()

# Close database connection
conn.close()

print("Database created successfully.")
print("Five student records added successfully.")
print("All records have Local as their source.")
