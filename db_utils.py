import sqlite3
import os
import uuid
import pandas as pd
from config import DB_PATH

def create_database():
    """Create the database and necessary tables, including a default admin account."""
    try:
        # Connect to the database (creates it if it doesn't exist)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                roll_number TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                department TEXT,
                year TEXT,
                section TEXT,
                face_registered INTEGER DEFAULT 0
            )
        """)

        # Create subjects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                department TEXT,
                year TEXT,
                semester TEXT,
                created_date TEXT DEFAULT (date('now'))
            )
        """)

        # Create attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                subject_id INTEGER,
                date TEXT,
                time TEXT,
                present INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)

        # Create admins table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL
            )
        """)

        # Check if default admin exists
        cursor.execute("SELECT username FROM admins WHERE username = ?", ('admin',))
        if not cursor.fetchone():
            # Insert default admin account
            default_admin = {
                'id': str(uuid.uuid4()),
                'username': 'admin',
                'password': 'admin123',
                'name': 'Administrator'
            }
            cursor.execute("""
                INSERT INTO admins (id, username, password, name)
                VALUES (?, ?, ?, ?)
            """, (
                default_admin['id'],
                default_admin['username'],
                default_admin['password'],
                default_admin['name']
            ))

        # Commit changes and close connection
        conn.commit()
        conn.close()
        print("Database initialized successfully with default admin account.")
    except Exception as e:
        print(f"Error creating database: {e}")

def get_student_by_credentials(roll_number, password):
    """Retrieve student by roll number and password."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE roll_number = ? AND password = ?",
            (roll_number, password)
        )
        student = cursor.fetchone()
        conn.close()
        return dict(student) if student else None
    except Exception as e:
        print(f"Error retrieving student: {e}")
        return None

def get_admin_by_credentials(username, password):
    """Retrieve admin by username and password."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admins WHERE username = ? AND password = ?",
            (username, password)
        )
        admin = cursor.fetchone()
        conn.close()
        return dict(admin) if admin else None
    except Exception as e:
        print(f"Error retrieving admin: {e}")
        return None

def add_student(student_id, name, roll_number, password, email, department, year, section, face_registered):
    """Add a new student to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (id, name, roll_number, password, email, department, year, section, face_registered)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, name, roll_number, password, email, department, year, section, face_registered))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding student: {e}")
        return False

def update_student_face_status(student_id, face_registered):
    """Update the face registration status of a student."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET face_registered = ? WHERE id = ?",
            (face_registered, student_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating student face status: {e}")
        return False

def get_all_students():
    """Retrieve all students."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY roll_number")
        students = cursor.fetchall()
        conn.close()
        return [dict(student) for student in students]
    except Exception as e:
        print(f"Error retrieving students: {e}")
        return []

def get_all_subjects():
    """Retrieve all subjects."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects ORDER BY name")
        subjects = cursor.fetchall()
        conn.close()
        return [dict(subject) for subject in subjects]
    except Exception as e:
        print(f"Error retrieving subjects: {e}")
        return []

def add_subject(name, department, year, semester):
    """Add a new subject to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subjects (name, department, year, semester)
            VALUES (?, ?, ?, ?)
        """, (name, department, year, semester))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding subject: {e}")
        return False

def import_students_from_csv(file_path):
    """Import students from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for _, row in df.iterrows():
            student_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT OR IGNORE INTO students (id, name, roll_number, password, email, department, year, section, face_registered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                row.get('name', ''),
                row.get('roll_number', ''),
                row.get('password', 'default123'),  # Default password if not provided
                row.get('email', ''),
                row.get('department', ''),
                row.get('year', ''),
                row.get('section', ''),
                0
            ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error importing students: {e}")
        return False