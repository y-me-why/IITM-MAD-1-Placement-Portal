from flask import Flask, render_template, request, redirect, url_for, flash
from flask import current_app as app
from .models import *


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        this_user = User.query.filter_by(email=email).first()
        if this_user.role == "admin" and this_user.password == password:
            return redirect("/admin_dashboard", user_id = this_user.id)
        else:
            if this_user and this_user.password == password:
                return redirect(url_for("home", user_id = this_user.id))
            else:
                flash("Invalid credentials")
                return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/admin_dashboard/<int:user_id>")
def admin_dashboard(user_id):
    this_user = User.query.filter_by(id=user_id).first()
    if this_user.role != "admin":
        flash("You are not authorized to access this page")
        return redirect(url_for("login"))
    all_students = Student.query.all()
    all_companies = Company.query.filter_by(is_approved = true).all()
    all_drives = Drive.query.all()
    all_applications = Application.query.all()
    company_requests = Company.query.filter_by(is_approved = false).all()
    return render_template("admin_dashboard.html", all_students = all_students, all_companies = all_companies, all_drives = all_drives, all_applications = all_applications, company_requests = company_requests)


@app.route("/home/<int:user_id>")
def home(user_id):
    this_user = User.query.filter_by(id=user_id).first()
    if this_user.role == "student":
        return render_template("home.html", user_id = user_id)
    else:
        return render_template("home.html", user_id = user_id)

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        password = request.form.get("password")
        email = request.form.get("email")
        role = request.form.get("role")
        new_user = User(password=password, email=email, role=role)
        db.session.add(new_user)
        db.session.commit()
        if role == "student":
            return render_template("student_register.html", user_id = new_user.id)
        else:
            return render_template("company_register.html", user_id = new_user.id)
    return render_template("register.html")

@app.route("/student_register/<int:user_id>", methods=["POST", "GET"])
def student_register(user_id):
    if request.method == "POST":
        name = request.form.get("name")
        yoe = request.form.get("yoe")
        resume = request.form.get("resume")
        about = request.form.get("about")
        new_student = Student(student_id=user_id, name=name, yoe=yoe, resume=resume, about=about)
        db.session.add(new_student)

        phones = request.form.getlist('phone')
        for phone in phones:
            if phone.strip():
                new_phone = StudentPhone(student_id=user_id, phone=phone)
                db.session.add(new_phone)
        db.session.commit()
        return redirect(url_for("login"))

@app.route("/company_registration/<int:user_id>", methods=["POST", "GET"])
def company_registration(user_id):
    if request.method == "POST":
        name = request.form.get("name")
        website = request.form.get("website")
        cin = request.form.get("cin")
        new_company = Company(company_id=user_id, name=name, website=website, cin=cin)
        db.session.add(new_company)

        phones = request.form.getlist('phone')
        for phone in phones:
            if phone.strip():
                new_phone = CompanyPhone(company_id=user_id, phone=phone)
                db.session.add(new_phone)
        addresses = request.form.getlist("address")
        for address in addresses:
            if address.strip():
                new_address = CompanyAddress(company_id=user_id, address=address)
                db.session.add(new_address)
        db.session.commit()
        return redirect(url_for("login"))
    