
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00063",
        "name": "Clark Vincent Labrador",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


@app.route('/course')
def get_course():
    return jsonify({
        "course": "Bachelor of Science in Information Technology",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


@app.route('/skills')
def get_skills():
    return jsonify({
        "skills": [
            "Python",
            "Flask",
            "HTML",
            "CSS",
            "JavaScript",
            "Database Management"
        ]
    })


@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
        "message": f"Hello, {name}!"
    })


@app.route('/students')
def get_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# Additional API: Display Students by Year Level
@app.route('/students/year/<int:year>')
def get_students_by_year(year):
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students WHERE year = ?',
        (year,)
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        """INSERT INTO students
        (student_id, name, program, year, section)
        VALUES (?, ?, ?, ?, ?)""",
        (data['student_id'], data['name'], data['program'],
         data['year'], data['section'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Student added", "id": new_id}), 201

@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()
    conn.close()
    if student is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dict(student))

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        """UPDATE students SET student_id=?, name=?, program=?,
        year=?, section=? WHERE id=?""",
        (data['student_id'], data['name'], data['program'],
         data['year'], data['section'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated"})

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted"})

if __name__ == '__main__':
    app.run(debug=True)
