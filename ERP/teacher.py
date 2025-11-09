# teacher.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from __init__ import get_db_connection

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")

def teacher_required():
    return session.get("user_id") and session.get("user_role") == "teacher"

@teacher_bp.route("/dashboard")
def dashboard():
    if not teacher_required():
        flash("Teacher login required.")
        return redirect(url_for("login"))
    conn = get_db_connection()
    courses = conn.execute("SELECT * FROM courses ORDER BY name").fetchall()
    branches = conn.execute("SELECT * FROM branches ORDER BY name").fetchall()
    sections = conn.execute("SELECT * FROM sections ORDER BY name").fetchall()
    students = conn.execute("""SELECT s.*, c.name as course_name, b.name as branch_name, sec.name as section_name
                               FROM students s
                               LEFT JOIN courses c ON s.course_id = c.id
                               LEFT JOIN branches b ON s.branch_id = b.id
                               LEFT JOIN sections sec ON s.section_id = sec.id
                            ORDER BY s.name""").fetchall()
    conn.close()
    return render_template("teacher_dashboard.html", courses=courses, branches=branches, sections=sections, students=students)

# Add course/branch/section
@teacher_bp.route("/add_course", methods=["POST"])
def add_course():
    if not teacher_required():
        flash("Teacher login required.")
        return redirect(url_for("login"))
    name = request.form.get("course_name","").strip()
    if name:
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO courses (name) VALUES (?)", (name,))
            conn.commit()
            flash("Course added.")
        except:
            flash("Course may already exist.")
        finally:
            conn.close()
    return redirect(url_for("teacher.dashboard"))

@teacher_bp.route("/add_branch", methods=["POST"])
def add_branch():
    if not teacher_required():
        flash("Teacher login required.")
        return redirect(url_for("login"))
    name = request.form.get("branch_name","").strip()
    if name:
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO branches (name) VALUES (?)", (name,))
            conn.commit()
            flash("Branch added.")
        except:
            flash("Branch may already exist.")
        finally:
            conn.close()
    return redirect(url_for("teacher.dashboard"))

@teacher_bp.route("/add_section", methods=["POST"])
def add_section():
    if not teacher_required():
        flash("Teacher login required.")
        return redirect(url_for("login"))
    name = request.form.get("section_name","").strip()
    if name:
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO sections (name) VALUES (?)", (name,))
            conn.commit()
            flash("Section added.")
        except:
            flash("Section may already exist.")
        finally:
            conn.close()
    return redirect(url_for("teacher.dashboard"))

# Add student (with course/branch/section selection)
@teacher_bp.route("/add_student", methods=["GET","POST"])
def add_student():
    if not teacher_required():
        flash("Teacher login required.")
        return redirect(url_for("login"))
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form.get("name","").strip()
        roll = request.form.get("roll_no","").strip()
        course_id = request.form.get("course_id")
        branch_id = request.form.get("branch_id")
        section_id = request.form.get("section_id")
        try:
            conn.execute("INSERT INTO students (name,roll_no,course_id,branch_id,section_id) VALUES (?,?,?,?,?)",
                         (name,roll, course_id or None, branch_id or None, section_id or None))
            conn.commit()
            flash("Student added.")
            return redirect(url_for("teacher.dashboard"))
        except Exception as e:
            flash("Could not add student. Roll no may exist.")
    courses = conn.execute("SELECT * FROM courses").fetchall()
    branches = conn.execute("SELECT * FROM branches").fetchall()
    sections = conn.execute("SELECT * FROM sections").fetchall()
    conn.close()
    return render_template("add_student.html", courses=courses, branches=branches, sections=sections)

@teacher_bp.route("/remove_student/<int:sid>", methods=["GET","POST"])
def remove_student(sid):
    if not teacher_required():
        flash("Teacher login required.")
        return redirect(url_for("login"))
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    if request.method == "POST":
        conn.execute("DELETE FROM attendance WHERE student_id = ?", (sid,))
        conn.execute("DELETE FROM students WHERE id = ?", (sid,))
        conn.commit()
        conn.close()
        flash("Student removed.")
        return redirect(url_for("teacher.dashboard"))
    conn.close()
    return render_template("remove_student.html", student=student)

# API: fetch students by course/branch/section (returns JSON)
@teacher_bp.route("/students_by_filter")
def students_by_filter():
    if not teacher_required():
        return {"error":"unauthorized"}, 401
    course = request.args.get("course_id")
    branch = request.args.get("branch_id")
    section = request.args.get("section_id")
    q = "SELECT id,name,roll_no FROM students WHERE 1=1"
    params = []
    if course:
        q += " AND course_id = ?"
        params.append(course)
    if branch:
        q += " AND branch_id = ?"
        params.append(branch)
    if section:
        q += " AND section_id = ?"
        params.append(section)
    conn = get_db_connection()
    rows = conn.execute(q, params).fetchall()
    conn.close()
    data = [{"id":r["id"], "name":r["name"], "roll_no": r["roll_no"]} for r in rows]
    return jsonify(data)
