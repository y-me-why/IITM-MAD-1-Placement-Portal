from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import current_app as app
from .models import *


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        this_user = User.query.filter_by(email=email).first()
        if this_user is None:
            flash("Invalid credentials")
            return redirect(url_for("login"))
        else:    
            if this_user.role == "admin" and this_user.password == password:
                session["user_id"] = this_user.id
                session["role"] = this_user.role
                return redirect("/admin_dashboard")
            else:
                if this_user.password == password:
                    session["user_id"] = this_user.id
                    session["role"] = this_user.role
                    return redirect(url_for("home"))
                else:
                    flash("Invalid credentials")
                    return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    user_id = session["user_id"]
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
        
    @app.route("/approve_company/<int:company_id>")
    def approve_company(company_id):
        user_id = session["user_id"]
        this_user = User.query.filter_by(id=user_id).first()
        if this_user.role != "admin":
            flash("You are not authorized to access this page")
            return redirect(url_for("login"))
        this_company = Company.query.filter_by(id=company_id).first()
        if this_company is None:
            flash("Company not found")
            return redirect(url_for("admin_dashboard"))
        this_company.is_approved = true
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
        
    @app.route("/reject_company/<int:company_id>")
    def reject_company(company_id):
        user_id = session["user_id"]
        this_user = User.query.filter_by(id=user_id).first()
        if this_user.role != "admin":
            flash("You are not authorized to access this page")
            return redirect(url_for("login"))
        this_company = Company.query.filter_by(id=company_id).first()
        if this_company is None:
            flash("Company not found")
            return redirect(url_for("admin_dashboard"))
        this_company.is_approved = false
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

    @app.route("/blacklist_company/<int:company_id>")
    def blacklist_company(company_id):
        user_id = session["user_id"]
        this_user = User.query.filter_by(id=user_id).first()
        if this_user.role != "admin":
            flash("You are not authorized to access this page")
            return redirect(url_for("login"))
        this_company = Company.query.filter_by(id=company_id).first()
        if this_company is None:
            flash("Company not found")
            return redirect(url_for("admin_dashboard"))
        this_company.is_blacklisted = true
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

    @app.route("/unblacklist_company/<int:company_id>")
    def unblacklist_company(company_id):
        user_id = session["user_id"]
        this_user = User.query.filter_by(id=user_id).first()
        if this_user.role != "admin":
            flash("You are not authorized to access this page")
            return redirect(url_for("login"))
        this_company = Company.query.filter_by(id=company_id).first()
        if this_company is None:
            flash("Company not found")
            return redirect(url_for("admin_dashboard"))
        this_company.is_blacklisted = false
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

    @app.route("/blacklist_student/<int:student_id>")
    def blacklist_student(student_id):
        user_id = session["user_id"]
        this_user = User.query.filter_by(id=user_id).first()
        if this_user.role != "admin":
            flash("You are not authorized to access this page")
            return redirect(url_for("login"))
        this_student = Student.query.filter_by(id=student_id).first()
        if this_student is None:
            flash("Student not found")
            return redirect(url_for("admin_dashboard"))
        this_student.is_blacklisted = true
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

    @app.route("/unblacklist_student/<int:student_id>")
    def unblacklist_student(student_id):
        user_id = session["user_id"]
        this_user = User.query.filter_by(id=user_id).first()
        if this_user.role != "admin":
            flash("You are not authorized to access this page")
            return redirect(url_for("login"))
        this_student = Student.query.filter_by(id=student_id).first()
        if this_student is None:
            flash("Student not found")
            return redirect(url_for("admin_dashboard"))
        this_student.is_blacklisted = false
        db.session.commit()
        return redirect(url_for("admin_dashboard")) 

@app.route("/home/<int:user_id>")
def home(user_id):
    this_user = User.query.filter_by(id=user_id).first()
    if this_user.role == "student":
        return render_template("student_dashboard.html", user_id = user_id)
    else:
        return render_template("company_dashboard.html", user_id = user_id)

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

@app.route("/create_drive/<int:company_id>", methods=["POST", "GET"])
def create_drive(company_id):
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        new_drive = Drive(company_id=company_id, name=name, description=description, start_date=start_date, end_date=end_date)
        db.session.add(new_drive)
        db.session.commit()
        return redirect(url_for("company_dashboard", company_id=company_id))
    return render_template("create_drive.html", company_id=company_id)

@app.route("/company_dashboard/<int:company_id>")
def company_dashboard(company_id):
    this_company = Company.query.filter_by(id=company_id).first()
    if this_company.is_approved == false:
        flash("You are not approved yet")
        return redirect(url_for("login"))
    all_drives = Drive.query.filter_by(company_id=company_id).all()
    return render_template("company_dashboard.html", all_drives = all_drives, company_id=company_id)

@app.route("student_dashboard/<int:student_id>")
def student_dashboard(student_id):
    this_student = Student.query.filter_by(id=student_id).first()
    if this_student.is_blacklisted == true:
        flash("You are blacklisted")
        return redirect(url_for("login"))
    all_drives = Drive.query.all()
    return render_template("student_dashboard.html", all_drives = all_drives, student_id=student_id)
