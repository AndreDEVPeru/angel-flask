from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, \
    Float, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Create a database connection
username = "postgres"
password = "V1pHvOcoqKSxwqI6uB2y"
host = "database-3.cwhnlj9dcl1p.us-east-1.rds.amazonaws.com"
port = "5432"
database = "postgres"  # Replace with your actual database name

DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"

engine = create_engine(
    DATABASE_URL
)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Models
class Teacher(Base, UserMixin):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    subjects = relationship('Subject', back_populates='teacher')

    def __str__(self):
        return f"Teacher {self.username}"


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey(Teacher.id))

    teacher = relationship('Teacher', back_populates='subjects')
    exams = relationship('Exam', back_populates='subject')
    enrollments = relationship('Enrollment', back_populates='subject')

    def __str__(self):
        return f"Curso {self.name}"


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    enrollments = relationship('Enrollment', back_populates='student')

    def __str__(self):
        return f"Student {self.name}"


class Exam(Base):
    __tablename__ = 'exams'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    name = Column(String)  # For example: 'pc1', 'pc2', 'ep', 'ef'

    subject = relationship('Subject', back_populates='exams')
    grades = relationship('Grade', back_populates='exam')

    def __str__(self):
        return f"Exam {self.name} of subject {self.subject.name}"


class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True)
    enrollment_id = Column(Integer,
                           ForeignKey('enrollments.id'),
                           primary_key=True)
    exam_id = Column(Integer,
                     ForeignKey('exams.id'),
                     primary_key=True)
    exam_grade = Column(Float)

    exam = relationship('Exam', back_populates='grades')
    enrollment = relationship('Enrollment', back_populates='grades')
    __table_args__ = (UniqueConstraint('enrollment_id',
                                       'exam_id',
                                       name='_enrollment_exam_uc'),)

    def __str__(self):
        return (f"Grade {self.id}:"
                f" exam {self.exam.name},"
                f" exam_grade {self.exam_grade}")


class Enrollment(Base):
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    final_grade = Column(Float)

    subject = relationship('Subject', back_populates='enrollments')
    student = relationship('Student', back_populates='enrollments')
    grades = relationship('Grade', back_populates='enrollment')

    def __str__(self):
        return (f"Enrollment {self.id}:"
                f" subject {self.subject.name},"
                f" final_grade {self.final_grade}")


# Create tables in the database
Base.metadata.create_all(engine)
