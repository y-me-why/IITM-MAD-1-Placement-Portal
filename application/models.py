from .database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)

class Student(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    name = db.Column(db.String(80), nullable = False)
    yoe = db.Column(db.Integer, nullable=False)
    resume = db.Column(db.String(255), nullable=True) 
    about = db.Column(db.String(255), nullable=True)

class Company(db.Model):
    company_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    cin = db.Column(db.String(21), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)

class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.company_id"), nullable=False)
    drive_name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="Upcoming")
    approval = db.Column(db.Boolean, default=False)

    company = db.relationship('Company', backref='drives')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("drive.id"), nullable=False)
    student_status = db.Column(db.String(20), default="Applied")
    company_status = db.Column(db.String(20), default="Pending")

    drive = db.relationship('Drive', backref='applications')
    student = db.relationship('Student', backref='applications')


class CompanyPhone(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.company_id"), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

class CompanyAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.company_id"), nullable=False)
    address = db.Column(db.String(255), nullable=False)