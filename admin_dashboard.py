import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from db_utils import get_all_students, get_all_subjects, add_subject, import_students_from_csv
from attendance_service import get_class_attendance, export_attendance_report

class AdminDashboard:
    def __init__(self, root, back_callback, admin, text_to_speech=None):
        self.root = root
        self.back_callback = back_callback
        self.admin = admin
        self.text_to_speech = text_to_speech
        
        # Set window title
        self.root.title(f"Admin Dashboard - {admin['name']}")
        
        # Configure root window
        self.setup_ui()
    
    def setup_ui(self):
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Create tabs
        self.dashboard_tab = tk.Frame(self.notebook, bg="white")
        self.students_tab = tk.Frame(self.notebook, bg="white")
        self.attendance_tab = tk.Frame(self.notebook, bg="white")
        self.subjects_tab = tk.Frame(self.notebook, bg="white")
        self.reports_tab = tk.Frame(self.notebook, bg="white")
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.students_tab, text="Students")
        self.notebook.add(self.attendance_tab, text="Attendance")
        self.notebook.add(self.subjects_tab, text="Subjects")
        self.notebook.add(self.reports_tab, text="Reports")
        
        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_students_tab()
        self.setup_attendance_tab()
        self.setup_subjects_tab()
        self.setup_reports_tab()
        
        # Footer frame
        self.footer_frame = tk.Frame(self.root, bg="#f5f5f5", pady=10)
        self.footer_frame.pack(fill=X, side=BOTTOM)
        
        # Logout button
        self.logout_btn = tk.Button(
            self.footer_frame,
            text="Logout",
            command=self.back_callback,
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            width=10,
            bd=0,
            cursor="hand2"
        )
        self.logout_btn.pack(side=RIGHT, padx=20)
    
    def setup_dashboard_tab(self):
        """Setup the dashboard tab with summary information"""
        # Header frame
        header_frame = tk.Frame(self.dashboard_tab, bg="#0d47a1", pady=15)
        header_frame.pack(fill=X)
        
        # Title and welcome message
        title_label = tk.Label(
            header_frame,
            text=f"Welcome, {self.admin['name']}",
            font=("Arial", 20, "bold"),
            bg="#0d47a1",
            fg="white"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Admin Dashboard",
            font=("Arial", 14),
            bg="#0d47a1",
            fg="white"
        )
        subtitle_label.pack(pady=5)
        
        # Content frame
        content_frame = tk.Frame(self.dashboard_tab, bg="white", pady=20)
        content_frame.pack(fill=BOTH, expand=True, padx=20)
        
        # Summary cards frame
        summary_frame = tk.Frame(content_frame, bg="white")
        summary_frame.pack(fill=X, pady=20)
        
        # Create summary cards (will be populated with actual data)
        self.create_summary_card(summary_frame, "Total Students", "0", "#2196f3", 0)
        self.create_summary_card(summary_frame, "Total Subjects", "0", "#4caf50", 1)
        self.create_summary_card(summary_frame, "Today's Attendance", "0%", "#ff9800", 2)
        
        # Recent activity frame
        activity_frame = tk.LabelFrame(
            content_frame,
            text="Recent Activity",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        activity_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Placeholder for recent activity
        self.activity_tree = ttk.Treeview(
            activity_frame,
            columns=("date", "time", "action", "details"),
            show="headings",
            height=8
        )
        
        # Define headings
        self.activity_tree.heading("date", text="Date")
        self.activity_tree.heading("time", text="Time")
        self.activity_tree.heading("action", text="Action")
        self.activity_tree.heading("details", text="Details")
        
        # Define columns
        self.activity_tree.column("date", width=100, anchor=CENTER)
        self.activity_tree.column("time", width=100, anchor=CENTER)
        self.activity_tree.column("action", width=150, anchor=W)
        self.activity_tree.column("details", width=300, anchor=W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            activity_frame,
            orient=VERTICAL,
            command=self.activity_tree.yview
        )
        self.activity_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.activity_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Populate with sample data
        today = datetime.date.today().strftime("%Y-%m-%d")
        time_now = datetime.datetime.now().strftime("%H:%M:%S")
        
        sample_activities = [
            (today, time_now, "Login", "Admin user logged in"),
            (today, time_now, "System", "Dashboard initialized"),
        ]
        
        for activity in sample_activities:
            self.activity_tree.insert("", END, values=activity)
        
        # Load actual data to update the summary cards
        self.load_dashboard_data()
    
    def create_summary_card(self, parent, title, value, color, column):
        """Create a summary card for the dashboard"""
        card_frame = tk.Frame(
            parent,
            bg=color,
            padx=15,
            pady=15,
            width=200,
            height=120
        )
        card_frame.grid(row=0, column=column, padx=10)
        card_frame.pack_propagate(False)  # Don't shrink
        
        # Title
        title_label = tk.Label(
            card_frame,
            text=title,
            font=("Arial", 14),
            bg=color,
            fg="white"
        )
        title_label.pack(anchor=W)
        
        # Value
        value_label = tk.Label(
            card_frame,
            text=value,
            font=("Arial", 28, "bold"),
            bg=color,
            fg="white"
        )
        value_label.pack(expand=True)
    
    def load_dashboard_data(self):
        """Load actual data for the dashboard"""
        # Get all students
        students = get_all_students()
        student_count = len(students)
        
        # Get all subjects
        subjects = get_all_subjects()
        subject_count = len(subjects)
        
        # Update summary cards
        summary_frame = self.dashboard_tab.winfo_children()[1].winfo_children()[0]
        
        # Update student count
        student_card = summary_frame.winfo_children()[0]
        student_card.winfo_children()[1].config(text=str(student_count))
        
        # Update subject count
        subject_card = summary_frame.winfo_children()[1]
        subject_card.winfo_children()[1].config(text=str(subject_count))
    
    def setup_students_tab(self):
        """Setup the students tab"""
        # Header frame
        header_frame = tk.Frame(self.students_tab, bg="#0d47a1", pady=15)
        header_frame.pack(fill=X)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Student Management",
            font=("Arial", 18, "bold"),
            bg="#0d47a1",
            fg="white"
        )
        title_label.pack()
        
        # Content frame
        content_frame = tk.Frame(self.students_tab, bg="white", pady=20)
        content_frame.pack(fill=BOTH, expand=True, padx=20)
        
        # Action buttons frame
        action_frame = tk.Frame(content_frame, bg="white")
        action_frame.pack(fill=X, pady=10)
        
        # Add student button
        add_student_btn = tk.Button(
            action_frame,
            text="Add New Student",
            command=self.back_callback,  # This will take us to registration page
            font=("Arial", 12),
            bg="#4caf50",
            fg="white",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        add_student_btn.pack(side=LEFT, padx=5)
        
        # Import students button
        import_students_btn = tk.Button(
            action_frame,
            text="Import Students (CSV)",
            command=self.import_students,
            font=("Arial", 12),
            bg="#2196f3",
            fg="white",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        import_students_btn.pack(side=LEFT, padx=5)
        
        # Search frame
        search_frame = tk.Frame(content_frame, bg="white", pady=10)
        search_frame.pack(fill=X)
        
        # Search entry
        search_label = tk.Label(
            search_frame,
            text="Search:",
            font=("Arial", 12),
            bg="white"
        )
        search_label.pack(side=LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief=GROOVE
        )
        search_entry.pack(side=LEFT, padx=5)
        
        # Search button
        search_btn = tk.Button(
            search_frame,
            text="Search",
            command=self.search_students,
            font=("Arial", 12),
            bg="#f5f5f5",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        search_btn.pack(side=LEFT, padx=5)
        
        # Clear search button
        clear_search_btn = tk.Button(
            search_frame,
            text="Clear",
            command=self.clear_search,
            font=("Arial", 12),
            bg="#f5f5f5",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        clear_search_btn.pack(side=LEFT, padx=5)
        
        # Students table frame
        table_frame = tk.Frame(content_frame, bg="white")
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Create treeview
        self.students_tree = ttk.Treeview(
            table_frame,
            columns=("roll", "name", "department", "year", "section", "registered"),
            show="headings",
            height=15
        )
        
        # Define headings
        self.students_tree.heading("roll", text="Roll Number")
        self.students_tree.heading("name", text="Name")
        self.students_tree.heading("department", text="Department")
        self.students_tree.heading("year", text="Year")
        self.students_tree.heading("section", text="Section")
        self.students_tree.heading("registered", text="Face Registered")
        
        # Define columns
        self.students_tree.column("roll", width=100, anchor=CENTER)
        self.students_tree.column("name", width=200, anchor=W)
        self.students_tree.column("department", width=150, anchor=W)
        self.students_tree.column("year", width=100, anchor=CENTER)
        self.students_tree.column("section", width=100, anchor=CENTER)
        self.students_tree.column("registered", width=100, anchor=CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=VERTICAL,
            command=self.students_tree.yview
        )
        self.students_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.students_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Load students
        self.load_students()
    
    def load_students(self):
        """Load students into the treeview"""
        # Clear existing data
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        # Get all students
        students = get_all_students()
        
        # Add to treeview
        for student in students:
            face_registered = "Yes" if student['face_registered'] else "No"
            
            self.students_tree.insert(
                "",
                END,
                values=(
                    student['roll_number'],
                    student['name'],
                    student['department'] or "-",
                    student['year'] or "-",
                    student['section'] or "-",
                    face_registered
                ),
                tags=('registered' if student['face_registered'] else 'not-registered',)
            )
        
        # Configure tag colors
        self.students_tree.tag_configure('registered', background="#e8f5e9")  # Light green
        self.students_tree.tag_configure('not-registered', background="#fff3e0")  # Light orange
    
    def search_students(self):
        """Search students in the treeview"""
        search_term = self.search_var.get().strip().lower()
        
        if not search_term:
            self.load_students()
            return
        
        # Clear existing data
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        # Get all students
        students = get_all_students()
        
        # Filter students
        filtered_students = []
        for student in students:
            if (search_term in student['roll_number'].lower() or
                search_term in student['name'].lower() or
                (student['department'] and search_term in student['department'].lower()) or
                (student['section'] and search_term in student['section'].lower())):
                filtered_students.append(student)
        
        # Add to treeview
        for student in filtered_students:
            face_registered = "Yes" if student['face_registered'] else "No"
            
            self.students_tree.insert(
                "",
                END,
                values=(
                    student['roll_number'],
                    student['name'],
                    student['department'] or "-",
                    student['year'] or "-",
                    student['section'] or "-",
                    face_registered
                ),
                tags=('registered' if student['face_registered'] else 'not-registered',)
            )
    
    def clear_search(self):
        """Clear search and reload all students"""
        self.search_var.set("")
        self.load_students()
    
    def import_students(self):
        """Import students from CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Ask for confirmation
        if messagebox.askyesno(
            "Confirm Import",
            "This will import students from the selected CSV file. Continue?"
        ):
            # Import students
            if import_students_from_csv(file_path):
                messagebox.showinfo(
                    "Success",
                    "Students imported successfully."
                )
                # Reload students
                self.load_students()
                # Update dashboard
                self.load_dashboard_data()
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to import students."
                )
    
    def setup_attendance_tab(self):
        """Setup the attendance tab"""
        # Header frame
        header_frame = tk.Frame(self.attendance_tab, bg="#0d47a1", pady=15)
        header_frame.pack(fill=X)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Attendance Management",
            font=("Arial", 18, "bold"),
            bg="#0d47a1",
            fg="white"
        )
        title_label.pack()
        
        # Content frame
        content_frame = tk.Frame(self.attendance_tab, bg="white", pady=20)
        content_frame.pack(fill=BOTH, expand=True, padx=20)
        
        # Filter frame
        filter_frame = tk.Frame(content_frame, bg="white", pady=10)
        filter_frame.pack(fill=X)
        
        # Subject selection
        subject_label = tk.Label(
            filter_frame,
            text="Subject:",
            font=("Arial", 12),
            bg="white"
        )
        subject_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)
        
        self.subject_var = tk.StringVar()
        self.subject_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.subject_var,
            font=("Arial", 12),
            width=30
        )
        self.subject_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Date selection
        date_label = tk.Label(
            filter_frame,
            text="Date:",
            font=("Arial", 12),
            bg="white"
        )
        date_label.grid(row=0, column=2, padx=5, pady=5, sticky=W)
        
        self.date_var = tk.StringVar()
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.date_var.set(today)
        date_entry = tk.Entry(
            filter_frame,
            textvariable=self.date_var,
            font=("Arial", 12),
            width=15,
            bd=2,
            relief=GROOVE
        )
        date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Date format hint
        date_hint = tk.Label(
            filter_frame,
            text="(YYYY-MM-DD)",
            font=("Arial", 10),
            bg="white",
            fg="#777777"
        )
        date_hint.grid(row=0, column=4, padx=0, pady=5, sticky=W)
        
        # View button
        view_btn = tk.Button(
            filter_frame,
            text="View Attendance",
            command=self.view_attendance,
            font=("Arial", 12),
            bg="#2196f3",
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        view_btn.grid(row=0, column=5, padx=20, pady=5)
        
        # Attendance table frame
        table_frame = tk.Frame(content_frame, bg="white")
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Create treeview
        self.attendance_tree = ttk.Treeview(
            table_frame,
            columns=("roll", "name", "status", "time"),
            show="headings",
            height=15
        )
        
        # Define headings
        self.attendance_tree.heading("roll", text="Roll Number")
        self.attendance_tree.heading("name", text="Name")
        self.attendance_tree.heading("status", text="Status")
        self.attendance_tree.heading("time", text="Time")
        
        # Define columns
        self.attendance_tree.column("roll", width=100, anchor=CENTER)
        self.attendance_tree.column("name", width=200, anchor=W)
        self.attendance_tree.column("status", width=100, anchor=CENTER)
        self.attendance_tree.column("time", width=100, anchor=CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=VERTICAL,
            command=self.attendance_tree.yview
        )
        self.attendance_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.attendance_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Load subjects for dropdown
        self.load_subjects_for_dropdown()
    
    def load_subjects_for_dropdown(self):
        """Load subjects for the dropdown"""
        subjects = get_all_subjects()
        subject_names = [subject['name'] for subject in subjects]
        
        # Update dropdown
        self.subject_dropdown['values'] = subject_names
        
        if subject_names:
            self.subject_var.set(subject_names[0])
    
    def view_attendance(self):
        """View attendance for selected subject and date"""
        subject = self.subject_var.get()
        date = self.date_var.get()
        
        if not subject:
            messagebox.showerror("Error", "Please select a subject")
            return
        
        # Clear existing data
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Get attendance data
        attendance_data = get_class_attendance(subject, date)
        
        if not attendance_data:
            messagebox.showinfo(
                "Information",
                f"No attendance records found for {subject} on {date}"
            )
            return
        
        # Add to treeview
        for record in attendance_data:
            status = "Present" if record['present'] else "Absent"
            
            self.attendance_tree.insert(
                "",
                END,
                values=(
                    record['roll_number'],
                    record['name'],
                    status,
                    record['time']
                ),
                tags=('present' if record['present'] else 'absent',)
            )
        
        # Configure tag colors
        self.attendance_tree.tag_configure('present', background="#e8f5e9")  # Light green
        self.attendance_tree.tag_configure('absent', background="#ffebee")  # Light red
    
    def setup_subjects_tab(self):
        """Setup the subjects tab"""
        # Header frame
        header_frame = tk.Frame(self.subjects_tab, bg="#0d47a1", pady=15)
        header_frame.pack(fill=X)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Subject Management",
            font=("Arial", 18, "bold"),
            bg="#0d47a1",
            fg="white"
        )
        title_label.pack()
        
        # Content frame
        content_frame = tk.Frame(self.subjects_tab, bg="white", pady=20)
        content_frame.pack(fill=BOTH, expand=True, padx=20)
        
        # Add subject frame
        add_frame = tk.LabelFrame(
            content_frame,
            text="Add New Subject",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        add_frame.pack(fill=X, pady=10)
        
        # Subject name field
        name_label = tk.Label(
            add_frame,
            text="Subject Name:",
            font=("Arial", 12),
            bg="white"
        )
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)
        
        self.subject_name_var = tk.StringVar()
        name_entry = tk.Entry(
            add_frame,
            textvariable=self.subject_name_var,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief=GROOVE
        )
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Department field
        dept_label = tk.Label(
            add_frame,
            text="Department:",
            font=("Arial", 12),
            bg="white"
        )
        dept_label.grid(row=0, column=2, padx=5, pady=5, sticky=W)
        
        self.subject_dept_var = tk.StringVar()
        dept_entry = tk.Entry(
            add_frame,
            textvariable=self.subject_dept_var,
            font=("Arial", 12),
            width=20,
            bd=2,
            relief=GROOVE
        )
        dept_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Year field
        year_label = tk.Label(
            add_frame,
            text="Year:",
            font=("Arial", 12),
            bg="white"
        )
        year_label.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        
        self.subject_year_var = tk.StringVar()
        year_options = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
        year_dropdown = ttk.Combobox(
            add_frame,
            textvariable=self.subject_year_var,
            font=("Arial", 12),
            width=28,
            values=year_options
        )
        year_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        # Semester field
        semester_label = tk.Label(
            add_frame,
            text="Semester:",
            font=("Arial", 12),
            bg="white"
        )
        semester_label.grid(row=1, column=2, padx=5, pady=5, sticky=W)
        
        self.subject_semester_var = tk.StringVar()
        semester_options = ["1st Semester", "2nd Semester"]
        semester_dropdown = ttk.Combobox(
            add_frame,
            textvariable=self.subject_semester_var,
            font=("Arial", 12),
            width=18,
            values=semester_options
        )
        semester_dropdown.grid(row=1, column=3, padx=5, pady=5)
        
        # Add button
        add_btn = tk.Button(
            add_frame,
            text="Add Subject",
            command=self.add_new_subject,
            font=("Arial", 12),
            bg="#4caf50",
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        add_btn.grid(row=2, column=1, padx=5, pady=15, sticky=W)
        
        # Subjects table frame
        table_frame = tk.LabelFrame(
            content_frame,
            text="All Subjects",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Create treeview
        self.subjects_tree = ttk.Treeview(
            table_frame,
            columns=("id", "name", "department", "year", "semester", "date"),
            show="headings",
            height=10
        )
        
        # Define headings
        self.subjects_tree.heading("id", text="ID")
        self.subjects_tree.heading("name", text="Subject Name")
        self.subjects_tree.heading("department", text="Department")
        self.subjects_tree.heading("year", text="Year")
        self.subjects_tree.heading("semester", text="Semester")
        self.subjects_tree.heading("date", text="Created Date")
        
        # Define columns
        self.subjects_tree.column("id", width=50, anchor=CENTER)
        self.subjects_tree.column("name", width=200, anchor=W)
        self.subjects_tree.column("department", width=150, anchor=W)
        self.subjects_tree.column("year", width=100, anchor=CENTER)
        self.subjects_tree.column("semester", width=100, anchor=CENTER)
        self.subjects_tree.column("date", width=100, anchor=CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=VERTICAL,
            command=self.subjects_tree.yview
        )
        self.subjects_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.subjects_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Load subjects
        self.load_subjects()
    
    def load_subjects(self):
        """Load subjects into the treeview"""
        # Clear existing data
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
        
        # Get all subjects
        subjects = get_all_subjects()
        
        # Add to treeview
        for subject in subjects:
            self.subjects_tree.insert(
                "",
                END,
                values=(
                    subject['id'],
                    subject['name'],
                    subject['department'] or "-",
                    subject['year'] or "-",
                    subject['semester'] or "-",
                    subject['created_date']
                )
            )
    
    def add_new_subject(self):
        """Add a new subject"""
        name = self.subject_name_var.get().strip()
        department = self.subject_dept_var.get().strip()
        year = self.subject_year_var.get()
        semester = self.subject_semester_var.get()
        
        if not name:
            messagebox.showerror("Error", "Subject name is required")
            return
        
        # Add subject
        if add_subject(name, department, year, semester):
            messagebox.showinfo(
                "Success",
                f"Subject '{name}' added successfully"
            )
            
            # Clear form
            self.subject_name_var.set("")
            self.subject_dept_var.set("")
            self.subject_year_var.set("")
            self.subject_semester_var.set("")
            
            # Reload subjects
            self.load_subjects()
            
            # Update dropdown in attendance tab
            self.load_subjects_for_dropdown()
            
            # Update dashboard
            self.load_dashboard_data()
        else:
            messagebox.showerror(
                "Error",
                f"Failed to add subject '{name}'. It may already exist."
            )
    
    def setup_reports_tab(self):
        """Setup the reports tab"""
        # Header frame
        header_frame = tk.Frame(self.reports_tab, bg="#0d47a1", pady=15)
        header_frame.pack(fill=X)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Attendance Reports",
            font=("Arial", 18, "bold"),
            bg="#0d47a1",
            fg="white"
        )
        title_label.pack()
        
        # Content frame
        content_frame = tk.Frame(self.reports_tab, bg="white", pady=20)
        content_frame.pack(fill=BOTH, expand=True, padx=20)
        
        # Report generation frame
        report_frame = tk.LabelFrame(
            content_frame,
            text="Generate Report",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        report_frame.pack(fill=X, pady=10)
        
        # Subject selection
        subject_label = tk.Label(
            report_frame,
            text="Subject:",
            font=("Arial", 12),
            bg="white"
        )
        subject_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)
        
        self.report_subject_var = tk.StringVar()
        self.report_subject_dropdown = ttk.Combobox(
            report_frame,
            textvariable=self.report_subject_var,
            font=("Arial", 12),
            width=30
        )
        self.report_subject_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Start date
        start_date_label = tk.Label(
            report_frame,
            text="Start Date:",
            font=("Arial", 12),
            bg="white"
        )
        start_date_label.grid(row=0, column=2, padx=5, pady=5, sticky=W)
        
        self.start_date_var = tk.StringVar()
        first_day = datetime.date.today().replace(day=1).strftime("%Y-%m-%d")
        self.start_date_var.set(first_day)
        start_date_entry = tk.Entry(
            report_frame,
            textvariable=self.start_date_var,
            font=("Arial", 12),
            width=15,
            bd=2,
            relief=GROOVE
        )
        start_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # End date
        end_date_label = tk.Label(
            report_frame,
            text="End Date:",
            font=("Arial", 12),
            bg="white"
        )
        end_date_label.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        
        self.end_date_var = tk.StringVar()
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.end_date_var.set(today)
        end_date_entry = tk.Entry(
            report_frame,
            textvariable=self.end_date_var,
            font=("Arial", 12),
            width=15,
            bd=2,
            relief=GROOVE
        )
        end_date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Date format hint
        date_hint = tk.Label(
            report_frame,
            text="(YYYY-MM-DD)",
            font=("Arial", 10),
            bg="white",
            fg="#777777"
        )
        date_hint.grid(row=1, column=2, padx=5, pady=5, sticky=W)
        
        # Generate button
        generate_btn = tk.Button(
            report_frame,
            text="Generate CSV Report",
            command=self.generate_report,
            font=("Arial", 12),
            bg="#ff9800",
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        generate_btn.grid(row=2, column=1, padx=5, pady=15, sticky=W)
        
        # Chart frame
        chart_frame = tk.LabelFrame(
            content_frame,
            text="Attendance Overview",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        chart_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # This will be populated when a report is generated
        self.chart_container = tk.Frame(chart_frame, bg="white")
        self.chart_container.pack(fill=BOTH, expand=True)
        
        # Load subjects for dropdown
        subjects = get_all_subjects()
        subject_names = [subject['name'] for subject in subjects]
        
        # Update dropdown
        self.report_subject_dropdown['values'] = subject_names
        
        if subject_names:
            self.report_subject_var.set(subject_names[0])
    
    def generate_report(self):
        """Generate attendance report"""
        subject = self.report_subject_var.get()
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        
        if not subject:
            messagebox.showerror("Error", "Please select a subject")
            return
        
        # Generate CSV report
        report_path = export_attendance_report(subject, start_date, end_date)
        
        if not report_path:
            messagebox.showinfo(
                "Information",
                f"No attendance records found for {subject} between {start_date} and {end_date}"
            )
            return
        
        # Show success message
        messagebox.showinfo(
            "Success",
            f"Report generated successfully.\n\nSaved to: {report_path}"
        )
        
        # Generate and display chart
        self.generate_attendance_chart(report_path)
    
    def generate_attendance_chart(self, csv_path):
        """Generate chart for attendance report"""
        # Clear existing chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Extract data
        roll_numbers = df['Roll Number'].tolist()
        names = df['Name'].tolist()
        percentages = [float(p.strip('%')) for p in df['Percentage'].tolist()]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        # Set colors based on attendance threshold
        colors = ['#4caf50' if p >= 75 else '#f44336' for p in percentages]
        
        # Create horizontal bar chart (better for many students)
        y_pos = range(len(names))
        bars = ax.barh(y_pos, percentages, color=colors)
        
        # Add a vertical line at 75%
        ax.axvline(x=75, color='r', linestyle='--', alpha=0.7, label='Minimum Required (75%)')
        
        # Customize chart
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{r} - {n}" for r, n in zip(roll_numbers, names)])
        ax.set_xlabel('Attendance (%)')
        ax.set_title('Subject-wise Attendance Percentage')
        ax.set_xlim(0, 100)
        
        # Add percentage labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.annotate(
                f'{width}%',
                xy=(width, i),
                xytext=(3, 0),  # 3 points horizontal offset
                textcoords="offset points",
                ha='left',
                va='center',
                fontsize=8
            )
        
        # Add legend
        ax.legend()
        
        # Adjust layout
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)