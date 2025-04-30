import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import cv2
import time
import datetime
import os
import threading

from face_recognition_service import load_models, recognize_face
from attendance_service import mark_attendance
from db_utils import get_all_subjects, get_all_students

class TakeAttendancePage:
    def __init__(self, root, back_callback, text_to_speech=None):
        self.root = root
        self.back_callback = back_callback
        self.text_to_speech = text_to_speech
        
        # Set window title
        self.root.title("Take Attendance - Face Recognition Attendance System")
        
        # Camera variables
        self.camera_active = False
        self.camera_thread = None
        self.stop_event = threading.Event()
        
        # Configure main frame
        self.setup_ui()
        
        # Load face recognition models
        load_models()
    
    def setup_ui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Header frame
        self.header_frame = tk.Frame(self.main_frame, bg="#0d47a1", pady=15)
        self.header_frame.pack(fill=X)
        
        # Title
        self.title_label = tk.Label(
            self.header_frame,
            text="Take Attendance with Face Recognition",
            font=("Arial", 20, "bold"),
            bg="#0d47a1",
            fg="white"
        )
        self.title_label.pack()
        
        # Content frame
        self.content_frame = tk.Frame(self.main_frame, bg="white", pady=20)
        self.content_frame.pack(fill=BOTH, expand=True, padx=20)
        
        # Setup frame - for selecting subject
        self.setup_frame = tk.LabelFrame(
            self.content_frame,
            text="Setup",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        self.setup_frame.pack(fill=X, pady=10)
        
        # Subject selection
        self.subject_label = tk.Label(
            self.setup_frame,
            text="Select Subject:",
            font=("Arial", 12),
            bg="white"
        )
        self.subject_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)
        
        self.subject_var = tk.StringVar()
        self.subject_dropdown = ttk.Combobox(
            self.setup_frame,
            textvariable=self.subject_var,
            font=("Arial", 12),
            width=30
        )
        self.subject_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Date display
        self.date_label = tk.Label(
            self.setup_frame,
            text="Date:",
            font=("Arial", 12),
            bg="white"
        )
        self.date_label.grid(row=0, column=2, padx=5, pady=5, sticky=W)
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.date_display = tk.Label(
            self.setup_frame,
            text=today,
            font=("Arial", 12, "bold"),
            bg="#f5f5f5",
            fg="#333333",
            width=15,
            bd=1,
            relief=GROOVE,
            padx=5,
            pady=5
        )
        self.date_display.grid(row=0, column=3, padx=5, pady=5)
        
        # Start button
        self.start_btn = tk.Button(
            self.setup_frame,
            text="Start Attendance",
            command=self.start_attendance,
            font=("Arial", 12, "bold"),
            bg="#4caf50",
            fg="white",
            width=15,
            bd=0,
            padx=5,
            pady=8,
            cursor="hand2"
        )
        self.start_btn.grid(row=1, column=1, pady=10)
        
        # Stop button (initially disabled)
        self.stop_btn = tk.Button(
            self.setup_frame,
            text="Stop Attendance",
            command=self.stop_attendance,
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            width=15,
            bd=0,
            padx=5,
            pady=8,
            cursor="hand2",
            state=DISABLED
        )
        self.stop_btn.grid(row=1, column=2, pady=10)
        
        # Camera frame - for displaying webcam feed
        self.camera_frame = tk.LabelFrame(
            self.content_frame,
            text="Camera Feed",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        self.camera_frame.pack(fill=X, pady=10)
        
        # Create a label for displaying video
        self.video_label = tk.Label(self.camera_frame, bg="black")
        self.video_label.pack(pady=10)
        
        # Attendance records frame
        self.records_frame = tk.LabelFrame(
            self.content_frame,
            text="Attendance Records",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        self.records_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Create treeview for displaying attendance records
        self.records_tree = ttk.Treeview(
            self.records_frame,
            columns=("roll", "name", "time", "status"),
            show="headings",
            height=8
        )
        
        # Define headings
        self.records_tree.heading("roll", text="Roll Number")
        self.records_tree.heading("name", text="Name")
        self.records_tree.heading("time", text="Time")
        self.records_tree.heading("status", text="Status")
        
        # Define columns
        self.records_tree.column("roll", width=100, anchor=CENTER)
        self.records_tree.column("name", width=200, anchor=W)
        self.records_tree.column("time", width=100, anchor=CENTER)
        self.records_tree.column("status", width=100, anchor=CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.records_frame,
            orient=VERTICAL,
            command=self.records_tree.yview
        )
        self.records_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.records_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Footer frame
        self.footer_frame = tk.Frame(self.main_frame, bg="#f5f5f5", pady=10)
        self.footer_frame.pack(fill=X, side=BOTTOM)
        
        # Back button
        self.back_btn = tk.Button(
            self.footer_frame,
            text="Back to Home",
            command=self.on_closing,
            font=("Arial", 12),
            bg="#f5f5f5",
            fg="#333333",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.back_btn.pack(side=LEFT, padx=20)
        
        # Load subjects
        self.load_subjects()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_subjects(self):
        """Load subjects for the dropdown"""
        subjects = get_all_subjects()
        subject_names = [subject['name'] for subject in subjects]
        
        # Update dropdown
        self.subject_dropdown['values'] = subject_names
        
        if subject_names:
            self.subject_var.set(subject_names[0])
    
    def start_attendance(self):
        """Start attendance process with webcam"""
        subject = self.subject_var.get()
        
        if not subject:
            messagebox.showerror("Error", "Please select a subject")
            return
        
        # Disable start button and enable stop button
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        
        # Clear attendance records
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        # Reset stop event
        self.stop_event.clear()
        
        # Start camera in a separate thread
        self.camera_active = True
        self.camera_thread = threading.Thread(target=self.run_camera)
        self.camera_thread.daemon = True
        self.camera_thread.start()
        
        # Announce
        if self.text_to_speech:
            self.text_to_speech(f"Starting attendance for {subject}. Please look at the camera.")
    
    def stop_attendance(self):
        """Stop attendance process"""
        # Signal camera thread to stop
        self.stop_event.set()
        self.camera_active = False
        
        # Enable start button and disable stop button
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        
        if self.text_to_speech:
            self.text_to_speech("Attendance process stopped.")
    
    def run_camera(self):
        """Run the camera feed and face recognition in a separate thread"""
        # Initialize camera
        cap = cv2.VideoCapture(0)
        
        # Get selected subject
        subject = self.subject_var.get()
        
        # Dictionary to track recognized students to avoid duplicates
        recognized_students = {}
        
        while self.camera_active and not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Perform face recognition
            student_id, confidence, face_coords = recognize_face(frame)
            
            # Draw rectangle around face
            if face_coords:
                x, y, w, h = face_coords
                
                if student_id and student_id not in recognized_students:
                    # Mark attendance
                    if mark_attendance(student_id, subject):
                        # Get student details
                        student_details = self.get_student_details(student_id)
                        
                        if student_details:
                            # Add to recognized students
                            recognized_students[student_id] = student_details
                            
                            # Add to treeview
                            current_time = datetime.datetime.now().strftime("%H:%M:%S")
                            self.records_tree.insert(
                                "",
                                0,  # Insert at top
                                values=(
                                    student_details['roll_number'],
                                    student_details['name'],
                                    current_time,
                                    "Present"
                                ),
                                tags=('present',)
                            )
                            
                            # Configure tag color
                            self.records_tree.tag_configure('present', background="#e8f5e9")  # Light green
                            
                            # Announce
                            if self.text_to_speech:
                                self.text_to_speech(f"Attendance marked for {student_details['name']}")
                    
                    # Draw green rectangle and show name
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    if student_details:
                        label = f"{student_details['name']} ({student_details['roll_number']})"
                        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Conf: {confidence:.2f}", (x, y+h+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                elif student_id:
                    # Already recognized
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                    
                    student_details = recognized_students.get(student_id)
                    if student_details:
                        label = f"{student_details['name']} (Already marked)"
                        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                else:
                    # Unknown face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Display date and time on the frame
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Add subject name
            cv2.putText(frame, f"Subject: {subject}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Add counter for recognized students
            cv2.putText(frame, f"Recognized: {len(recognized_students)}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Convert to RGB for tkinter
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Update label with new frame
            img = tk.PhotoImage(data=cv2.imencode('.ppm', rgb_frame)[1].tobytes())
            self.video_label.configure(image=img)
            self.video_label.image = img
            
            # Process tkinter events
            self.root.update()
        
        # Release camera
        cap.release()
        
        # Clear video label
        self.video_label.configure(image='')
    
    def get_student_details(self, student_id):
        """Get student details by ID"""
        students = get_all_students()
        
        for student in students:
            if student['id'] == student_id:
                return student
        
        return None
    
    def on_closing(self):
        """Handle window closing"""
        if self.camera_active:
            self.stop_attendance()
        
        # Wait for camera thread to finish
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(1.0)  # Wait up to 1 second
        
        # Go back to main window
        self.back_callback()