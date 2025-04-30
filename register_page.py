import tkinter as tk
from tkinter import *
from tkinter import messagebox
import os
import uuid
import time
from PIL import Image, ImageTk

from db_utils import add_student, update_student_face_status
from face_recognition_service import take_face_images, train_model
from config import FACE_REGISTER_IMAGES

class RegisterPage:
    def __init__(self, root, back_callback, text_to_speech=None):
        self.root = root
        self.back_callback = back_callback
        self.text_to_speech = text_to_speech
        
        # Set window title
        self.root.title("Student Registration - Face Recognition Attendance System")
        
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
            text="Student Registration",
            font=("Arial", 24, "bold"),
            bg="#0d47a1",
            fg="white"
        )
        self.title_label.pack()
        
        # Registration form frame
        self.form_frame = tk.Frame(self.main_frame, bg="white", pady=30)
        self.form_frame.pack()
        
        # Roll Number field
        self.roll_label = tk.Label(
            self.form_frame,
            text="Roll Number:",
            font=("Arial", 12),
            bg="white",
            fg="#333333"
        )
        self.roll_label.grid(row=0, column=0, sticky=W, pady=10, padx=10)
        
        self.roll_var = tk.StringVar()
        self.roll_entry = tk.Entry(
            self.form_frame,
            textvariable=self.roll_var,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief=GROOVE
        )
        self.roll_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Name field
        self.name_label = tk.Label(
            self.form_frame,
            text="Full Name:",
            font=("Arial", 12),
            bg="white",
            fg="#333333"
        )
        self.name_label.grid(row=1, column=0, sticky=W, pady=10, padx=10)
        
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(
            self.form_frame,
            textvariable=self.name_var,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief=GROOVE
        )
        self.name_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Email field
        self.email_label = tk.Label(
            self.form_frame,
            text="Email:",
            font=("Arial", 12),
            bg="white",
            fg="#333333"
        )
        self.email_label.grid(row=2, column=0, sticky=W, pady=10, padx=10)
        
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(
            self.form_frame,
            textvariable=self.email_var,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief=GROOVE
        )
        self.email_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Department field
        self.dept_label = tk.Label(
            self.form_frame,
            text="Department:",
            font=("Arial", 12),
            bg="white",
            fg="#333333"
        )
        self.dept_label.grid(row=3, column=0, sticky=W, pady=10, padx=10)
        
        self.dept_var = tk.StringVar()
        self.dept_entry = tk.Entry(
            self.form_frame,
            textvariable=self.dept_var,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief=GROOVE
        )
        self.dept_entry.grid(row=3, column=1, pady=10, padx=10)
        
        # Year field
        self.year_label = tk.Label(
            self.form_frame,
            text="Year:",
            font=("Arial", 12),
            bg="white",
            fg="#333333"
        )
        self.year_label.grid(row=4, column=0, sticky=W, pady=10, padx=10)
        
        self.year_var = tk.StringVar()
        self.year_options = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
        self.year_dropdown = tk.OptionMenu(self.form_frame, self.year_var, *self.year_options)
        self.year_dropdown.config(
            font=("Arial", 12),
            width=28,
            bg="white",
            bd=2,
            relief=GROOVE
        )
        self.year_dropdown.grid(row=4, column=1, pady=10, padx=10, sticky=W+E)
        
        # Section field
        self.section_label = tk.Label(
            self.form_frame,
            text="Section:",
            font=("Arial", 12),
            bg="white",
            fg="#333333"
        )
        self.section_label.grid(row=5, column=0, sticky=W, pady=10, padx=10)
        
        self.section_var = tk.StringVar()
        self.section_entry = tk.Entry(
            self.form_frame,
            textvariable=self.section_var,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief=GROOVE
        )
        self.section_entry.grid(row=5, column=1, pady=10, padx=10)
        
        # Password field
        self.password_label = tk.Label(
            self.form_frame,
            text="Password:",
            font=("Arial", 12),
            bg="white",
            fg="#333333"
        )
        self.password_label.grid(row=6, column=0, sticky=W, pady=10, padx=10)
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            self.form_frame,
            textvariable=self.password_var,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief=GROOVE,
            show="*"
        )
        self.password_entry.grid(row=6, column=1, pady=10, padx=10)
        
        # Confirm Password field
        self.confirm_password_label = tk.Label(
            self.form_frame,
            text="Confirm Password:",
            font=("Arial", 12),
            bg="white",
            fg="#333333"
        )
        self.confirm_password_label.grid(row=7, column=0, sticky=W, pady=10, padx=10)
        
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = tk.Entry(
            self.form_frame,
            textvariable=self.confirm_password_var,
            font=("Arial", 12),
            width=30,
            bd=2,
            relief=GROOVE,
            show="*"
        )
        self.confirm_password_entry.grid(row=7, column=1, pady=10, padx=10)
        
        # Buttons frame
        self.buttons_frame = tk.Frame(self.form_frame, bg="white", pady=20)
        self.buttons_frame.grid(row=8, column=0, columnspan=2)
        
        # Register button
        self.register_btn = tk.Button(
            self.buttons_frame,
            text="Register & Capture Face",
            command=self.handle_registration,
            font=("Arial", 14, "bold"),
            bg="#4caf50",
            fg="white",
            width=20,
            bd=0,
            cursor="hand2"
        )
        self.register_btn.grid(row=0, column=0, padx=10)
        
        # Back button
        self.back_btn = tk.Button(
            self.buttons_frame,
            text="Back",
            command=self.back_callback,
            font=("Arial", 14),
            bg="#f5f5f5",
            fg="#333333",
            width=10,
            bd=0,
            cursor="hand2"
        )
        self.back_btn.grid(row=0, column=1, padx=10)
    
    def validate_form(self):
        """Validate registration form"""
        roll = self.roll_var.get().strip()
        name = self.name_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        if not roll:
            messagebox.showerror("Error", "Roll Number is required")
            return False
        
        if not name:
            messagebox.showerror("Error", "Name is required")
            return False
        
        if not password:
            messagebox.showerror("Error", "Password is required")
            return False
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return False
        
        return True
    
    def handle_registration(self):
        """Handle student registration"""
        if not self.validate_form():
            return
        
        # Get form data
        roll = self.roll_var.get().strip()
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        department = self.dept_var.get().strip()
        year = self.year_var.get()
        section = self.section_var.get().strip()
        password = self.password_var.get()
        
        # Generate unique ID for the student
        student_id = str(uuid.uuid4())
        
        # First save student to database
        if add_student(
            student_id=student_id,
            name=name,
            roll_number=roll,
            password=password,
            email=email,
            department=department,
            year=year,
            section=section,
            face_registered=0
        ):
            # Ask if user wants to capture face
            response = messagebox.askyesno(
                "Face Registration",
                f"Student registered successfully!\n\nWould you like to capture face images for {name}?"
            )
            
            if response:
                # Inform user about face capture
                messagebox.showinfo(
                    "Face Capture",
                    f"We will now capture {FACE_REGISTER_IMAGES} images of your face.\n\n"
                    "Please look at the camera from different angles."
                )
                
                # Capture face images
                num_images = take_face_images(student_id, name, FACE_REGISTER_IMAGES)
                
                if num_images > 0:
                    # Train the model with new images
                    if train_model():
                        # Update student face registration status
                        update_student_face_status(student_id, True)
                        
                        messagebox.showinfo(
                            "Success",
                            f"Successfully captured {num_images} face images and trained the model.\n\n"
                            "You can now login using face recognition."
                        )
                    else:
                        messagebox.showwarning(
                            "Warning",
                            "Face images captured but model training failed.\n\n"
                            "Please try again or contact administrator."
                        )
                else:
                    messagebox.showerror(
                        "Error",
                        "Failed to capture face images.\n\n"
                        "Please try again or use password login."
                    )
            
            # Return to main menu
            self.back_callback()
        else:
            messagebox.showerror(
                "Error",
                "Registration failed. Please try again.\n\n"
                "This roll number may already be registered."
            )