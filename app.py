
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


if __name__ == '__main__':
    app.run(debug=True)
