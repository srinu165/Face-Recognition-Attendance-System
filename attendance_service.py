import os
import pandas as pd
import datetime
import sqlite3
from config import DB_PATH, ATTENDANCE_DIR

# Ensure attendance directory exists
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

def mark_attendance(student_id, subject, present=True):
    """Mark attendance for a student in a specific subject"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get current date
        today = datetime.date.today().strftime("%Y-%m-%d")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Check if student exists
        cursor.execute("SELECT name, roll_number FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            print(f"Student with ID {student_id} not found.")
            conn.close()
            return False
        
        student_name, roll_number = student
        
        # Check if subject exists
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject,))
        subject_row = cursor.fetchone()
        
        if not subject_row:
            # Create subject if it doesn't exist
            cursor.execute("INSERT INTO subjects (name) VALUES (?)", (subject,))
            conn.commit()
            subject_id = cursor.lastrowid
        else:
            subject_id = subject_row[0]
        
        # Check if attendance already marked for today
        cursor.execute(
            "SELECT id FROM attendance WHERE student_id = ? AND subject_id = ? AND date = ?",
            (student_id, subject_id, today)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing attendance
            cursor.execute(
                "UPDATE attendance SET present = ?, time = ? WHERE id = ?",
                (present, current_time, existing[0])
            )
        else:
            # Insert new attendance record
            cursor.execute(
                """
                INSERT INTO attendance 
                (student_id, subject_id, date, time, present) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (student_id, subject_id, today, current_time, present)
            )
        
        conn.commit()
        
        # Also save to CSV for backup
        subject_dir = os.path.join(ATTENDANCE_DIR, subject)
        os.makedirs(subject_dir, exist_ok=True)
        
        csv_path = os.path.join(subject_dir, f"{today}.csv")
        
        # Create or update CSV file
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Update or add student
            if roll_number in df['Roll Number'].values:
                df.loc[df['Roll Number'] == roll_number, 'Present'] = present
                df.loc[df['Roll Number'] == roll_number, 'Time'] = current_time
            else:
                new_row = pd.DataFrame({
                    'Roll Number': [roll_number],
                    'Name': [student_name],
                    'Present': [present],
                    'Time': [current_time]
                })
                df = pd.concat([df, new_row], ignore_index=True)
        else:
            # Create new CSV
            df = pd.DataFrame({
                'Roll Number': [roll_number],
                'Name': [student_name],
                'Present': [present],
                'Time': [current_time]
            })
        
        # Sort by roll number and save
        df = df.sort_values('Roll Number')
        df.to_csv(csv_path, index=False)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error marking attendance: {e}")
        return False

def get_student_attendance(student_id):
    """Get attendance percentage for a student across all subjects"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get student details
        cursor.execute("SELECT name, roll_number FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            print(f"Student with ID {student_id} not found.")
            conn.close()
            return None
        
        student_name, roll_number = student
        
        # Get all subjects
        cursor.execute("SELECT id, name FROM subjects")
        subjects = cursor.fetchall()
        
        attendance_data = []
        
        for subject_id, subject_name in subjects:
            # Count total classes for this subject
            cursor.execute(
                """
                SELECT COUNT(DISTINCT date) 
                FROM attendance 
                WHERE subject_id = ?
                """,
                (subject_id,)
            )
            total_classes = cursor.fetchone()[0]
            
            if total_classes == 0:
                continue  # Skip subjects with no classes
            
            # Count attended classes
            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM attendance 
                WHERE student_id = ? AND subject_id = ? AND present = 1
                """,
                (student_id, subject_id)
            )
            attended_classes = cursor.fetchone()[0]
            
            # Calculate percentage
            attendance_percentage = round((attended_classes / total_classes) * 100, 2) if total_classes > 0 else 0
            
            attendance_data.append({
                'subject': subject_name,
                'total_classes': total_classes,
                'attended': attended_classes,
                'percentage': attendance_percentage
            })
        
        conn.close()
        
        # Calculate overall attendance
        if attendance_data:
            total_attended = sum(item['attended'] for item in attendance_data)
            total_classes = sum(item['total_classes'] for item in attendance_data)
            overall_percentage = round((total_attended / total_classes) * 100, 2) if total_classes > 0 else 0
        else:
            overall_percentage = 0
        
        return {
            'student_name': student_name,
            'roll_number': roll_number,
            'subjects': attendance_data,
            'overall_percentage': overall_percentage
        }
        
    except Exception as e:
        print(f"Error getting student attendance: {e}")
        return None

def get_class_attendance(subject, date=None):
    """Get attendance for an entire class on a specific date"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # If date is not specified, use today's date
        if not date:
            date = datetime.date.today().strftime("%Y-%m-%d")
        
        # Get subject ID
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject,))
        subject_row = cursor.fetchone()
        
        if not subject_row:
            print(f"Subject {subject} not found.")
            conn.close()
            return None
        
        subject_id = subject_row['id']
        
        # Get attendance for this subject and date
        cursor.execute(
            """
            SELECT s.roll_number, s.name, a.present, a.time
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.subject_id = ? AND a.date = ?
            ORDER BY s.roll_number
            """,
            (subject_id, date)
        )
        attendance = cursor.fetchall()
        
        # Convert to list of dictionaries
        result = []
        for row in attendance:
            result.append({
                'roll_number': row['roll_number'],
                'name': row['name'],
                'present': bool(row['present']),
                'time': row['time']
            })
        
        conn.close()
        return result
        
    except Exception as e:
        print(f"Error getting class attendance: {e}")
        return None

def export_attendance_report(subject, start_date=None, end_date=None):
    """Export attendance report for a subject within date range"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # If dates not specified, use current month
        if not start_date or not end_date:
            today = datetime.date.today()
            start_date = datetime.date(today.year, today.month, 1).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        
        # Get subject ID
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject,))
        subject_row = cursor.fetchone()
        
        if not subject_row:
            print(f"Subject {subject} not found.")
            conn.close()
            return None
        
        subject_id = subject_row[0]
        
        # Get all students
        cursor.execute("SELECT id, roll_number, name FROM students ORDER BY roll_number")
        students = cursor.fetchall()
        
        # Get all dates within range where attendance was taken
        cursor.execute(
            """
            SELECT DISTINCT date 
            FROM attendance 
            WHERE subject_id = ? AND date BETWEEN ? AND ?
            ORDER BY date
            """,
            (subject_id, start_date, end_date)
        )
        dates = [row[0] for row in cursor.fetchall()]
        
        if not dates:
            print(f"No attendance records found for {subject} between {start_date} and {end_date}.")
            conn.close()
            return None
        
        # Create DataFrame with dates as columns
        df = pd.DataFrame(columns=['Roll Number', 'Name'] + dates + ['Percentage'])
        
        for student_id, roll_number, name in students:
            row_data = {'Roll Number': roll_number, 'Name': name}
            present_count = 0
            
            for date in dates:
                # Check if student was present on this date
                cursor.execute(
                    """
                    SELECT present 
                    FROM attendance 
                    WHERE student_id = ? AND subject_id = ? AND date = ?
                    """,
                    (student_id, subject_id, date)
                )
                result = cursor.fetchone()
                
                if result:
                    present = bool(result[0])
                    row_data[date] = 'P' if present else 'A'
                    if present:
                        present_count += 1
                else:
                    row_data[date] = '-'  # Not marked
            
            # Calculate percentage
            attendance_percentage = round((present_count / len(dates)) * 100, 2) if dates else 0
            row_data['Percentage'] = f"{attendance_percentage}%"
            
            # Add row to DataFrame
            df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
        
        # Save to CSV
        report_dir = os.path.join(ATTENDANCE_DIR, 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        file_name = f"{subject}_{start_date}_to_{end_date}.csv"
        file_path = os.path.join(report_dir, file_name)
        
        df.to_csv(file_path, index=False)
        conn.close()
        
        return file_path
        
    except Exception as e:
        print(f"Error exporting attendance report: {e}")
        return None