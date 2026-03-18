from flask import Flask, render_template, request, redirect, url_for, flash
from flask import current_app
from .models import *


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")
            return redirect(url_for("login"))
    return render_template("login.html")