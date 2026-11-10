
import sqlite3
import requests
from pathlib import Path
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = Path(__file__).resolve().parent / "students.db"

# RAVEEN'S DEPLOYED STUDENT API
CLASSMATE_API = "https://13.238.105.177/api/students"

# PARTNER API
# This points to Raveen's API.
PARTNER_API = "http://13.238.105.177/api/students"
PARTNER_POST_URL = PARTNER_API


# DATABASE CONNECTION
def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


# INITIALIZE DATABASE
def initialize_database():
    conn = get_db_connection()

    try:
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

        columns = {
            column["name"]
            for column in conn.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        }

        if "source" not in columns:
            conn.execute("""
                ALTER TABLE students
                ADD COLUMN source TEXT DEFAULT 'Local'
            """)

        conn.execute("""
            UPDATE students
            SET source = 'Local'
            WHERE source IS NULL OR TRIM(source) = ''
        """)

        conn.commit()

    finally:
        conn.close()


initialize_database()


# VALIDATE STUDENT DATA
def validate_student_data(data):

    if not isinstance(data, dict):
        return "Invalid JSON data."

    required_fields = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    for field in required_fields:
        if field not in data or str(data[field]).strip() == "":
            return f"{field} is required."

    try:
        year = int(data["year"])

        if year < 1 or year > 4:
            return "Year must be between 1 and 4."

    except (ValueError, TypeError):
        return "Invalid year."

    return None


# INSERT STUDENT
def insert_student(data, source):

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(data["student_id"]).strip(),
            str(data["name"]).strip(),
            str(data["program"]).strip(),
            int(data["year"]),
            str(data["section"]).strip(),
            source
        ))

        conn.commit()
        return cursor.lastrowid

    finally:
        conn.close()


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

        return jsonify([
            dict(student) for student in students
        ])

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
            return jsonify({
                "error": "Student not found."
            }), 404

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

        return jsonify([
            dict(student) for student in students
        ])

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# ADD STUDENT
@app.route("/api/students", methods=["POST"])
def add_student():

    data = request.get_json(silent=True)

    error = validate_student_data(data)

    if error:
        return jsonify({"error": error}), 400

    source = str(
        data.get("source", "External API")
    ).strip()

    allowed_sources = [
        "Local",
        "Imported",
        "External API",
        "Partner API"
    ]

    if source not in allowed_sources:
        return jsonify({
            "error": "Invalid student source.",
            "received_source": source,
            "allowed_sources": allowed_sources
        }), 400

    try:
        new_id = insert_student(data, source)

        return jsonify({
            "message": "Student added successfully!",
            "id": new_id,
            "source": source
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists."
        }), 409

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500


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
            return jsonify({
                "error": "Student not found."
            }), 404

        conn.execute("""
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
        """, (
            str(data["student_id"]).strip(),
            str(data["name"]).strip(),
            str(data["program"]).strip(),
            int(data["year"]),
            str(data["section"]).strip(),
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
            return jsonify({
                "error": "Student not found."
            }), 404

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
        response = requests.get(
            CLASSMATE_API,
            timeout=30
        )

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


# RETRIEVE PARTNER RECORDS
@app.route("/partner-records", methods=["GET"])
def partner_records():

    try:
        response = requests.get(
            PARTNER_API,
            timeout=30
        )

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


# IMPORT SELECTED PARTNER RECORD
@app.route("/import-student", methods=["POST"])
def import_student():

    data = request.get_json(silent=True)

    error = validate_student_data(data)

    if error:
        return jsonify({"error": error}), 400

    try:
        new_id = insert_student(data, "Partner API")

        return jsonify({
            "message": "Partner record saved successfully!",
            "id": new_id,
            "source": "Partner API"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists in your database."
        }), 409

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500


# SEND PRACTICE RECORD TO PARTNER
# AUTOMATIC - NO INPUT REQUIRED
@app.route("/send-to-partner", methods=["POST"])
def send_to_partner():

    record = {
        "student_id": "EXT-CLARK-001",
        "name": "Clark Sample Exchange Record",
        "program": "BSIT",
        "year": 1,
        "section": "A",
        "source": "Partner API"
    }

    error = validate_student_data(record)

    if error:
        return jsonify({"error": error}), 400

    try:
        response = requests.post(
            PARTNER_POST_URL,
            json=record,
            timeout=20
        )

        try:
            partner_result = response.json()
        except ValueError:
            partner_result = response.text

        return jsonify({
            "message": (
                "Partner accepted the record."
                if response.ok
                else "Partner rejected the record."
            ),
            "status_code": response.status_code,
            "partner_response": partner_result,
            "sent_record": record
        }), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Partner API request timed out."
        }), 504

    except requests.exceptions.RequestException as error:
        return jsonify({
            "error": "Unable to send record to partner.",
            "details": str(error)
        }), 502


# 404 ERROR HANDLER
@app.errorhandler(404)
def page_not_found(error):

    if request.path.startswith("/api/"):
        return jsonify({
            "error": "API endpoint not found."
        }), 404

    return "Page not found.", 404


if __name__ == "__main__":
    app.run(debug=True)
