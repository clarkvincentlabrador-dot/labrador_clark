
import sqlite3
import requests
from pathlib import Path
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = Path(__file__).resolve().parent / "students.db"

# Raveen's deployed student API
CLASSMATE_API = "https://raveenemmanuelcelo.onrender.com/api/students"

# Partner API
# Replace this URL if your partner has a different deployed API.
PARTNER_API = CLASSMATE_API


# DATABASE CONNECTION
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# CREATE DATABASE AND TABLE
def initialize_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year INTEGER NOT NULL,
            section TEXT NOT NULL,
            source TEXT DEFAULT 'Local'
        )
    """)

    # Check if source column exists
    columns = [
        column["name"]
        for column in conn.execute("PRAGMA table_info(students)").fetchall()
    ]

    # Add source column to existing database
    if "source" not in columns:
        conn.execute("""
            ALTER TABLE students
            ADD COLUMN source TEXT DEFAULT 'Local'
        """)

    conn.commit()
    conn.close()


initialize_database()


# VALIDATE STUDENT DATA
def validate_student_data(data):
    if not isinstance(data, dict):
        return "Invalid JSON data."

    fields = ["student_id", "name", "program", "year", "section"]

    for field in fields:
        if field not in data or str(data[field]).strip() == "":
            return f"{field} is required."

    try:
        year = int(data["year"])

        if year < 1 or year > 4:
            return "Year must be between 1 and 4."

    except (ValueError, TypeError):
        return "Invalid year."

    return None


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# STUDENT INFORMATION API
@app.route("/student", methods=["GET"])
def get_student():
    return jsonify({
        "student_id": "24-00063",
        "name": "Clark Vincent Labrador",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# COURSE API
@app.route("/course", methods=["GET"])
def get_course():
    return jsonify({
        "course": "Bachelor of Science in Information Technology",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# SKILLS API
@app.route("/skills", methods=["GET"])
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


# GREETING API
@app.route("/hello", methods=["GET"])
def say_hello():
    name = request.args.get("name", "Student")

    return jsonify({
        "message": f"Hello, {name}!"
    })


# GET ALL STUDENTS
@app.route("/students", methods=["GET"])
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_db_connection()

    try:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

        return jsonify([dict(student) for student in students])

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# GET ONE STUDENT
@app.route("/students/<int:id>", methods=["GET"])
@app.route("/api/students/<int:id>", methods=["GET"])
def get_student_by_id(id):
    conn = get_db_connection()

    try:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({"error": "Student not found."}), 404

        return jsonify(dict(student))

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# GET STUDENTS BY YEAR
@app.route("/students/year/<int:year>", methods=["GET"])
def get_students_by_year(year):
    if year < 1 or year > 4:
        return jsonify({
            "error": "Year must be between 1 and 4."
        }), 400

    conn = get_db_connection()

    try:
        students = conn.execute(
            "SELECT * FROM students WHERE year = ? ORDER BY id DESC",
            (year,)
        ).fetchall()

        return jsonify([dict(student) for student in students])

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# ADD STUDENT (LOCAL OR IMPORTED)
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)
    error = validate_student_data(data)

    if error:
        return jsonify({"error": error}), 400

    source = data.get("source", "Local")

    if source not in ["Local", "Imported"]:
        return jsonify({"error": "Invalid student source."}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"].strip(),
            data["name"].strip(),
            data["program"].strip(),
            int(data["year"]),
            data["section"].strip(),
            source
        ))

        conn.commit()

        return jsonify({
            "message": "Student added successfully!",
            "id": cursor.lastrowid,
            "source": source
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists."
        }), 409

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# UPDATE STUDENT
@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)
    error = validate_student_data(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if existing is None:
            return jsonify({"error": "Student not found."}), 404

        conn.execute("""
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
        """, (
            data["student_id"].strip(),
            data["name"].strip(),
            data["program"].strip(),
            int(data["year"]),
            data["section"].strip(),
            id
        ))

        conn.commit()

        return jsonify({
            "message": "Student updated successfully!"
        })

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists."
        }), 409

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# DELETE STUDENT
@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?",
            (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found."}), 404

        conn.commit()

        return jsonify({
            "message": "Student deleted successfully!"
        })

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# RETRIEVE RAVEEN'S RECORDS
@app.route("/classmate-records", methods=["GET"])
def get_classmate_students():
    try:
        response = requests.get(CLASSMATE_API, timeout=60)
        response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            return jsonify({
                "error": "Classmate API did not return a student list."
            }), 502

        return jsonify(records)

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Raveen's API request timed out."
        }), 504

    except requests.exceptions.RequestException as error:
        return jsonify({
            "error": "Unable to connect to Raveen's API.",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({
            "error": "Raveen's API returned invalid JSON."
        }), 502


# STEP 4: RETRIEVE PARTNER RECORDS
@app.route("/partner-records", methods=["GET"])
def partner_records():
    try:
        response = requests.get(PARTNER_API, timeout=60)
        response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            return jsonify({
                "error": "Partner API did not return a student list."
            }), 502

        return jsonify(records)

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Partner API request timed out."
        }), 504

    except requests.exceptions.RequestException as error:
        return jsonify({
            "error": "Unable to retrieve partner records.",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({
            "error": "Partner API returned invalid JSON."
        }), 502


# IMPORT PARTNER STUDENT INTO MY DATABASE
@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True)
    error = validate_student_data(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"].strip(),
            data["name"].strip(),
            data["program"].strip(),
            int(data["year"]),
            data["section"].strip(),
            "Imported"
        ))

        conn.commit()

        return jsonify({
            "message": "Partner record saved successfully!",
            "id": cursor.lastrowid,
            "source": "Imported"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists in your database."
        }), 409

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# API ERROR HANDLER
@app.errorhandler(404)
def page_not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "error": "API endpoint not found."
        }), 404

    return "Page not found.", 404


# RUN FLASK APPLICATION
if __name__ == "__main__":
    app.run(debug=True)
