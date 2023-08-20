from flask import Flask, request, jsonify, g, render_template, url_for, \
    redirect, make_response
from sqlalchemy.orm import sessionmaker
from flask_login import (LoginManager, login_user, login_required,
                         logout_user, current_user)
from sqlalchemy import create_engine
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# cors
from flask_cors import CORS

from models import Teacher, Subject, Student, Grade, Exam, Enrollment

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database setup
engine = create_engine('sqlite:///university.db')
Session = sessionmaker(bind=engine)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = Session()
    return session.query(Teacher).get(int(user_id))


admin = Admin(app, name='University Admin', template_mode='bootstrap3')

# Add your models to the admin interface
admin.add_view(ModelView(Teacher, Session()))
admin.add_view(ModelView(Subject, Session()))
admin.add_view(ModelView(Student, Session()))
admin.add_view(ModelView(Enrollment, Session()))
admin.add_view(ModelView(Exam, Session()))
admin.add_view(ModelView(Grade, Session()))


@app.route('/')
def index():
    return render_template('index.html')


@app.before_request
def before_request():
    g.session = Session()


@app.after_request
def after_request(response):
    g.session.close()
    return response

"""
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    session = Session()
    teacher = session.query(Teacher).filter_by(username=username).first()

    if teacher and teacher.password == password:
        login_user(teacher)
        return redirect(url_for('dashboard'))
    else:
        return "Invalid login"
"""


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'OPTIONS':
        # Respond to preflight requests with necessary headers
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return response
    username = request.form.get('username')
    password = request.form.get('password')

    session = Session()
    teacher = session.query(Teacher).filter_by(username=username).first()

    if teacher and teacher.password == password:
        login_user(teacher)
        response = make_response()
        response.headers['Access-Control-Expose-Headers'] = 'Set-Cookie'
        response.set_cookie('your_cookie_name', 'your_cookie_value')
        response.headers['lala'] = 'lala'

        return response
    else:
        return "Invalid login"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome, {current_user.username}!"


@app.route('/teacher/subjects', methods=['GET'])
@login_required
def get_teacher_subjects():
    print("lalamon")
    print("hola", request.headers)
    teacher = current_user


    if teacher:
        subjects = [{'id': subject.id, 'name': subject.name}
                    for subject in teacher.subjects]
        return jsonify(subjects), 200
    else:
        return jsonify({'message': 'Teacher not found'}), 404


@app.route('/subject/<subject_id>/students', methods=['GET'])
def get_subject_students(subject_id):
    subject = g.session.query(Subject).get(subject_id)

    if subject:
        students = [{'id': student.id, 'name': student.name} for enrollment in
                    subject.enrollments for student in enrollment.student]
        return jsonify({'students': students}), 200
    else:
        return jsonify({'message': 'Subject not found'}), 404


@app.route('/student/<student_id>/grades', methods=['GET'])
def get_student_grades(student_id):
    student = g.session.query(Student).get(student_id)

    if student:
        grades = [{'subject': grade.subject.name, 'exam': grade.exam.name,
                   'exam_grade': grade.exam_grade,
                   'final_grade': grade.final_grade} for grade in
                  student.grades]
        return jsonify({'grades': grades}), 200
    else:
        return jsonify({'message': 'Student not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
