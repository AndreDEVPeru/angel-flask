from flask import Flask, request, jsonify, g, render_template, url_for, \
    redirect, make_response
from sqlalchemy.orm import sessionmaker
from flask_login import (LoginManager, login_user, login_required,
                         logout_user, current_user)
from sqlalchemy import create_engine
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm.exc import NoResultFound

# cors
from flask_cors import CORS

from models import Teacher, Subject, Student, Grade, Exam, Enrollment

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_COOKIE_HTTPONLY'] = False


username = "postgres"
password = "V1pHvOcoqKSxwqI6uB2y"
host = "database-3.cwhnlj9dcl1p.us-east-1.rds.amazonaws.com"
port = "5432"
database = "postgres"  # Replace with your actual database name

DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"

engine = create_engine(
    DATABASE_URL
)
# Database setup
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
admin.add_view(ModelView(Exam, Session()))
admin.add_view(ModelView(Grade, Session()))
admin.add_view(ModelView(Enrollment, Session()))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    content_type = request.headers.get('Content-Type')
    if 'application/json' in content_type:
        request_json = request.get_json()
        username = request_json.get('username')
        password = request_json.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    session = Session()
    teacher = session.query(Teacher).filter_by(username=username).first()

    if teacher and teacher.password == password:
        login_user(teacher)
        response = make_response(url_for('index'))
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
    teacher = current_user

    if teacher:
        subjects = [{'id': subject.id, 'name': subject.name}
                    for subject in teacher.subjects]
        return jsonify(subjects), 200
    else:
        return jsonify({'message': 'Teacher not found'}), 404


@app.route('/subject/<subject_id>/students', methods=['GET'])
def get_subject_students(subject_id):
    session = Session()
    subject = session.query(Subject).get(subject_id)

    if subject:
        students = []
        for enrollment in session.query(Enrollment).filter(
                Enrollment.subject == subject):
            students.append({'id': enrollment.student_id,
                             'name': enrollment.student.name,
                             'enrollment_id': enrollment.id
                             })
        return jsonify(students), 200
    else:
        session.close()  # Close the session in case of error
        return jsonify({'message': 'Subject not found'}), 404


@app.route('/exams/<enrollment_id>', methods=['GET'])
def get_exams(enrollment_id):
    session = Session()
    enrollment = session.query(Enrollment).get(enrollment_id)
    if enrollment:
        exams = [{'id': exam.id,
                    'name': exam.name,
                    'subject_id': exam.subject_id}
                     for exam in enrollment.subject.exams]
        return jsonify(exams), 200
    else:
        session.close()
        return jsonify({'message': 'Enrollment not found'}), 404


@app.route('/grades/<enrollment_id>/', methods=['GET', 'POST'])
def grades_endpoint(enrollment_id):
    session = Session()
    if request.method == 'GET':
        enrollment = session.query(Enrollment).get(enrollment_id)
        if enrollment:
            grades = [{'exam_grade': grade.exam_grade,
                       'exam_id': grade.exam_id,
                       'exam_name': grade.exam.name}
                      for grade in enrollment.grades]
            session.close()  # Close the session
            return jsonify(grades), 200
        else:
            session.close()  # Close the session in case of error
            return jsonify({'message': 'Student not found'}), 404

    elif request.method == 'POST':
        grades = request.get_json()
        for grade in grades:
            exam_id = grade.get('exam_id')
            exam_grade = grade.get('exam_grade')

            try:
                existing_grade = session.query(Grade).filter_by(
                    enrollment_id=enrollment_id,
                    exam_id=exam_id
                ).one()
                existing_grade.exam_grade = exam_grade  # Update the existing grade
            except NoResultFound:
                new_grade = Grade(enrollment_id=enrollment_id,
                                  exam_id=exam_id,
                                  exam_grade=exam_grade)
                session.add(new_grade)
        session.commit()
        session.close()
        return jsonify({'message': 'Grades added successfully'}), 200


@app.route('/grades/average/<enrollment_id>/', methods=['GET'])
def average_grades(enrollment_id):
    session = Session()
    enrollment = session.query(Enrollment).get(enrollment_id)
    if enrollment:
        grades = [grade.exam_grade for grade in enrollment.grades]
        average = sum(grades) / len(grades)
        enrollment.final_grade = average
        session.commit()
        return jsonify({'average': average,
                        'course_id': enrollment.subject.id,
                        'course_name': enrollment.subject.name,
                        'student_id': enrollment.student.id,
                        'student_name': enrollment.student.name,
                        }), 200
    else:
        session.close()
        return jsonify({'message': 'Enrollment not found'}), 404



@app.route('/grades/average/all/<enrollment_id>', methods=['GET'])
def average_grades_all(enrollment_id):
    session = Session()
    enrollment = session.query(Enrollment).get(enrollment_id)
    if enrollment:
        enrollments = session.query(Enrollment).filter_by(
            subject_id=enrollment.subject_id
        ).all()
        grades = []
        for _enrollment in enrollments:
            grades += [{
                'student_average': _enrollment.final_grade,
                'course_id': _enrollment.subject.id,
                'course_name': _enrollment.subject.name,
                'student_id': _enrollment.student.id,
                'student_name': _enrollment.student.name,
                'enrollment_id': _enrollment.id
            }]
        return jsonify(grades), 200
    else:
        session.close()
        return jsonify({'message': 'Enrollment not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
