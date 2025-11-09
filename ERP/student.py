# student.py
from flask import Blueprint, render_template, session, redirect, url_for, flash
from __init__ import get_db_connection

student_bp = Blueprint("student", __name__, url_prefix="/student")

def student_required():
    return session.get("user_id") and session.get("user_role") == "student"

@student_bp.route("/dashboard")
def dashboard():
    if not student_required():
        flash("Student login required.")
        return redirect(url_for("login"))
    # find student by linked email or name - simple heuristic: match user_name to student.name or email prefix to roll_no
    conn = get_db_connection()
    user_name = session.get("user_name")
    user_email = session.get("user_email")
    roll_guess = user_email.split("@")[0].upper() if user_email else None
    student = None
    if user_name:
        student = conn.execute("SELECT * FROM students WHERE name = ?", (user_name,)).fetchone()
    if not student and roll_guess:
        student = conn.execute("SELECT * FROM students WHERE roll_no = ?", (roll_guess,)).fetchone()

    if not student:
        # fallback: if student not mapped, show message and all attendance (teacher should map)
        rows = conn.execute("""SELECT a.date, a.status, a.remarks, s.name, s.roll_no
                               FROM attendance a JOIN students s ON a.student_id = s.id
                               ORDER BY a.date DESC""").fetchall()
        conn.close()
        flash("Your student record not linked. Contact teacher.")
        return render_template("student_dashboard.html", rows=rows, mapped=False)
    # get attendance for this student
    rows = conn.execute("SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC", (student["id"],)).fetchall()
    conn.close()
    return render_template("student_dashboard.html", rows=rows, mapped=True, student=student)
