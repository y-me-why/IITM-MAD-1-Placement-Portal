from flask import Flask, render_template, request, redirect, url_for, flash
from flask import current_app
from .models import *


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        this_user = User.query.filter_by(email=email).first()
        if this_user.role == "admin" and this_user.password == password:
            return render_template("admin_dashboard.html")
        else:
            if this_user and this_user.password == password:
                return render_template("dashboard.html")
            else:
                flash("Invalid credentials")
                return redirect(url_for("login"))
    return render_template("login.html")

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
    return render_template("student_register.html")
    