
from flask import Flask, render_template, request, redirect, url_for, session, flash
from __init__ import create_app, get_db_connection
import database
from teacher import teacher_bp
from student import student_bp
from attendance import attendance_bp
from report import report_bp

app = create_app()
database.init_db()

app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(report_bp)

@app.route("/")
def index():
    if session.get("user_id"):
        if session.get("user_role") == "teacher":
            return redirect(url_for("teacher.dashboard"))
        else:
            return redirect(url_for("student.dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip()
        password = request.form.get("password","").strip()
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]
            flash("Logged in as " + user["role"])
            if user["role"] == "teacher":
                return redirect(url_for("teacher.dashboard"))
            return redirect(url_for("student.dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    # only allow student registration here
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        password = request.form.get("password","").strip()
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                         (name,email,password,"student"))
            # create a basic student record (roll_no as email prefix)
            roll = email.split("@")[0].upper()
            conn.execute("INSERT OR IGNORE INTO students (name,roll_no) VALUES (?,?)",(name,roll))
            conn.commit()
            flash("Registered. Please login.")
            return redirect(url_for("login"))
        except Exception as e:
            flash("Could not register. Email may already exist.")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
