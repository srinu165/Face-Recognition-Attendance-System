import tkinter as tk
from tkinter import *

class NotFoundPage:
    def __init__(self, root, back_callback):
        self.root = root
        self.back_callback = back_callback
        
        # Set window title
        self.root.title("Page Not Found - Face Recognition Attendance System")
        
        # Configure main frame
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Content frame
        self.content_frame = tk.Frame(self.main_frame, bg="white")
        self.content_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Error icon (using text as emoji)
        self.error_label = tk.Label(
            self.content_frame,
            text="⚠️",
            font=("Arial", 72),
            bg="white",
            fg="#f44336"
        )
        self.error_label.pack(pady=20)
        
        # Error title
        self.title_label = tk.Label(
            self.content_frame,
            text="404 - Page Not Found",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#333333"
        )
        self.title_label.pack(pady=10)
        
        # Error message
        self.message_label = tk.Label(
            self.content_frame,
            text="The page you're looking for doesn't exist or is unavailable.",
            font=("Arial", 14),
            bg="white",
            fg="#666666",
            wraplength=400,
            justify=CENTER
        )
        self.message_label.pack(pady=20)
        
        # Back button
        self.back_btn = tk.Button(
            self.content_frame,
            text="Go Back to Home",
            command=self.back_callback,
            font=("Arial", 14, "bold"),
            bg="#0d47a1",
            fg="white",
            padx=20,
            pady=10,
            bd=0,
            cursor="hand2"
        )
        self.back_btn.pack(pady=20)