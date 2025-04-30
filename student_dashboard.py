import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from attendance_service import get_student_attendance

class StudentDashboard:
    def __init__(self, root, back_callback, student, text_to_speech=None):
        self.root = root
        self.back_callback = back_callback
        self.student = student
        self.text_to_speech = text_to_speech
        
        # Set window title
        self.root.title(f"Student Dashboard - {student['name']}")
        
        # Configure main frame
        self.setup_ui()
        
        # Load attendance data
        self.load_attendance_data()
    
    def setup_ui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Header frame
        self.header_frame = tk.Frame(self.main_frame, bg="#0d47a1", pady=15)
        self.header_frame.pack(fill=X)
        
        # Title and welcome message
        self.title_label = tk.Label(
            self.header_frame,
            text=f"Welcome, {self.student['name']}",
            font=("Arial", 20, "bold"),
            bg="#0d47a1",
            fg="white"
        )
        self.title_label.pack()
        
        self.subtitle_label = tk.Label(
            self.header_frame,
            text=f"Roll Number: {self.student['roll_number']}",
            font=("Arial", 14),
            bg="#0d47a1",
            fg="white"
        )
        self.subtitle_label.pack(pady=5)
        
        # Content frame
        self.content_frame = tk.Frame(self.main_frame, bg="white", pady=20)
        self.content_frame.pack(fill=BOTH, expand=True, padx=20)
        
        # Summary frame for overall attendance
        self.summary_frame = tk.LabelFrame(
            self.content_frame,
            text="Attendance Summary",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        self.summary_frame.pack(fill=X, pady=10)
        
        # Loading message (will be replaced with actual data)
        self.loading_label = tk.Label(
            self.summary_frame,
            text="Loading attendance data...",
            font=("Arial", 12),
            bg="white",
            fg="#555555"
        )
        self.loading_label.pack(pady=10)
        
        # Subject-wise attendance frame
        self.subjects_frame = tk.LabelFrame(
            self.content_frame,
            text="Subject-wise Attendance",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        self.subjects_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Table for subject-wise attendance
        self.create_attendance_table()
        
        # Graph frame for visualization
        self.graph_frame = tk.LabelFrame(
            self.content_frame,
            text="Attendance Visualization",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333333",
            pady=15,
            padx=15
        )
        self.graph_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Footer frame
        self.footer_frame = tk.Frame(self.main_frame, bg="#f5f5f5", pady=10)
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
        
        # Refresh button
        self.refresh_btn = tk.Button(
            self.footer_frame,
            text="Refresh Data",
            command=self.load_attendance_data,
            font=("Arial", 12),
            bg="#4caf50",
            fg="white",
            width=12,
            bd=0,
            cursor="hand2"
        )
        self.refresh_btn.pack(side=RIGHT, padx=10)
    
    def create_attendance_table(self):
        """Create the attendance table"""
        # Create treeview
        self.attendance_tree = ttk.Treeview(
            self.subjects_frame,
            columns=("subject", "total", "attended", "percentage"),
            show="headings",
            height=8
        )
        
        # Define headings
        self.attendance_tree.heading("subject", text="Subject")
        self.attendance_tree.heading("total", text="Total Classes")
        self.attendance_tree.heading("attended", text="Classes Attended")
        self.attendance_tree.heading("percentage", text="Attendance %")
        
        # Define columns
        self.attendance_tree.column("subject", width=200, anchor=W)
        self.attendance_tree.column("total", width=100, anchor=CENTER)
        self.attendance_tree.column("attended", width=150, anchor=CENTER)
        self.attendance_tree.column("percentage", width=150, anchor=CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.subjects_frame,
            orient=VERTICAL,
            command=self.attendance_tree.yview
        )
        self.attendance_tree.configure(yscroll=scrollbar.set)
        
        # Pack elements
        self.attendance_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
    
    def load_attendance_data(self):
        """Load attendance data for the student"""
        # Clear existing data
        if hasattr(self, 'attendance_tree'):
            for item in self.attendance_tree.get_children():
                self.attendance_tree.delete(item)
        
        # Clear graph if exists
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        
        # Get attendance data
        attendance_data = get_student_attendance(self.student['id'])
        
        if not attendance_data:
            # Update loading label to show no data
            self.loading_label.config(text="No attendance data available")
            return
        
        # Update summary frame
        if hasattr(self, 'loading_label'):
            self.loading_label.destroy()
        
        # Create summary widgets
        overall_frame = tk.Frame(self.summary_frame, bg="white")
        overall_frame.pack(fill=X)
        
        # Overall attendance percentage
        percentage = attendance_data['overall_percentage']
        color = "#4caf50" if percentage >= 75 else "#f44336"  # Green if >= 75%, red otherwise
        
        percentage_label = tk.Label(
            overall_frame,
            text=f"Overall Attendance: {percentage}%",
            font=("Arial", 18, "bold"),
            bg="white",
            fg=color
        )
        percentage_label.pack(side=LEFT, padx=20)
        
        # Status message
        status_message = "Good standing" if percentage >= 75 else "Attendance below required minimum (75%)"
        status_label = tk.Label(
            overall_frame,
            text=status_message,
            font=("Arial", 14),
            bg="white",
            fg=color
        )
        status_label.pack(side=LEFT, padx=20)
        
        # Update table
        subjects = attendance_data['subjects']
        for subject in subjects:
            self.attendance_tree.insert(
                "",
                END,
                values=(
                    subject['subject'],
                    subject['total_classes'],
                    subject['attended'],
                    f"{subject['percentage']}%"
                ),
                tags=('low' if subject['percentage'] < 75 else 'good',)
            )
        
        # Configure tag colors
        self.attendance_tree.tag_configure('low', background="#ffebee")  # Light red for low attendance
        self.attendance_tree.tag_configure('good', background="#e8f5e9")  # Light green for good attendance
        
        # Create graph
        self.create_attendance_graph(subjects)
    
    def create_attendance_graph(self, subjects):
        """Create a bar graph for attendance visualization"""
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        
        # Extract data
        subject_names = [s['subject'] for s in subjects]
        percentages = [s['percentage'] for s in subjects]
        colors = ['#4caf50' if p >= 75 else '#f44336' for p in percentages]
        
        # Create bar chart
        bars = ax.bar(subject_names, percentages, color=colors)
        
        # Add a horizontal line at 75%
        ax.axhline(y=75, color='r', linestyle='--', alpha=0.7, label='Minimum Required (75%)')
        
        # Customize chart
        ax.set_ylabel('Attendance (%)')
        ax.set_title('Subject-wise Attendance Percentage')
        ax.set_ylim(0, 100)
        
        # Add percentage labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f'{height}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center',
                va='bottom',
                fontsize=8
            )
        
        # Add legend
        ax.legend()
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        