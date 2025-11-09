# database.py

# 👇 yahan se relative import hata de, direct import use kar
from __init__ import get_db_connection

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('teacher','student')) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS branches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        course_id INTEGER,
        branch_id INTEGER,
        section_id INTEGER,
        FOREIGN KEY(course_id) REFERENCES courses(id),
        FOREIGN KEY(branch_id) REFERENCES branches(id),
        FOREIGN KEY(section_id) REFERENCES sections(id)
    );

    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT CHECK(status IN ('Present','Absent','Late')) NOT NULL,
        remarks TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    );
    """)

    conn.commit()

    # 👇 seed default teacher + student and sample data
    try:
        cur = conn.cursor()

        # default users
        cur.execute("SELECT id FROM users WHERE email = ?", ("teacher@erp.local",))
        if not cur.fetchone():
            cur.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                        ("Main Teacher","teacher@erp.local","teacher123","teacher"))

        cur.execute("SELECT id FROM users WHERE email = ?", ("student@erp.local",))
        if not cur.fetchone():
            cur.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                        ("Demo Student","student@erp.local","student123","student"))

        # sample course/branch/section
        cur.execute("INSERT OR IGNORE INTO courses (name) VALUES (?)", ("BTech",))
        cur.execute("INSERT OR IGNORE INTO branches (name) VALUES (?)", ("CSE",))
        cur.execute("INSERT OR IGNORE INTO sections (name) VALUES (?)", ("A",))

        # find ids
        cur.execute("SELECT id FROM courses WHERE name=?", ("BTech",))
        course_id = cur.fetchone()[0]
        cur.execute("SELECT id FROM branches WHERE name=?", ("CSE",))
        branch_id = cur.fetchone()[0]
        cur.execute("SELECT id FROM sections WHERE name=?", ("A",))
        section_id = cur.fetchone()[0]

        # sample student
        cur.execute("SELECT id FROM students WHERE roll_no = ?", ("S101",))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO students (name, roll_no, course_id, branch_id, section_id)
                VALUES (?,?,?,?,?)
            """, ("Demo Student", "S101", course_id, branch_id, section_id))

        conn.commit()

    except Exception as e:
        print("Seeding error:", e)
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("ERP.db initialized.")
