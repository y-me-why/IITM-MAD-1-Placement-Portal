from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import current_app as app
from .models import *
from .database import db

# Authentication
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        this_user = User.query.filter_by(email=email).first()
        
        if this_user is None or this_user.password != password:
            flash("Invalid credentials")
            return redirect(url_for("login"))
            
        session["user_id"] = this_user.id
        session["role"] = this_user.role
        
        if this_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        else:
            return redirect(url_for("home"))
            
    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        password = request.form.get("password")
        email = request.form.get("email")
        role = request.form.get("role")
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register"))

        new_user = User(password=password, email=email, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        session["user_id"] = new_user.id
        session["role"] = role
        
        if role == "student":
            return redirect(url_for("student_register"))
        else:
            return redirect(url_for("company_registration"))
            
    return render_template("register.html")

@app.route("/student_register", methods=["POST", "GET"])
def student_register():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    
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
        return redirect(url_for("home"))
        
    return render_template("student_register.html")

@app.route("/company_registration", methods=["POST", "GET"])
def company_registration():
    if "user_id" not in session or session.get("role") != "company":
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    
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
        return redirect(url_for("home"))
        
    return render_template("company_register.html")

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    if session["role"] == "student":
        return redirect(url_for("student_dashboard"))
    elif session["role"] == "company":
        return redirect(url_for("company_dashboard"))
    else:
        return redirect(url_for("admin_dashboard"))



# Admin functions
@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        flash("You are not logged in")
        return redirect(url_for("login"))
        
    all_students = Student.query.all()
    all_companies = Company.query.filter_by(is_approved=True).all()
    accepted_drives = Drive.query.filter_by(approval=True).all()
    pendingApprovalDrives = Drive.query.filter_by(approval=False).all()
    all_applications = Application.query.all()
    company_requests = Company.query.filter_by(is_approved=False).all()
    
    return render_template("admin_dashboard.html", all_students=all_students, all_companies=all_companies, accepted_drives=accepted_drives, pendingApprovalDrives=pendingApprovalDrives, all_applications=all_applications, company_requests=company_requests)

@app.route("/company_status/<int:company_id>")
def company_status(company_id):
    if session.get("role") != "admin": return redirect(url_for("login"))
    this_company = Company.query.filter_by(company_id=company_id).first()
    selected_option = request.form.get("selected_option")
    if this_company and selected_option == "approve":
        this_company.is_approved = True
        db.session.commit()
    elif this_company and selected_option == "reject":
        this_company.is_approved = False
        db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/blacklist_user/<int:user_id>")
def blacklist_user(user_id):
    if session.get("role") != "admin": return redirect(url_for("login"))
    this_user = User.query.filter_by(id=user_id).first()
    if this_user:
        this_user.is_blacklisted = True
        db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/unblacklist_user/<int:user_id>")
def unblacklist_user(user_id):
    if session.get("role") != "admin": return redirect(url_for("login"))
    this_user = User.query.filter_by(id=user_id).first()
    if this_user:
        this_user.is_blacklisted = False
        db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/search", methods=["POST", "GET"])
def search():
    user_id = session.get("user_id")
    role = session.get("role")
    if role != "admin": return redirect(url_for("login"))
    if request.method == "POST":
        search_word = request.form.get("search_word")
        key = request.form.get("key")
        if key == "company":
            found_companies = Company.query.filter(Company.name.ilike(f"%{search_word}%")).all()
            return render_template("result.html", results=found_companies)
        elif key == "student":
            found_students = Student.query.filter(Student.name.ilike(f"%{search_word}%")).all()
            return render_template("result.html", results=found_students)
    return redirect(url_for("admin_dashboard"))

@app.route("/drive_status/<int:drive_id>")
def drive_status(drive_id):
    if session.get("role") != "admin": return redirect(url_for("login"))
    this_drive = Drive.query.filter_by(id=drive_id).first()
    selected_option = request.form.get("selected_option")
    if this_drive and selected_option == "approve":
        this_drive.approval = True 
        db.session.commit()
    elif this_drive and selected_option == "reject":
        this_drive.approval = False
        db.session.commit()
    return redirect(request.referrer or url_for("admin_dashboard"))




# Company functions
@app.route("/company_dashboard")
def company_dashboard():
    if "user_id" not in session or session.get("role") != "company":
        return redirect(url_for("login"))
        
    company_id = session["user_id"]
    this_company = Company.query.filter_by(company_id=company_id).first()
    this_user = User.query.filter_by(id=company_id).first()
    
    if not this_company.is_approved or this_user.is_blacklisted:
        flash("Your account is pending admin approval or has been blacklisted.")
        return render_template("waiting_approval.html") 
        
    all_drives = Drive.query.filter_by(company_id=company_id).all()
    return render_template("company_dashboard.html", all_drives=all_drives, company=this_company)

@app.route("/create_drive", methods=["POST", "GET"])
def create_drive():
    if "user_id" not in session or session.get("role") != "company": return redirect(url_for("login"))
    company_id = session["user_id"]
    this_user = User.query.filter_by(id=company_id).first()
    this_company = Company.query.filter_by(company_id=company_id).first()
    
    if not this_company.is_approved or this_user.is_blacklisted: return redirect(url_for("company_dashboard"))
        
    if request.method == "POST":
        drive_name = request.form.get("drive_name")
        job_title = request.form.get("job_title")
        description = request.form.get("description")
        eligibility = request.form.get("eligibility")
        status = request.form.get("status")
        
        from datetime import datetime
        deadline_str = request.form.get("deadline")
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')

        new_drive = Drive(company_id=company_id, drive_name=drive_name, job_title=job_title, description=description, eligibility=eligibility, deadline=deadline, status=status)
        db.session.add(new_drive)
        db.session.commit()
        return redirect(url_for("company_dashboard"))
        
    return render_template("create_drive.html")

@app.route("/view_applications/<int:drive_id>")
def view_applications(drive_id):
    if session.get("role") != "company": return redirect(url_for("login"))
    this_drive = Drive.query.filter_by(id=drive_id).first()
    if this_drive and this_drive.company_id == session["user_id"]:
        applications = Application.query.filter_by(drive_id=drive_id).all()
        return render_template("view_applications.html", applications=applications)
    return redirect(url_for("company_dashboard"))

@app.route("/update_application/<int:application_id>", methods=["POST"])
def update_application(application_id):
    if session.get("role") != "company": return redirect(url_for("login"))
    this_application = Application.query.get(application_id)
    
    if this_application and this_application.drive.company_id == session["user_id"]:
        this_application.company_status = request.form.get("status")
        db.session.commit()
    return redirect(url_for("company_dashboard"))

@app.route("/edit_drive/<int:drive_id>", methods=["POST", "GET"])
def edit_drive(drive_id):
    if session.get("role") != "company": return redirect(url_for("login"))
    this_drive = Drive.query.filter_by(id=drive_id).first()
    
    if not this_drive or this_drive.company_id != session["user_id"]:
        flash("Unauthorized access")
        return redirect(url_for("company_dashboard"))

    if request.method == "POST":
        this_drive.drive_name = request.form.get("drive_name")
        this_drive.job_title = request.form.get("job_title")
        this_drive.description = request.form.get("description")
        this_drive.eligibility = request.form.get("eligibility")
        this_drive.status = request.form.get("status") 
        db.session.commit()
        return redirect(url_for("company_dashboard"))
        
    return render_template("edit_drive.html", drive=this_drive)

@app.route("/delete_drive/<int:drive_id>")
def delete_drive(drive_id):
    if session.get("role") != "company": return redirect(url_for("login"))
    this_drive = Drive.query.filter_by(id=drive_id).first()
    
    if this_drive and this_drive.company_id == session["user_id"]:
        Application.query.filter_by(drive_id=drive_id).delete()
        db.session.delete(this_drive)
        db.session.commit()
        
    return redirect(url_for("company_dashboard"))




# Student functions
@app.route("/student_dashboard")
def student_dashboard():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))
        
    student_id = session["user_id"]
    this_student = Student.query.filter_by(student_id=student_id).first()
    this_user = User.query.filter_by(id=student_id).first()
    
    if this_user.is_blacklisted:
        flash("Your account has been blacklisted.")
        return render_template("blacklisted.html")
 
    applied_drives_subquery = [app.drive_id for app in Application.query.filter_by(student_id=student_id).all()]
    
    available_drives = Drive.query.filter(
        Drive.status.in_(["Upcoming", "Ongoing"]), 
        Drive.approval == True, 
        Drive.id.notin_(applied_drives_subquery)
    ).all()
    
    applied_history = Application.query.filter_by(student_id=student_id).all()
    
    return render_template("student_dashboard.html", student=this_student, available_drives=available_drives, applied_history=applied_history)

@app.route("/apply_drive/<int:drive_id>", methods=["POST"])
def apply_drive(drive_id):
    user_id = session.get("user_id")
    this_user = User.query.filter_by(id=user_id).first()
    if session.get("role") != "student" or this_user.is_blacklisted: return redirect(url_for("login"))
    student_id = session["user_id"]
    
    existing_app = Application.query.filter_by(student_id=student_id, drive_id=drive_id).first()
    this_drive = Drive.query.filter_by(id=drive_id).first()

    if not this_drive or this_drive.approval == False:
        flash("Drive does not exist")
        return redirect(url_for("student_dashboard"))
    if this_drive.status == "Closed":
        flash("Drive is closed")
        return redirect(url_for("student_dashboard"))

    if not existing_app:
        new_application = Application(student_id=student_id, drive_id=drive_id)
        db.session.add(new_application)
        db.session.commit()
        flash("Application successful!")
        
    return redirect(request.referrer or url_for("student_dashboard"))

@app.route("/update_student_profile", methods=["POST", "GET"])
def update_student_profile():
    user_id = session.get("user_id")
    this_user = User.query.filter_by(id=user_id).first()
    if session.get("role") != "student" or this_user.is_blacklisted: return redirect(url_for("login"))
    student_id = session["user_id"]
    this_student = Student.query.filter_by(student_id=student_id).first()
    
    if request.method == "POST":
        this_student.name = request.form.get("name")
        this_student.resume = request.form.get("resume")
        this_student.about = request.form.get("about")
        db.session.commit()
        flash("Profile updated")
        return redirect(url_for("student_dashboard"))
        
    return render_template("update_student_profile.html", student=this_student)