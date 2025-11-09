# attendance.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from __init__ import get_db_connection
from datetime import date

attendance_bp = Blueprint("attendance", __name__, url_prefix="")

def teacher_required():
    return session.get("user_id") and session.get("user_role") == "teacher"

@attendance_bp.route("/mark_attendance", methods=["GET","POST"])
def mark_attendance():
    if not teacher_required():
        flash("Teacher login required.")
        return redirect(url_for("login"))
    conn = get_db_connection()
    courses = conn.execute("SELECT * FROM courses").fetchall()
    branches = conn.execute("SELECT * FROM branches").fetchall()
    sections = conn.execute("SELECT * FROM sections").fetchall()

    if request.method == "POST":
        course_id = request.form.get("course_id")
        branch_id = request.form.get("branch_id")
        section_id = request.form.get("section_id")
        attend_date = request.form.get("date") or date.today().isoformat()
        # find students matching filter
        q = "SELECT * FROM students WHERE 1=1"
        params = []
        if course_id:
            q += " AND course_id = ?"
            params.append(course_id)
        if branch_id:
            q += " AND branch_id = ?"
            params.append(branch_id)
        if section_id:
            q += " AND section_id = ?"
            params.append(section_id)
        students = conn.execute(q, params).fetchall()
        # For each student, get status field value
        for s in students:
            status = request.form.get(f"status_{s['id']}", "Absent")
            remarks = request.form.get(f"remarks_{s['id']}", "")
            # check if attendance for same student & date exists -> update else insert
            exists = conn.execute("SELECT id FROM attendance WHERE student_id = ? AND date = ?", (s["id"], attend_date)).fetchone()
            if exists:
                conn.execute("UPDATE attendance SET status = ?, remarks = ? WHERE id = ?", (status, remarks, exists["id"]))
            else:
                conn.execute("INSERT INTO attendance (student_id,date,status,remarks) VALUES (?,?,?,?)",
                             (s["id"], attend_date, status, remarks))
        conn.commit()
        conn.close()
        flash("Attendance saved/updated for selected group.")
        return redirect(url_for("teacher.dashboard"))

    conn.close()
    return render_template("mark_attendance.html", courses=courses, branches=branches, sections=sections)

@attendance_bp.route("/edit_attendance/<int:att_id>", methods=["GET","POST"])
def edit_attendance(att_id):
    if not teacher_required():
        flash("Teacher login required.")
        return redirect(url_for("login"))
    conn = get_db_connection()
    att = conn.execute("""SELECT a.id, a.student_id, a.date, a.status, a.remarks, s.name, s.roll_no
                         FROM attendance a JOIN students s ON a.student_id = s.id WHERE a.id = ?""", (att_id,)).fetchone()
    if not att:
        conn.close()
        flash("Record not found.")
        return redirect(url_for("teacher.dashboard"))
    if request.method == "POST":
        status = request.form.get("status")
        remarks = request.form.get("remarks","")
        conn.execute("UPDATE attendance SET status = ?, remarks = ? WHERE id = ?", (status,remarks,att_id))
        conn.commit()
        conn.close()
        flash("Attendance updated.")
        return redirect(url_for("teacher.dashboard"))
    conn.close()
    return render_template("edit_attendance.html", att=att)
