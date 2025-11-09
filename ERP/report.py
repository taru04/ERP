# report.py
from flask import Blueprint, render_template, request, send_file, session, redirect, url_for, flash
from __init__ import get_db_connection
import io, csv

report_bp = Blueprint("report", __name__, url_prefix="")

def login_required():
    return session.get("user_id")

@report_bp.route("/report")
def view_report():
    if not login_required():
        flash("Please login.")
        return redirect(url_for("login"))
    conn = get_db_connection()
    rows = conn.execute("""SELECT s.name, s.roll_no, a.date, a.status, a.remarks
                           FROM attendance a JOIN students s ON a.student_id = s.id
                           ORDER BY a.date DESC""").fetchall()
    conn.close()
    return render_template("report.html", rows=rows)

@report_bp.route("/report/export")
def export_report():
    if not login_required():
        flash("Please login.")
        return redirect(url_for("login"))
    t = request.args.get("type","csv")
    conn = get_db_connection()
    rows = conn.execute("""SELECT s.name, s.roll_no, a.date, a.status, a.remarks
                           FROM attendance a JOIN students s ON a.student_id = s.id
                           ORDER BY a.date DESC""").fetchall()
    conn.close()

    # CSV always available
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name","Roll No","Date","Status","Remarks"])
    for r in rows:
        writer.writerow([r["name"], r["roll_no"], r["date"], r["status"], r["remarks"]])
    csv_data = output.getvalue().encode("utf-8")
    return send_file(io.BytesIO(csv_data), mimetype="text/csv", as_attachment=True, download_name="attendance_report.csv")
