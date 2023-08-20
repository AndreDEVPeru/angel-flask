from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, \
    Float
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Create a database connection
engine = create_engine('sqlite:///university.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Models
class Teacher(Base, UserMixin):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    subjects = relationship('Subject', back_populates='teacher')


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))

    teacher = relationship('Teacher', back_populates='subjects')
    enrollments = relationship('Enrollment', back_populates='subject')
    exams = relationship('Exam', back_populates='subject')
    grades = relationship('Grade', back_populates='subject')


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    enrollments = relationship('Enrollment', back_populates='student')
    grades = relationship('Grade', back_populates='student')


class Enrollment(Base):
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))

    student = relationship('Student', back_populates='enrollments')
    subject = relationship('Subject', back_populates='enrollments')


class Exam(Base):
    __tablename__ = 'exams'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    name = Column(String)  # For example: 'pc1', 'pc2', 'ep', 'ef'

    subject = relationship('Subject', back_populates='exams')
    grades = relationship('Grade', back_populates='exam')


class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    exam_id = Column(Integer, ForeignKey('exams.id'))
    exam_grade = Column(Float)
    final_grade = Column(Float)

    student = relationship('Student', back_populates='grades')
    subject = relationship('Subject', back_populates='grades')
    exam = relationship('Exam', back_populates='grades')


# Create tables in the database
Base.metadata.create_all(engine)
