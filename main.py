import tkinter as tk
from tkinter import *
import os
import cv2
import numpy as np
import pandas as pd
import datetime
import time
import pyttsx3

# Import application modules
from face_recognition_service import load_models, detect_faces
from login_page import LoginPage
from register_page import RegisterPage
from student_dashboard import StudentDashboard
from admin_dashboard import AdminDashboard
from take_attendance_page import TakeAttendancePage
from db_utils import create_database
from config import COLLEGE_NAME

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1280x720")
        self.root.configure(background="white")
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        
        # Create database if it doesn't exist
        create_database()
        
        # Load face recognition models
        load_models()
        
        # Configure root window
        self.setup_main_window()
        
    def setup_main_window(self):
        # College name title
        title_frame = tk.Frame(self.root, bg="#0d47a1", pady=10)
        title_frame.pack(fill=X)
        
        college_title = tk.Label(
            title_frame, 
            text=COLLEGE_NAME,
            bg="#0d47a1",
            fg="white",
            font=("Arial", 24, "bold"),
            pady=10
        )
        college_title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Face Recognition Attendance System",
            bg="#0d47a1",
            fg="white",
            font=("Arial", 16),
            pady=5
        )
        subtitle.pack()
        
        # Main content
        content_frame = tk.Frame(self.root, bg="white", pady=30)
        content_frame.pack(fill=BOTH, expand=True)
        
        # Main buttons
        self.create_main_buttons(content_frame)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg="#0d47a1", pady=10)
        footer_frame.pack(fill=X, side=BOTTOM)
        
        footer_text = tk.Label(
            footer_frame,
            text=f"© {datetime.datetime.now().year} {COLLEGE_NAME}. All rights reserved.",
            bg="#0d47a1",
            fg="white",
            font=("Arial", 10)
        )
        footer_text.pack()
    
    def create_main_buttons(self, parent):
        buttons_frame = tk.Frame(parent, bg="white")
        buttons_frame.pack(pady=50)
        
        # Button styling
        button_style = {
            "font": ("Arial", 14, "bold"),
            "bg": "#1976d2",
            "fg": "white",
            "width": 25,
            "height": 2,
            "borderwidth": 0,
            "relief": FLAT,
            "cursor": "hand2"
        }
        
        # Register button
        register_button = tk.Button(
            buttons_frame,
            text="Register New Student",
            command=self.open_register_page,
            **button_style
        )
        register_button.grid(row=0, column=0, padx=20, pady=20)
        
        # Take attendance button
        attendance_button = tk.Button(
            buttons_frame,
            text="Take Attendance",
            command=self.open_take_attendance,
            **button_style
        )
        attendance_button.grid(row=0, column=1, padx=20, pady=20)
        
        # Student login button
        student_login_button = tk.Button(
            buttons_frame,
            text="Student Login",
            command=self.open_student_login,
            **button_style
        )
        student_login_button.grid(row=1, column=0, padx=20, pady=20)
        
        # Admin login button
        admin_login_button = tk.Button(
            buttons_frame,
            text="Admin Login",
            command=self.open_admin_login,
            **button_style
        )
        admin_login_button.grid(row=1, column=1, padx=20, pady=20)
    
    def text_to_speech(self, text):
        """Convert text to speech"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def open_register_page(self):
        """Open student registration page"""
        self.clear_window()
        RegisterPage(self.root, self.back_to_main)
    
    def open_take_attendance(self):
        """Open take attendance page"""
        self.clear_window()
        TakeAttendancePage(self.root, self.back_to_main, self.text_to_speech)
    
    def open_student_login(self):
        """Open student login page"""
        self.clear_window()
        LoginPage(self.root, self.back_to_main, "student", self.text_to_speech)
    
    def open_admin_login(self):
        """Open admin login page"""
        self.clear_window()
        LoginPage(self.root, self.back_to_main, "admin", self.text_to_speech)
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def back_to_main(self):
        """Return to main window"""
        self.clear_window()
        self.setup_main_window()

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystem(root)
    root.mainloop()