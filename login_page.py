import tkinter as tk
from tkinter import *
from tkinter import messagebox
import os
import uuid
import cv2
import time
from PIL import Image, ImageTk

from db_utils import get_student_by_credentials, get_admin_by_credentials
from face_recognition_service import verify_student_face
from student_dashboard import StudentDashboard
from admin_dashboard import AdminDashboard

class LoginPage:
    def __init__(self, root, back_callback, role="student", text_to_speech=None):
        self.root = root
        self.back_callback = back_callback
        self.role = role
        self.text_to_speech = text_to_speech
        
        # Set window title
        self.root.title(f"{role.capitalize()} Login - Face Recognition Attendance System")
        
        # Configure main frame
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Title frame
        self.title_frame = tk.Frame(self.main_frame, bg="#0d47a1", pady=20)
        self.title_frame.pack(fill=X)
        
        # Title label
        self.title_label = tk.Label(
            self.title_frame,
            text=f"{self.role.capitalize()} Login",
            font=("Arial", 24, "bold"),
            bg="#0d47a1",
            fg="white"
        )
        self.title_label.pack()
        
        # Login form frame
        self.form_frame = tk.Frame(self.main_frame, bg="white", pady=50)
        self.form_frame.pack()
        
        # Username/Roll Number field
        self.id_label = tk.Label(
            self.form_frame,
            text="Roll Number:" if self.role == "student" else "Username:",
            font=("Arial", 14),
            bg="white",
            fg="#333333"
        )
        self.id_label.grid(row=0, column=0, sticky=W, pady=10, padx=10)
        
        self.id_var = tk.StringVar()
        self.id_entry = tk.Entry(
            self.form_frame,
            textvariable=self.id_var,
            font=("Arial", 14),
            width=25,
            bd=2,
            relief=GROOVE
        )
        self.id_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Password field
        self.password_label = tk.Label(
            self.form_frame,
            text="Password:",
            font=("Arial", 14),
            bg="white",
            fg="#333333"
        )
        self.password_label.grid(row=1, column=0, sticky=W, pady=10, padx=10)
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            self.form_frame,
            textvariable=self.password_var,
            font=("Arial", 14),
            width=25,
            bd=2,
            relief=GROOVE,
            show="*"
        )
        self.password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Login button
        self.login_btn = tk.Button(
            self.form_frame,
            text="Login",
            command=self.handle_login,
            font=("Arial", 14, "bold"),
            bg="#1976d2",
            fg="white",
            width=15,
            bd=0,
            cursor="hand2"
        )
        self.login_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Face recognition login (only for students)
        if self.role == "student":
            self.face_login_frame = tk.Frame(self.form_frame, bg="white")
            self.face_login_frame.grid(row=3, column=0, columnspan=2, pady=20)
            
            self.face_login_label = tk.Label(
                self.face_login_frame,
                text="- OR -",
                font=("Arial", 14),
                bg="white",
                fg="#555555"
            )
            self.face_login_label.pack(pady=10)
            
            self.face_login_btn = tk.Button(
                self.face_login_frame,
                text="Login with Face",
                command=self.handle_face_login,
                font=("Arial", 14, "bold"),
                bg="#4caf50",
                fg="white",
                width=15,
                bd=0,
                cursor="hand2"
            )
            self.face_login_btn.pack()
        
        # Back button
        self.back_frame = tk.Frame(self.main_frame, bg="white", pady=20)
        self.back_frame.pack(side=BOTTOM, fill=X)
        
        self.back_btn = tk.Button(
            self.back_frame,
            text="Back to Home",
            command=self.back_callback,
            font=("Arial", 12),
            bg="#f5f5f5",
            fg="#333333",
            bd=0,
            cursor="hand2"
        )
        self.back_btn.pack(side=LEFT, padx=20)
    
    def handle_login(self):
        """Handle login with username/roll and password"""
        user_id = self.id_var.get()
        password = self.password_var.get()
        
        if not user_id or not password:
            messagebox.showerror("Error", "Please enter both fields")
            if self.text_to_speech:
                self.text_to_speech("Please enter both fields")
            return
        
        # Authenticate based on role
        if self.role == "student":
            user = get_student_by_credentials(user_id, password)
            if user:
                messagebox.showinfo("Success", f"Welcome, {user['name']}!")
                if self.text_to_speech:
                    self.text_to_speech(f"Welcome, {user['name']}!")
                self.show_student_dashboard(user)
            else:
                messagebox.showerror("Error", "Invalid roll number or password")
                if self.text_to_speech:
                    self.text_to_speech("Invalid roll number or password")
        else:
            user = get_admin_by_credentials(user_id, password)
            if user:
                messagebox.showinfo("Success", f"Welcome, {user['name']}!")
                if self.text_to_speech:
                    self.text_to_speech(f"Welcome, {user['name']}!")
                self.show_admin_dashboard(user)
            else:
                messagebox.showerror("Error", "Invalid username or password")
                if self.text_to_speech:
                    self.text_to_speech("Invalid username or password")
    
    def handle_face_login(self):
        """Handle login with face recognition"""
        # This only works for students
        if self.role != "student":
            return
        
        # Ask for roll number first
        roll_number = self.id_var.get()
        
        if not roll_number:
            messagebox.showerror("Error", "Please enter your roll number")
            if self.text_to_speech:
                self.text_to_speech("Please enter your roll number")
            return
        
        # Get student details
        student = get_student_by_credentials(roll_number, "")
        
        if not student:
            messagebox.showerror("Error", "Student not found with this roll number")
            if self.text_to_speech:
                self.text_to_speech("Student not found with this roll number")
            return
        
        if not student['face_registered']:
            messagebox.showerror("Error", "Face not registered. Please register your face first.")
            if self.text_to_speech:
                self.text_to_speech("Face not registered. Please register your face first.")
            return
        
        # Show message before starting face verification
        messagebox.showinfo("Face Verification", "Please look at the camera for face verification.")
        if self.text_to_speech:
            self.text_to_speech("Please look at the camera for face verification.")
        
        # Verify face
        if verify_student_face(student['id']):
            messagebox.showinfo("Success", f"Face verified! Welcome, {student['name']}!")
            if self.text_to_speech:
                self.text_to_speech(f"Face verified! Welcome, {student['name']}!")
            self.show_student_dashboard(student)
        else:
            messagebox.showerror("Error", "Face verification failed. Please try again or use password login.")
            if self.text_to_speech:
                self.text_to_speech("Face verification failed. Please try again or use password login.")
    
    def show_student_dashboard(self, student):
        """Show student dashboard"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        StudentDashboard(self.root, self.back_callback, student, self.text_to_speech)
    
    def show_admin_dashboard(self, admin):
        """Show admin dashboard"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        AdminDashboard(self.root, self.back_callback, admin, self.text_to_speech)