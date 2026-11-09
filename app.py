
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(debug=True)
