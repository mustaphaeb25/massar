import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import sqlite3
import hashlib
import os
from datetime import datetime

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System - Massar")
        self.root.geometry("1200x700")
        
        # Initialize database
        self.init_database()
        
        # Current user
        self.current_user = None
        self.current_role = None
        self.current_user_id = None
        
        # Show login screen
        self.show_login()
    
    def init_database(self):
        """Initialize SQLite database and create tables"""
        self.conn = sqlite3.connect('massar_system.db')
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                cne TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                password TEXT NOT NULL,
                class TEXT,
                birth_date TEXT,
                address TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                password TEXT NOT NULL,
                subject TEXT,
                qualification TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_code TEXT UNIQUE NOT NULL,
                subject_name TEXT NOT NULL,
                teacher_id INTEGER,
                class TEXT,
                credits INTEGER,
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                grade REAL NOT NULL,
                exam_type TEXT,
                semester TEXT,
                academic_year TEXT,
                remarks TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id),
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT UNIQUE NOT NULL,
                level TEXT,
                capacity INTEGER,
                year TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date DATE NOT NULL,
                status TEXT NOT NULL,
                subject_id INTEGER,
                remarks TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default admin if not exists
        self.cursor.execute("SELECT COUNT(*) FROM admin")
        if self.cursor.fetchone()[0] == 0:
            default_password = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO admin (username, password, email) VALUES (?, ?, ?)",
                ("admin", default_password, "admin@school.ma")
            )
        
        self.conn.commit()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login(self):
        """Show login screen"""
        self.clear_window()
        
        # Main frame with ttkbootstrap style
        main_frame = ttk.Frame(self.root, bootstyle="light")
        main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Title with Moroccan flag colors
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        ttk.Label(title_frame, text="🏫", font=("Helvetica", 40)).pack(side=LEFT, padx=5)
        ttk.Label(title_frame, text="Massar System", 
                 font=("Helvetica", 28, "bold"), bootstyle="primary").pack(side=LEFT)
        
        # Login box
        login_box = ttk.Labelframe(main_frame, text="Login", padding=20, bootstyle="info")
        login_box.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Role selection
        ttk.Label(login_box, text="Login as:", font=("Helvetica", 12)).grid(row=0, column=0, columnspan=3, pady=5, sticky=W)
        
        self.role_var = tk.StringVar(value="student")
        roles_frame = ttk.Frame(login_box)
        roles_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Radiobutton(roles_frame, text="🎓 Student", variable=self.role_var, 
                       value="student", bootstyle="info-toolbutton").pack(side=LEFT, padx=5)
        ttk.Radiobutton(roles_frame, text="👨‍🏫 Teacher", variable=self.role_var, 
                       value="teacher", bootstyle="success-toolbutton").pack(side=LEFT, padx=5)
        ttk.Radiobutton(roles_frame, text="👑 Admin", variable=self.role_var, 
                       value="admin", bootstyle="danger-toolbutton").pack(side=LEFT, padx=5)
        
        # Username/ID
        ttk.Label(login_box, text="Username/ID:").grid(row=2, column=0, pady=10, sticky=W)
        self.username_entry = ttk.Entry(login_box, width=30)
        self.username_entry.grid(row=2, column=1, columnspan=2, pady=10, padx=(10, 0))
        
        # Password
        ttk.Label(login_box, text="Password:").grid(row=3, column=0, pady=10, sticky=W)
        self.password_entry = ttk.Entry(login_box, width=30, show="•")
        self.password_entry.grid(row=3, column=1, columnspan=2, pady=10, padx=(10, 0))
        
        # Login button
        ttk.Button(login_box, text="🔐 Login", command=self.login, 
                  bootstyle="primary", width=20).grid(row=4, column=0, columnspan=3, pady=20)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Label(footer_frame, text="Student Management System v1.0", 
                 font=("Helvetica", 10), bootstyle="secondary").pack()
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        hashed_password = self.hash_password(password)
        
        if role == "admin":
            self.cursor.execute(
                "SELECT id FROM admin WHERE username = ? AND password = ?",
                (username, hashed_password)
            )
            admin = self.cursor.fetchone()
            if admin:
                self.current_user = username
                self.current_role = "admin"
                self.current_user_id = admin[0]
                self.show_admin_dashboard()
            else:
                messagebox.showerror("Error", "Invalid admin credentials")
        
        elif role == "student":
            self.cursor.execute(
                "SELECT id, name FROM students WHERE student_id = ? AND password = ?",
                (username, hashed_password)
            )
            student = self.cursor.fetchone()
            if student:
                self.current_user = student[1]
                self.current_role = "student"
                self.current_user_id = student[0]
                self.show_student_dashboard()
            else:
                messagebox.showerror("Error", "Invalid student credentials")
        
        elif role == "teacher":
            self.cursor.execute(
                "SELECT id, name FROM teachers WHERE teacher_id = ? AND password = ?",
                (username, hashed_password)
            )
            teacher = self.cursor.fetchone()
            if teacher:
                self.current_user = teacher[1]
                self.current_role = "teacher"
                self.current_user_id = teacher[0]
                self.show_teacher_dashboard()
            else:
                messagebox.showerror("Error", "Invalid teacher credentials")
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.current_role = None
        self.current_user_id = None
        self.show_login()
    
    def show_student_dashboard(self):
        """Show student dashboard"""
        self.clear_window()
        
        # Header
        header = ttk.Frame(self.root, bootstyle="primary")
        header.pack(fill=X, padx=10, pady=10)
        
        # Get student info
        self.cursor.execute(
            "SELECT name, student_id, class FROM students WHERE id = ?",
            (self.current_user_id,)
        )
        student_info = self.cursor.fetchone()
        
        # Welcome message
        welcome_text = f"🎓 Welcome, {student_info[0]} | ID: {student_info[1]} | Class: {student_info[2]}"
        ttk.Label(header, text=welcome_text, 
                 font=("Helvetica", 14, "bold"), bootstyle="inverse-primary").pack(side=LEFT, padx=10)
        
        ttk.Button(header, text="🚪 Logout", command=self.logout, 
                  bootstyle="danger-outline").pack(side=RIGHT, padx=5)
        
        # Main content with Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Results Tab
        results_tab = ttk.Frame(notebook)
        notebook.add(results_tab, text="📊 My Results")
        self.create_student_results_tab(results_tab)
        
        # Profile Tab
        profile_tab = ttk.Frame(notebook)
        notebook.add(profile_tab, text="👤 My Profile")
        self.create_student_profile_tab(profile_tab)
    
    def create_student_results_tab(self, parent):
        """Create student results tab"""
        # Stats frame with refresh button
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=X, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(stats_frame, text="🔄 Refresh", command=self.load_student_results,
                  bootstyle="info").pack(side=LEFT, padx=10)
        
        # Stats labels
        self.total_exams_label = ttk.Label(stats_frame, text="📈 Total Exams: 0", 
                                          bootstyle="info")
        self.total_exams_label.pack(side=LEFT, padx=20)
        
        self.average_label = ttk.Label(stats_frame, text="⭐ Average: N/A", 
                                      bootstyle="success")
        self.average_label.pack(side=LEFT, padx=20)
        
        # Results table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        columns = ("Subject", "Grade", "Exam Type", "Semester", "Year", "Date", "Teacher")
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, 
                                         show="headings", yscrollcommand=scrollbar.set,
                                         height=15)
        scrollbar.config(command=self.results_tree.yview)
        
        # Define headings
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120, anchor=CENTER)
        
        self.results_tree.pack(fill=BOTH, expand=True)
        
        # Load results
        self.load_student_results()
    
    def load_student_results(self):
        """Load student results into treeview and update stats"""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Calculate statistics
        self.cursor.execute('''
            SELECT COUNT(*), AVG(grade), MIN(grade), MAX(grade)
            FROM results
            WHERE student_id = ?
        ''', (self.current_user_id,))
        stats = self.cursor.fetchone()
        
        # Update stats labels
        self.total_exams_label.config(text=f"📈 Total Exams: {stats[0] or 0}")
        if stats[1]:
            self.average_label.config(text=f"⭐ Average: {stats[1]:.2f}")
        else:
            self.average_label.config(text="⭐ Average: N/A")
        
        # Load results
        self.cursor.execute('''
            SELECT 
                sub.subject_name, 
                r.grade, 
                r.exam_type, 
                r.semester, 
                r.academic_year, 
                r.date,
                t.name
            FROM results r
            LEFT JOIN subjects sub ON r.subject_id = sub.id
            LEFT JOIN teachers t ON r.teacher_id = t.id
            WHERE r.student_id = ?
            ORDER BY r.date DESC
        ''', (self.current_user_id,))
        
        results = self.cursor.fetchall()
        
        if not results:
            # Insert a placeholder if no results
            self.results_tree.insert("", END, values=("No results found", "", "", "", "", "", ""))
            return
        
        for result in results:
            # Color code based on grade
            tags = ()
            grade = result[1] if result[1] is not None else 0
            if grade >= 16:
                tags = ('excellent',)
            elif grade >= 14:
                tags = ('very_good',)
            elif grade >= 12:
                tags = ('good',)
            elif grade >= 10:
                tags = ('pass',)
            else:
                tags = ('fail',)
            
            self.results_tree.insert("", END, values=result, tags=tags)
        
        # Configure tag colors
        self.results_tree.tag_configure('excellent', background='#d4edda')
        self.results_tree.tag_configure('very_good', background='#fff3cd')
        self.results_tree.tag_configure('good', background='#d1ecf1')
        self.results_tree.tag_configure('pass', background='#f8d7da')
        self.results_tree.tag_configure('fail', background='#f5c6cb')
    
    def create_student_profile_tab(self, parent):
        """Create student profile tab"""
        # Get student details
        self.cursor.execute(
            "SELECT * FROM students WHERE id = ?", (self.current_user_id,)
        )
        student = self.cursor.fetchone()
        columns = [description[0] for description in self.cursor.description]
        
        # Profile frame
        profile_frame = ttk.Labelframe(parent, text="Personal Information", padding=20)
        profile_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Display student information
        info_frame = ttk.Frame(profile_frame)
        info_frame.pack(fill=BOTH, expand=True)
        
        # Create labels for each field
        fields = [
            ("Student ID", student[columns.index('student_id')]),
            ("CNE", student[columns.index('cne')] or "N/A"),
            ("Full Name", student[columns.index('name')]),
            ("Email", student[columns.index('email')] or "N/A"),
            ("Class", student[columns.index('class')] or "N/A"),
            ("Birth Date", student[columns.index('birth_date')] or "N/A"),
            ("Phone", student[columns.index('phone')] or "N/A"),
            ("Registration Date", student[columns.index('created_at')])
        ]
        
        for i, (label, value) in enumerate(fields):
            row = i
            ttk.Label(info_frame, text=f"{label}:", font=("Helvetica", 10, "bold"),
                     bootstyle="secondary").grid(row=row, column=0, padx=10, pady=5, sticky=W)
            ttk.Label(info_frame, text=value, font=("Helvetica", 10)).grid(
                row=row, column=1, padx=10, pady=5, sticky=W)
    
    def create_student_attendance_tab(self, parent):
        """Create student attendance tab"""
        # Stats frame
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=X, padx=10, pady=10)
        
        # Calculate attendance statistics
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent,
                SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late
            FROM attendance 
            WHERE student_id = ?
        ''', (self.current_user_id,))
        
        stats = self.cursor.fetchone()
        total = stats[0] or 0
        present = stats[1] or 0
        absent = stats[2] or 0
        late = stats[3] or 0
        
        if total > 0:
            attendance_rate = (present / total) * 100
        else:
            attendance_rate = 0
        
        ttk.Label(stats_frame, text=f"✅ Present: {present}", 
                 bootstyle="success").pack(side=LEFT, padx=20)
        ttk.Label(stats_frame, text=f"❌ Absent: {absent}", 
                 bootstyle="danger").pack(side=LEFT, padx=20)
        ttk.Label(stats_frame, text=f"⏰ Late: {late}", 
                 bootstyle="warning").pack(side=LEFT, padx=20)
        ttk.Label(stats_frame, text=f"📊 Attendance Rate: {attendance_rate:.1f}%", 
                 bootstyle="info").pack(side=LEFT, padx=20)
        
        # Attendance table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        columns = ("Date", "Subject", "Status", "Remarks")
        self.attendance_tree = ttk.Treeview(tree_frame, columns=columns, 
                                           show="headings", yscrollcommand=scrollbar.set,
                                           height=15)
        scrollbar.config(command=self.attendance_tree.yview)
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=150, anchor=CENTER)
        
        self.attendance_tree.pack(fill=BOTH, expand=True)
        
        # Load attendance
        self.load_student_attendance()
    
    def load_student_attendance(self):
        """Load student attendance"""
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        self.cursor.execute('''
            SELECT a.date, s.subject_name, a.status, a.remarks
            FROM attendance a
            LEFT JOIN subjects s ON a.subject_id = s.id
            WHERE a.student_id = ?
            ORDER BY a.date DESC
        ''', (self.current_user_id,))
        
        records = self.cursor.fetchall()
        
        for record in records:
            tags = ()
            if record[2] == 'Present':
                tags = ('present',)
            elif record[2] == 'Absent':
                tags = ('absent',)
            elif record[2] == 'Late':
                tags = ('late',)
            
            self.attendance_tree.insert("", END, values=record, tags=tags)
        
        # Configure tag colors
        self.attendance_tree.tag_configure('present', background='#d4edda')
        self.attendance_tree.tag_configure('absent', background='#f8d7da')
        self.attendance_tree.tag_configure('late', background='#fff3cd')
    
    def show_teacher_dashboard(self):
        """Show teacher dashboard"""
        self.clear_window()
        
        # Header
        header = ttk.Frame(self.root, bootstyle="success")
        header.pack(fill=X, padx=10, pady=10)
        
        # Get teacher info
        self.cursor.execute(
            "SELECT name, teacher_id, subject FROM teachers WHERE id = ?",
            (self.current_user_id,)
        )
        teacher_info = self.cursor.fetchone()
        
        welcome_text = f"👨‍🏫 Welcome, Prof. {teacher_info[0]} | ID: {teacher_info[1]} | Subject: {teacher_info[2]}"
        ttk.Label(header, text=welcome_text, 
                 font=("Helvetica", 14, "bold"), bootstyle="inverse-success").pack(side=LEFT, padx=10)
        
        ttk.Button(header, text="🚪 Logout", command=self.logout, 
                  bootstyle="danger-outline").pack(side=RIGHT, padx=5)
        
        # Main content with Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Add Results Tab
        add_results_tab = ttk.Frame(notebook)
        notebook.add(add_results_tab, text="➕ Add Results")
        self.create_add_results_tab(add_results_tab)
        
        # View Results Tab
        view_results_tab = ttk.Frame(notebook)
        notebook.add(view_results_tab, text="📋 View Results")
        self.create_view_results_tab(view_results_tab)
        
        # Students Tab
        students_tab = ttk.Frame(notebook)
        notebook.add(students_tab, text="🎓 My Students")
        self.create_teacher_students_tab(students_tab)
        
        # Attendance Tab
        attendance_tab = ttk.Frame(notebook)
        notebook.add(attendance_tab, text="📅 Mark Attendance")
        self.create_teacher_attendance_tab(attendance_tab)
    
    def create_add_results_tab(self, parent):
        """Create add results tab for teachers"""
        form_frame = ttk.Labelframe(parent, text="Add New Result", padding=20)
        form_frame.pack(fill=BOTH, padx=20, pady=20)
        
        # Student selection
        ttk.Label(form_frame, text="Student:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.student_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.student_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Subject selection
        ttk.Label(form_frame, text="Subject:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.subject_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.subject_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Grade
        ttk.Label(form_frame, text="Grade (0-20):").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.grade_entry = ttk.Entry(form_frame, width=30)
        self.grade_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Exam type
        ttk.Label(form_frame, text="Exam Type:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.exam_type_combo = ttk.Combobox(form_frame, width=30, values=["Normal", "Quiz", "Mid-term", "Final"])
        self.exam_type_combo.set("Normal")
        self.exam_type_combo.grid(row=3, column=1, padx=5, pady=5)
        
        # Semester
        ttk.Label(form_frame, text="Semester:").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.semester_combo = ttk.Combobox(form_frame, width=30, values=["Semester 1", "Semester 2"])
        self.semester_combo.set("Semester 1")
        self.semester_combo.grid(row=4, column=1, padx=5, pady=5)
        
        # Academic year
        ttk.Label(form_frame, text="Academic Year:").grid(row=5, column=0, padx=5, pady=5, sticky=W)
        self.year_entry = ttk.Entry(form_frame, width=30)
        self.year_entry.insert(0, "2023-2024")
        self.year_entry.grid(row=5, column=1, padx=5, pady=5)
        
        # Remarks
        ttk.Label(form_frame, text="Remarks:").grid(row=6, column=0, padx=5, pady=5, sticky=W)
        self.remarks_entry = ttk.Entry(form_frame, width=30)
        self.remarks_entry.grid(row=6, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="📥 Add Result", command=self.add_result,
                  bootstyle="success").pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_result_form,
                  bootstyle="secondary").pack(side=LEFT, padx=10)
        
        # Load students and subjects
        self.load_students_for_teacher()
        self.load_subjects_for_teacher()
    
    def load_students_for_teacher(self):
        """Load students for the current teacher's subjects"""
        self.cursor.execute('''
            SELECT DISTINCT s.id, s.name, s.student_id
            FROM students s
            JOIN results r ON s.id = r.student_id
            WHERE r.teacher_id = ?
            UNION
            SELECT s.id, s.name, s.student_id
            FROM students s
            JOIN subjects sub ON s.class = sub.class
            WHERE sub.teacher_id = ?
        ''', (self.current_user_id, self.current_user_id))
        
        students = self.cursor.fetchall()
        student_list = [f"{s[2]} - {s[1]}" for s in students]
        self.student_combo['values'] = student_list
        if student_list:
            self.student_combo.set(student_list[0])
    
    def load_subjects_for_teacher(self):
        """Load subjects taught by the current teacher"""
        self.cursor.execute(
            "SELECT subject_name FROM subjects WHERE teacher_id = ?",
            (self.current_user_id,)
        )
        subjects = self.cursor.fetchall()
        subject_list = [s[0] for s in subjects]
        self.subject_combo['values'] = subject_list
        if subject_list:
            self.subject_combo.set(subject_list[0])
    
    def add_result(self):
        """Add a new result"""
        student_text = self.student_combo.get()
        subject_name = self.subject_combo.get()
        grade = self.grade_entry.get().strip()
        exam_type = self.exam_type_combo.get()
        semester = self.semester_combo.get()
        academic_year = self.year_entry.get().strip()
        remarks = self.remarks_entry.get().strip()
        
        if not all([student_text, subject_name, grade]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        try:
            grade_float = float(grade)
            if grade_float < 0 or grade_float > 20:
                messagebox.showerror("Error", "Grade must be between 0 and 20")
                return
        except ValueError:
            messagebox.showerror("Error", "Grade must be a number")
            return
        
        # Extract student ID from combo text
        student_id = student_text.split(" - ")[0]
        
        # Get student ID from database
        self.cursor.execute(
            "SELECT id FROM students WHERE student_id = ?",
            (student_id,)
        )
        student_db_id = self.cursor.fetchone()
        
        if not student_db_id:
            messagebox.showerror("Error", "Student not found")
            return
        
        # Get subject ID
        self.cursor.execute(
            "SELECT id FROM subjects WHERE subject_name = ? AND teacher_id = ?",
            (subject_name, self.current_user_id)
        )
        subject_db_id = self.cursor.fetchone()
        
        if not subject_db_id:
            messagebox.showerror("Error", "Subject not found")
            return
        
        # Insert result
        try:
            self.cursor.execute('''
                INSERT INTO results (student_id, subject_id, teacher_id, grade, 
                                   exam_type, semester, academic_year, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_db_id[0], subject_db_id[0], self.current_user_id, grade_float,
                 exam_type, semester, academic_year, remarks))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Result added successfully!")
            self.clear_result_form()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def clear_result_form(self):
        """Clear the result form"""
        self.grade_entry.delete(0, END)
        self.exam_type_combo.set("Normal")
        self.semester_combo.set("Semester 1")
        self.year_entry.delete(0, END)
        self.year_entry.insert(0, "2023-2024")
        self.remarks_entry.delete(0, END)
    
    def create_view_results_tab(self, parent):
        """Create view results tab for teachers"""
        # Filter frame
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Label(filter_frame, text="Filter by Subject:").pack(side=LEFT, padx=5)
        self.filter_subject_combo = ttk.Combobox(filter_frame, width=20, state="readonly")
        self.filter_subject_combo.pack(side=LEFT, padx=5)
        self.filter_subject_combo.bind('<<ComboboxSelected>>', self.filter_results)
        
        ttk.Label(filter_frame, text="Filter by Class:").pack(side=LEFT, padx=5)
        self.filter_class_combo = ttk.Combobox(filter_frame, width=20, state="readonly")
        self.filter_class_combo.pack(side=LEFT, padx=5)
        self.filter_class_combo.bind('<<ComboboxSelected>>', self.filter_results)
        
        ttk.Button(filter_frame, text="🔄 Refresh", command=self.load_teacher_results,
                  bootstyle="info").pack(side=LEFT, padx=10)
        
        # Results table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        columns = ("Student", "Student ID", "Subject", "Grade", "Exam Type", "Date", "Remarks")
        self.teacher_results_tree = ttk.Treeview(tree_frame, columns=columns,
                                                show="headings", yscrollcommand=scrollbar.set,
                                                height=15)
        scrollbar.config(command=self.teacher_results_tree.yview)
        
        for col in columns:
            self.teacher_results_tree.heading(col, text=col)
            self.teacher_results_tree.column(col, width=120, anchor=CENTER)
        
        self.teacher_results_tree.pack(fill=BOTH, expand=True)
        
        # Load initial data
        self.load_teacher_results()
        self.load_filter_options()
    
    def load_teacher_results(self):
        """Load teacher's results"""
        for item in self.teacher_results_tree.get_children():
            self.teacher_results_tree.delete(item)
        
        self.cursor.execute('''
            SELECT stu.name, stu.student_id, sub.subject_name, r.grade, 
                   r.exam_type, r.date, r.remarks
            FROM results r
            JOIN students stu ON r.student_id = stu.id
            JOIN subjects sub ON r.subject_id = sub.id
            WHERE r.teacher_id = ?
            ORDER BY r.date DESC
        ''', (self.current_user_id,))
        
        results = self.cursor.fetchall()
        
        for result in results:
            # Color code based on grade
            tags = ()
            grade = result[3]
            if grade >= 16:
                tags = ('excellent',)
            elif grade >= 14:
                tags = ('very_good',)
            elif grade >= 12:
                tags = ('good',)
            elif grade >= 10:
                tags = ('pass',)
            else:
                tags = ('fail',)
            
            self.teacher_results_tree.insert("", END, values=result, tags=tags)
        
        # Configure tag colors
        self.teacher_results_tree.tag_configure('excellent', background='#d4edda')
        self.teacher_results_tree.tag_configure('very_good', background='#fff3cd')
        self.teacher_results_tree.tag_configure('good', background='#d1ecf1')
        self.teacher_results_tree.tag_configure('pass', background='#f8d7da')
        self.teacher_results_tree.tag_configure('fail', background='#f5c6cb')
    
    def load_filter_options(self):
        """Load filter options for teacher results"""
        # Load subjects
        self.cursor.execute(
            "SELECT DISTINCT subject_name FROM subjects WHERE teacher_id = ?",
            (self.current_user_id,)
        )
        subjects = ['All'] + [s[0] for s in self.cursor.fetchall()]
        self.filter_subject_combo['values'] = subjects
        self.filter_subject_combo.set('All')
        
        # Load classes
        self.cursor.execute('''
            SELECT DISTINCT stu.class
            FROM results r
            JOIN students stu ON r.student_id = stu.id
            WHERE r.teacher_id = ?
            ORDER BY stu.class
        ''', (self.current_user_id,))
        classes = ['All'] + [c[0] for c in self.cursor.fetchall() if c[0]]
        self.filter_class_combo['values'] = classes
        self.filter_class_combo.set('All')
    
    def filter_results(self, event=None):
        """Filter results based on selected options"""
        subject = self.filter_subject_combo.get()
        class_filter = self.filter_class_combo.get()
        
        query = '''
            SELECT stu.name, stu.student_id, sub.subject_name, r.grade, 
                   r.exam_type, r.date, r.remarks
            FROM results r
            JOIN students stu ON r.student_id = stu.id
            JOIN subjects sub ON r.subject_id = sub.id
            WHERE r.teacher_id = ?
        '''
        params = [self.current_user_id]
        
        if subject != 'All':
            query += " AND sub.subject_name = ?"
            params.append(subject)
        
        if class_filter != 'All':
            query += " AND stu.class = ?"
            params.append(class_filter)
        
        query += " ORDER BY r.date DESC"
        
        # Clear tree
        for item in self.teacher_results_tree.get_children():
            self.teacher_results_tree.delete(item)
        
        # Execute filtered query
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        for result in results:
            tags = ()
            grade = result[3]
            if grade >= 16:
                tags = ('excellent',)
            elif grade >= 14:
                tags = ('very_good',)
            elif grade >= 12:
                tags = ('good',)
            elif grade >= 10:
                tags = ('pass',)
            else:
                tags = ('fail',)
            
            self.teacher_results_tree.insert("", END, values=result, tags=tags)
    
    def create_teacher_students_tab(self, parent):
        """Create teacher's students tab"""
        # Stats frame
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=X, padx=10, pady=10)
        
        # Calculate statistics
        self.cursor.execute('''
            SELECT COUNT(DISTINCT r.student_id), 
                   AVG(r.grade),
                   COUNT(*)
            FROM results r
            WHERE r.teacher_id = ?
        ''', (self.current_user_id,))
        
        stats = self.cursor.fetchone()
        
        ttk.Label(stats_frame, text=f"👥 Total Students: {stats[0] or 0}", 
                 bootstyle="info").pack(side=LEFT, padx=20)
        ttk.Label(stats_frame, text=f"⭐ Average Grade: {stats[1]:.2f if stats[1] else 'N/A'}", 
                 bootstyle="success").pack(side=LEFT, padx=20)
        ttk.Label(stats_frame, text=f"📊 Total Results: {stats[2] or 0}", 
                 bootstyle="warning").pack(side=LEFT, padx=20)
        
        # Students table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        columns = ("Student ID", "Name", "Class", "Email", "Phone", "Last Result", "Average")
        self.teacher_students_tree = ttk.Treeview(tree_frame, columns=columns,
                                                 show="headings", yscrollcommand=scrollbar.set,
                                                 height=15)
        scrollbar.config(command=self.teacher_students_tree.yview)
        
        for col in columns:
            self.teacher_students_tree.heading(col, text=col)
            self.teacher_students_tree.column(col, width=120, anchor=CENTER)
        
        self.teacher_students_tree.pack(fill=BOTH, expand=True)
        
        # Load students
        self.load_teacher_students()
    
    def load_teacher_students(self):
        """Load teacher's students"""
        for item in self.teacher_students_tree.get_children():
            self.teacher_students_tree.delete(item)
        
        self.cursor.execute('''
            SELECT DISTINCT 
                stu.student_id, stu.name, stu.class, stu.email, stu.phone,
                MAX(r.date) as last_date,
                AVG(r.grade) as avg_grade
            FROM students stu
            JOIN results r ON stu.id = r.student_id
            WHERE r.teacher_id = ?
            GROUP BY stu.id
            ORDER BY stu.name
        ''', (self.current_user_id,))
        
        students = self.cursor.fetchall()
        
        for student in students:
            self.teacher_students_tree.insert("", END, values=student)
    
    def create_teacher_attendance_tab(self, parent):
        """Create attendance tab for teachers"""
        form_frame = ttk.Labelframe(parent, text="Mark Attendance", padding=20)
        form_frame.pack(fill=BOTH, padx=20, pady=20)
        
        # Date selection
        ttk.Label(form_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.attendance_date = ttk.Entry(form_frame, width=30)
        self.attendance_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.attendance_date.grid(row=0, column=1, padx=5, pady=5)
        
        # Subject selection
        ttk.Label(form_frame, text="Subject:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.attendance_subject_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.attendance_subject_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Class selection
        ttk.Label(form_frame, text="Class:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.attendance_class_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.attendance_class_combo.grid(row=2, column=1, padx=5, pady=5)
        self.attendance_class_combo.bind('<<ComboboxSelected>>', self.load_class_students_attendance)
        
        # Student list with checkboxes
        ttk.Label(form_frame, text="Select Students:").grid(row=3, column=0, padx=5, pady=5, sticky=NW)
        
        self.attendance_students_frame = ttk.Frame(form_frame)
        self.attendance_students_frame.grid(row=3, column=1, padx=5, pady=5, sticky=W)
        
        # Status selection
        ttk.Label(form_frame, text="Status for selected:").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.attendance_status_var = tk.StringVar(value="Present")
        status_frame = ttk.Frame(form_frame)
        status_frame.grid(row=4, column=1, padx=5, pady=5, sticky=W)
        
        ttk.Radiobutton(status_frame, text="✅ Present", variable=self.attendance_status_var,
                       value="Present", bootstyle="success").pack(side=LEFT, padx=5)
        ttk.Radiobutton(status_frame, text="❌ Absent", variable=self.attendance_status_var,
                       value="Absent", bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Radiobutton(status_frame, text="⏰ Late", variable=self.attendance_status_var,
                       value="Late", bootstyle="warning").pack(side=LEFT, padx=5)
        
        # Remarks
        ttk.Label(form_frame, text="Remarks:").grid(row=5, column=0, padx=5, pady=5, sticky=W)
        self.attendance_remarks = ttk.Entry(form_frame, width=30)
        self.attendance_remarks.grid(row=5, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="✅ Mark Attendance", command=self.mark_attendance,
                  bootstyle="success").pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="🔄 Load Students", 
                  command=lambda: self.load_class_students_attendance(),
                  bootstyle="info").pack(side=LEFT, padx=10)
        
        # Load initial data
        self.load_attendance_options()
    
    def load_attendance_options(self):
        """Load options for attendance form"""
        # Load subjects
        self.cursor.execute(
            "SELECT DISTINCT subject_name FROM subjects WHERE teacher_id = ?",
            (self.current_user_id,)
        )
        subjects = [s[0] for s in self.cursor.fetchall()]
        self.attendance_subject_combo['values'] = subjects
        if subjects:
            self.attendance_subject_combo.set(subjects[0])
        
        # Load classes
        self.cursor.execute('''
            SELECT DISTINCT class 
            FROM students 
            WHERE class IS NOT NULL AND class != ''
            ORDER BY class
        ''')
        classes = [c[0] for c in self.cursor.fetchall()]
        self.attendance_class_combo['values'] = classes
        if classes:
            self.attendance_class_combo.set(classes[0])
            self.load_class_students_attendance()
    
    def load_class_students_attendance(self, event=None):
        """Load students for selected class"""
        selected_class = self.attendance_class_combo.get()
        
        # Clear previous checkboxes
        for widget in self.attendance_students_frame.winfo_children():
            widget.destroy()
        
        # Get students from selected class
        self.cursor.execute(
            "SELECT id, name, student_id FROM students WHERE class = ? ORDER BY name",
            (selected_class,)
        )
        students = self.cursor.fetchall()
        
        self.attendance_checkboxes = {}
        self.attendance_student_ids = {}
        
        for i, (student_id, name, stu_id) in enumerate(students):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.attendance_students_frame, text=f"{stu_id} - {name}", 
                               variable=var)
            cb.grid(row=i, column=0, sticky=W, pady=2)
            self.attendance_checkboxes[stu_id] = var
            self.attendance_student_ids[stu_id] = student_id
    
    def mark_attendance(self):
        """Mark attendance for selected students"""
        date = self.attendance_date.get().strip()
        subject_name = self.attendance_subject_combo.get()
        status = self.attendance_status_var.get()
        remarks = self.attendance_remarks.get().strip()
        
        if not date or not subject_name:
            messagebox.showerror("Error", "Please select date and subject")
            return
        
        # Get subject ID
        self.cursor.execute(
            "SELECT id FROM subjects WHERE subject_name = ? AND teacher_id = ?",
            (subject_name, self.current_user_id)
        )
        subject_result = self.cursor.fetchone()
        subject_id = subject_result[0] if subject_result else None
        
        # Mark attendance for each selected student
        count = 0
        for stu_id, var in self.attendance_checkboxes.items():
            if var.get():  # If checkbox is checked
                student_id = self.attendance_student_ids[stu_id]
                
                # Check if attendance already exists for this student, date, and subject
                self.cursor.execute('''
                    SELECT id FROM attendance 
                    WHERE student_id = ? AND date = ? AND subject_id = ?
                ''', (student_id, date, subject_id))
                
                existing = self.cursor.fetchone()
                
                if existing:
                    # Update existing record
                    self.cursor.execute('''
                        UPDATE attendance 
                        SET status = ?, remarks = ?
                        WHERE id = ?
                    ''', (status, remarks, existing[0]))
                else:
                    # Insert new record
                    self.cursor.execute('''
                        INSERT INTO attendance (student_id, date, status, subject_id, remarks)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (student_id, date, status, subject_id, remarks))
                
                count += 1
        
        self.conn.commit()
        messagebox.showinfo("Success", f"Attendance marked for {count} students")
    
    def show_admin_dashboard(self):
        """Show admin dashboard"""
        self.clear_window()
        
        # Header
        header = ttk.Frame(self.root, bootstyle="danger")
        header.pack(fill=X, padx=10, pady=10)
        
        welcome_text = f"👑 Admin Dashboard | Welcome, {self.current_user}"
        ttk.Label(header, text=welcome_text, 
                 font=("Helvetica", 14, "bold"), bootstyle="inverse-danger").pack(side=LEFT, padx=10)
        
        ttk.Button(header, text="🚪 Logout", command=self.logout, 
                  bootstyle="light-outline").pack(side=RIGHT, padx=5)
        
        # Stats frame
        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(fill=X, padx=10, pady=10)
        
        # Get statistics
        self.cursor.execute("SELECT COUNT(*) FROM students")
        student_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM results")
        result_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM subjects")
        subject_count = self.cursor.fetchone()[0]
        
        # Display stats
        stats = [
            (f"🎓 Students: {student_count}", "primary"),
            (f"👨‍🏫 Teachers: {teacher_count}", "success"),
            (f"📊 Results: {result_count}", "info"),
            (f"📚 Subjects: {subject_count}", "warning")
        ]
        
        for stat_text, style in stats:
            ttk.Label(stats_frame, text=stat_text, font=("Helvetica", 12),
                     bootstyle=style).pack(side=LEFT, padx=20)
        
        # Main content with Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Students Management Tab
        students_tab = ttk.Frame(notebook)
        notebook.add(students_tab, text="🎓 Manage Students")
        self.create_admin_students_tab(students_tab)
        
        # Teachers Management Tab
        teachers_tab = ttk.Frame(notebook)
        notebook.add(teachers_tab, text="👨‍🏫 Manage Teachers")
        self.create_admin_teachers_tab(teachers_tab)
        
        # Subjects Management Tab
        subjects_tab = ttk.Frame(notebook)
        notebook.add(subjects_tab, text="📚 Manage Subjects")
        self.create_admin_subjects_tab(subjects_tab)
        
        # Classes Management Tab
        classes_tab = ttk.Frame(notebook)
        notebook.add(classes_tab, text="🏫 Manage Classes")
        self.create_admin_classes_tab(classes_tab)
        
        # System Settings Tab
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="⚙️ System Settings")
        self.create_admin_settings_tab(settings_tab)
    
    def create_admin_students_tab(self, parent):
        """Create students management tab for admin"""
        # Form frame
        form_frame = ttk.Labelframe(parent, text="Add/Edit Student", padding=15)
        form_frame.pack(fill=X, padx=10, pady=10)
        
        # Row 1
        ttk.Label(form_frame, text="Student ID:*").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.admin_student_id = ttk.Entry(form_frame, width=25)
        self.admin_student_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="CNE:*").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.admin_student_cne = ttk.Entry(form_frame, width=25)
        self.admin_student_cne.grid(row=0, column=3, padx=5, pady=5)
        
        # Row 2
        ttk.Label(form_frame, text="Full Name:*").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.admin_student_name = ttk.Entry(form_frame, width=25)
        self.admin_student_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        self.admin_student_email = ttk.Entry(form_frame, width=25)
        self.admin_student_email.grid(row=1, column=3, padx=5, pady=5)
        
        # Row 3
        ttk.Label(form_frame, text="Password:*").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.admin_student_password = ttk.Entry(form_frame, width=25, show="•")
        self.admin_student_password.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Class:").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        self.admin_student_class = ttk.Combobox(form_frame, width=25, state="readonly")
        self.admin_student_class.grid(row=2, column=3, padx=5, pady=5)
        
        # Row 4
        ttk.Label(form_frame, text="Birth Date:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.admin_student_birth = ttk.Entry(form_frame, width=25)
        self.admin_student_birth.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Phone:").grid(row=3, column=2, padx=5, pady=5, sticky=W)
        self.admin_student_phone = ttk.Entry(form_frame, width=25)
        self.admin_student_phone.grid(row=3, column=3, padx=5, pady=5)
        
        # Row 5
        ttk.Label(form_frame, text="Address:").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.admin_student_address = ttk.Entry(form_frame, width=58)
        self.admin_student_address.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky=W)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=4, pady=15)
        
        ttk.Button(button_frame, text="➕ Add Student", command=self.admin_add_student,
                  bootstyle="success").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Update", command=self.admin_update_student,
                  bootstyle="warning").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.admin_delete_student,
                  bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Clear", command=self.admin_clear_student_form,
                  bootstyle="secondary").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="📋 View All", command=self.admin_load_students,
                  bootstyle="info").pack(side=LEFT, padx=5)
        
        # Students table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        columns = ("ID", "Student ID", "CNE", "Name", "Email", "Class", "Phone", "Registered")
        self.admin_students_tree = ttk.Treeview(tree_frame, columns=columns,
                                               show="headings", yscrollcommand=scrollbar.set,
                                               height=12)
        scrollbar.config(command=self.admin_students_tree.yview)
        
        for col in columns:
            self.admin_students_tree.heading(col, text=col)
            self.admin_students_tree.column(col, width=120, anchor=CENTER)
        
        self.admin_students_tree.pack(fill=BOTH, expand=True)
        self.admin_students_tree.bind('<<TreeviewSelect>>', self.admin_on_student_select)
        
        # Load classes for combo
        self.load_classes_for_admin()
        # Load students
        self.admin_load_students()
    
    def load_classes_for_admin(self):
        """Load classes for admin forms"""
        self.cursor.execute("SELECT class_name FROM classes ORDER BY class_name")
        classes = [c[0] for c in self.cursor.fetchall()]
        self.admin_student_class['values'] = classes
        if classes:
            self.admin_student_class.set(classes[0])
    
    def admin_load_students(self):
        """Load all students for admin"""
        for item in self.admin_students_tree.get_children():
            self.admin_students_tree.delete(item)
        
        self.cursor.execute('''
            SELECT id, student_id, cne, name, email, class, phone, 
                   strftime('%Y-%m-%d', created_at)
            FROM students 
            ORDER BY created_at DESC
        ''')
        
        students = self.cursor.fetchall()
        
        for student in students:
            self.admin_students_tree.insert("", END, values=student)
    
    def admin_on_student_select(self, event):
        """Handle student selection in admin tree"""
        selected = self.admin_students_tree.selection()
        if selected:
            item = self.admin_students_tree.item(selected[0])
            values = item['values']
            
            # Get full student details
            self.cursor.execute(
                "SELECT * FROM students WHERE id = ?", (values[0],)
            )
            student = self.cursor.fetchone()
            columns = [description[0] for description in self.cursor.description]
            
            # Fill form
            self.admin_student_id.delete(0, END)
            self.admin_student_id.insert(0, student[columns.index('student_id')])
            self.admin_student_cne.delete(0, END)
            self.admin_student_cne.insert(0, student[columns.index('cne')] or "")
            self.admin_student_name.delete(0, END)
            self.admin_student_name.insert(0, student[columns.index('name')])
            self.admin_student_email.delete(0, END)
            self.admin_student_email.insert(0, student[columns.index('email')] or "")
            self.admin_student_password.delete(0, END)
            self.admin_student_password.insert(0, "********")  # Placeholder
            if student[columns.index('class')]:
                self.admin_student_class.set(student[columns.index('class')])
            else:
                self.admin_student_class.set("")
            self.admin_student_birth.delete(0, END)
            self.admin_student_birth.insert(0, student[columns.index('birth_date')] or "")
            self.admin_student_phone.delete(0, END)
            self.admin_student_phone.insert(0, student[columns.index('phone')] or "")
            self.admin_student_address.delete(0, END)
            self.admin_student_address.insert(0, student[columns.index('address')] or "")
    
    def admin_add_student(self):
        """Add new student from admin panel"""
        # Get form data
        student_id = self.admin_student_id.get().strip()
        cne = self.admin_student_cne.get().strip()
        name = self.admin_student_name.get().strip()
        email = self.admin_student_email.get().strip()
        password = self.admin_student_password.get().strip()
        class_name = self.admin_student_class.get().strip()
        birth_date = self.admin_student_birth.get().strip()
        phone = self.admin_student_phone.get().strip()
        address = self.admin_student_address.get().strip()
        
        # Validation
        if not student_id or not cne or not name:
            messagebox.showerror("Error", "Student ID, CNE, and Name are required")
            return
        
        if password == "********":  # If updating without changing password
            password = None
        elif len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        # Check if student ID already exists
        self.cursor.execute(
            "SELECT id FROM students WHERE student_id = ?", (student_id,)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Student ID already exists")
            return
        
        # Check if CNE already exists
        if cne:
            self.cursor.execute(
                "SELECT id FROM students WHERE cne = ?", (cne,)
            )
            if self.cursor.fetchone():
                messagebox.showerror("Error", "CNE already exists")
                return
        
        # Hash password
        if password:
            hashed_password = self.hash_password(password)
        else:
            hashed_password = self.hash_password("1234")  # Default password
        
        # Insert student
        try:
            self.cursor.execute('''
                INSERT INTO students (student_id, cne, name, email, password, 
                                    class, birth_date, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, cne, name, email, hashed_password, class_name, 
                 birth_date, phone, address))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Student added successfully!")
            self.admin_clear_student_form()
            self.admin_load_students()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_update_student(self):
        """Update existing student"""
        selected = self.admin_students_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to update")
            return
        
        item = self.admin_students_tree.item(selected[0])
        student_db_id = item['values'][0]
        
        # Get form data
        student_id = self.admin_student_id.get().strip()
        cne = self.admin_student_cne.get().strip()
        name = self.admin_student_name.get().strip()
        email = self.admin_student_email.get().strip()
        password = self.admin_student_password.get().strip()
        class_name = self.admin_student_class.get().strip()
        birth_date = self.admin_student_birth.get().strip()
        phone = self.admin_student_phone.get().strip()
        address = self.admin_student_address.get().strip()
        
        # Validation
        if not student_id or not cne or not name:
            messagebox.showerror("Error", "Student ID, CNE, and Name are required")
            return
        
        # Check if student ID already exists (excluding current student)
        self.cursor.execute(
            "SELECT id FROM students WHERE student_id = ? AND id != ?",
            (student_id, student_db_id)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Student ID already exists")
            return
        
        # Check if CNE already exists (excluding current student)
        if cne:
            self.cursor.execute(
                "SELECT id FROM students WHERE cne = ? AND id != ?",
                (cne, student_db_id)
            )
            if self.cursor.fetchone():
                messagebox.showerror("Error", "CNE already exists")
                return
        
        # Update student
        try:
            if password != "********":  # If password changed
                hashed_password = self.hash_password(password)
                self.cursor.execute('''
                    UPDATE students 
                    SET student_id = ?, cne = ?, name = ?, email = ?, password = ?,
                        class = ?, birth_date = ?, phone = ?, address = ?
                    WHERE id = ?
                ''', (student_id, cne, name, email, hashed_password, class_name,
                     birth_date, phone, address, student_db_id))
            else:
                # Keep existing password
                self.cursor.execute('''
                    UPDATE students 
                    SET student_id = ?, cne = ?, name = ?, email = ?,
                        class = ?, birth_date = ?, phone = ?, address = ?
                    WHERE id = ?
                ''', (student_id, cne, name, email, class_name,
                     birth_date, phone, address, student_db_id))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Student updated successfully!")
            self.admin_load_students()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_delete_student(self):
        """Delete student from admin panel"""
        selected = self.admin_students_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete")
            return
        
        item = self.admin_students_tree.item(selected[0])
        student_id = item['values'][0]
        student_name = item['values'][3]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete student:\n{student_name}?\n\nThis will also delete all their results and attendance records!"):
            try:
                # Delete related results first (foreign key constraint)
                self.cursor.execute("DELETE FROM results WHERE student_id = ?", (student_id,))
                # Delete related attendance
                self.cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
                # Delete student
                self.cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
                self.conn.commit()
                
                messagebox.showinfo("Success", "Student deleted successfully!")
                self.admin_clear_student_form()
                self.admin_load_students()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_clear_student_form(self):
        """Clear admin student form"""
        self.admin_student_id.delete(0, END)
        self.admin_student_cne.delete(0, END)
        self.admin_student_name.delete(0, END)
        self.admin_student_email.delete(0, END)
        self.admin_student_password.delete(0, END)
        self.admin_student_password.insert(0, "1234")  # Default password
        self.admin_student_birth.delete(0, END)
        self.admin_student_phone.delete(0, END)
        self.admin_student_address.delete(0, END)
    
    def create_admin_teachers_tab(self, parent):
        """Create teachers management tab for admin"""
        # Form frame
        form_frame = ttk.Labelframe(parent, text="Add/Edit Teacher", padding=15)
        form_frame.pack(fill=X, padx=10, pady=10)
        
        # Row 1
        ttk.Label(form_frame, text="Teacher ID:*").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.admin_teacher_id = ttk.Entry(form_frame, width=25)
        self.admin_teacher_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Full Name:*").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.admin_teacher_name = ttk.Entry(form_frame, width=25)
        self.admin_teacher_name.grid(row=0, column=3, padx=5, pady=5)
        
        # Row 2
        ttk.Label(form_frame, text="Email:*").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.admin_teacher_email = ttk.Entry(form_frame, width=25)
        self.admin_teacher_email.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Password:*").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        self.admin_teacher_password = ttk.Entry(form_frame, width=25, show="•")
        self.admin_teacher_password.grid(row=1, column=3, padx=5, pady=5)
        
        # Row 3
        ttk.Label(form_frame, text="Subject:*").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.admin_teacher_subject = ttk.Entry(form_frame, width=25)
        self.admin_teacher_subject.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Qualification:").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        self.admin_teacher_qualification = ttk.Entry(form_frame, width=25)
        self.admin_teacher_qualification.grid(row=2, column=3, padx=5, pady=5)
        
        # Row 4
        ttk.Label(form_frame, text="Phone:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.admin_teacher_phone = ttk.Entry(form_frame, width=25)
        self.admin_teacher_phone.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=15)
        
        ttk.Button(button_frame, text="➕ Add Teacher", command=self.admin_add_teacher,
                  bootstyle="success").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Update", command=self.admin_update_teacher,
                  bootstyle="warning").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.admin_delete_teacher,
                  bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Clear", command=self.admin_clear_teacher_form,
                  bootstyle="secondary").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="📋 View All", command=self.admin_load_teachers,
                  bootstyle="info").pack(side=LEFT, padx=5)
        
        # Teachers table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        columns = ("ID", "Teacher ID", "Name", "Email", "Subject", "Qualification", "Phone", "Registered")
        self.admin_teachers_tree = ttk.Treeview(tree_frame, columns=columns,
                                               show="headings", yscrollcommand=scrollbar.set,
                                               height=12)
        scrollbar.config(command=self.admin_teachers_tree.yview)
        
        for col in columns:
            self.admin_teachers_tree.heading(col, text=col)
            self.admin_teachers_tree.column(col, width=120, anchor=CENTER)
        
        self.admin_teachers_tree.pack(fill=BOTH, expand=True)
        self.admin_teachers_tree.bind('<<TreeviewSelect>>', self.admin_on_teacher_select)
        
        # Load teachers
        self.admin_load_teachers()
    
    def admin_load_teachers(self):
        """Load all teachers for admin"""
        for item in self.admin_teachers_tree.get_children():
            self.admin_teachers_tree.delete(item)
        
        self.cursor.execute('''
            SELECT id, teacher_id, name, email, subject, qualification, phone,
                   strftime('%Y-%m-%d', created_at)
            FROM teachers 
            ORDER BY created_at DESC
        ''')
        
        teachers = self.cursor.fetchall()
        
        for teacher in teachers:
            self.admin_teachers_tree.insert("", END, values=teacher)
    
    def admin_on_teacher_select(self, event):
        """Handle teacher selection in admin tree"""
        selected = self.admin_teachers_tree.selection()
        if selected:
            item = self.admin_teachers_tree.item(selected[0])
            values = item['values']
            
            # Get full teacher details
            self.cursor.execute(
                "SELECT * FROM teachers WHERE id = ?", (values[0],)
            )
            teacher = self.cursor.fetchone()
            columns = [description[0] for description in self.cursor.description]
            
            # Fill form
            self.admin_teacher_id.delete(0, END)
            self.admin_teacher_id.insert(0, teacher[columns.index('teacher_id')])
            self.admin_teacher_name.delete(0, END)
            self.admin_teacher_name.insert(0, teacher[columns.index('name')])
            self.admin_teacher_email.delete(0, END)
            self.admin_teacher_email.insert(0, teacher[columns.index('email')] or "")
            self.admin_teacher_password.delete(0, END)
            self.admin_teacher_password.insert(0, "********")  # Placeholder
            self.admin_teacher_subject.delete(0, END)
            self.admin_teacher_subject.insert(0, teacher[columns.index('subject')] or "")
            self.admin_teacher_qualification.delete(0, END)
            self.admin_teacher_qualification.insert(0, teacher[columns.index('qualification')] or "")
            self.admin_teacher_phone.delete(0, END)
            self.admin_teacher_phone.insert(0, teacher[columns.index('phone')] or "")
    
    def admin_add_teacher(self):
        """Add new teacher from admin panel"""
        # Get form data
        teacher_id = self.admin_teacher_id.get().strip()
        name = self.admin_teacher_name.get().strip()
        email = self.admin_teacher_email.get().strip()
        password = self.admin_teacher_password.get().strip()
        subject = self.admin_teacher_subject.get().strip()
        qualification = self.admin_teacher_qualification.get().strip()
        phone = self.admin_teacher_phone.get().strip()
        
        # Validation
        if not teacher_id or not name or not email or not subject:
            messagebox.showerror("Error", "Teacher ID, Name, Email, and Subject are required")
            return
        
        if password == "********":  # If placeholder
            password = None
        elif len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        # Check if teacher ID already exists
        self.cursor.execute(
            "SELECT id FROM teachers WHERE teacher_id = ?", (teacher_id,)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Teacher ID already exists")
            return
        
        # Check if email already exists
        self.cursor.execute(
            "SELECT id FROM teachers WHERE email = ?", (email,)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Email already exists")
            return
        
        # Hash password
        if password:
            hashed_password = self.hash_password(password)
        else:
            hashed_password = self.hash_password("1234")  # Default password
        
        # Insert teacher
        try:
            self.cursor.execute('''
                INSERT INTO teachers (teacher_id, name, email, password, subject, qualification, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (teacher_id, name, email, hashed_password, subject, qualification, phone))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Teacher added successfully!")
            self.admin_clear_teacher_form()
            self.admin_load_teachers()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_update_teacher(self):
        """Update existing teacher"""
        selected = self.admin_teachers_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a teacher to update")
            return
        
        item = self.admin_teachers_tree.item(selected[0])
        teacher_db_id = item['values'][0]
        
        # Get form data
        teacher_id = self.admin_teacher_id.get().strip()
        name = self.admin_teacher_name.get().strip()
        email = self.admin_teacher_email.get().strip()
        password = self.admin_teacher_password.get().strip()
        subject = self.admin_teacher_subject.get().strip()
        qualification = self.admin_teacher_qualification.get().strip()
        phone = self.admin_teacher_phone.get().strip()
        
        # Validation
        if not teacher_id or not name or not email or not subject:
            messagebox.showerror("Error", "Teacher ID, Name, Email, and Subject are required")
            return
        
        # Check if teacher ID already exists (excluding current teacher)
        self.cursor.execute(
            "SELECT id FROM teachers WHERE teacher_id = ? AND id != ?",
            (teacher_id, teacher_db_id)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Teacher ID already exists")
            return
        
        # Check if email already exists (excluding current teacher)
        self.cursor.execute(
            "SELECT id FROM teachers WHERE email = ? AND id != ?",
            (email, teacher_db_id)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Email already exists")
            return
        
        # Update teacher
        try:
            if password != "********":  # If password changed
                hashed_password = self.hash_password(password)
                self.cursor.execute('''
                    UPDATE teachers 
                    SET teacher_id = ?, name = ?, email = ?, password = ?,
                        subject = ?, qualification = ?, phone = ?
                    WHERE id = ?
                ''', (teacher_id, name, email, hashed_password, subject,
                     qualification, phone, teacher_db_id))
            else:
                # Keep existing password
                self.cursor.execute('''
                    UPDATE teachers 
                    SET teacher_id = ?, name = ?, email = ?,
                        subject = ?, qualification = ?, phone = ?
                    WHERE id = ?
                ''', (teacher_id, name, email, subject,
                     qualification, phone, teacher_db_id))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Teacher updated successfully!")
            self.admin_load_teachers()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_delete_teacher(self):
        """Delete teacher from admin panel"""
        selected = self.admin_teachers_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a teacher to delete")
            return
        
        item = self.admin_teachers_tree.item(selected[0])
        teacher_id = item['values'][0]
        teacher_name = item['values'][2]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete teacher:\n{teacher_name}?\n\nThis will also delete all their results and subjects!"):
            try:
                # Delete related results first
                self.cursor.execute("DELETE FROM results WHERE teacher_id = ?", (teacher_id,))
                # Update subjects to remove teacher reference
                self.cursor.execute("UPDATE subjects SET teacher_id = NULL WHERE teacher_id = ?", (teacher_id,))
                # Delete teacher
                self.cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
                self.conn.commit()
                
                messagebox.showinfo("Success", "Teacher deleted successfully!")
                self.admin_clear_teacher_form()
                self.admin_load_teachers()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_clear_teacher_form(self):
        """Clear admin teacher form"""
        self.admin_teacher_id.delete(0, END)
        self.admin_teacher_name.delete(0, END)
        self.admin_teacher_email.delete(0, END)
        self.admin_teacher_password.delete(0, END)
        self.admin_teacher_password.insert(0, "1234")  # Default password
        self.admin_teacher_subject.delete(0, END)
        self.admin_teacher_qualification.delete(0, END)
        self.admin_teacher_phone.delete(0, END)
    
    def create_admin_subjects_tab(self, parent):
        """Create subjects management tab for admin"""
        # Form frame
        form_frame = ttk.Labelframe(parent, text="Add/Edit Subject", padding=15)
        form_frame.pack(fill=X, padx=10, pady=10)
        
        # Form fields
        ttk.Label(form_frame, text="Subject Code:*").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.admin_subject_code = ttk.Entry(form_frame, width=25)
        self.admin_subject_code.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Subject Name:*").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.admin_subject_name = ttk.Entry(form_frame, width=25)
        self.admin_subject_name.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Teacher:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.admin_subject_teacher = ttk.Combobox(form_frame, width=25, state="readonly")
        self.admin_subject_teacher.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Class:").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        self.admin_subject_class = ttk.Combobox(form_frame, width=25, state="readonly")
        self.admin_subject_class.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Credits:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.admin_subject_credits = ttk.Entry(form_frame, width=25)
        self.admin_subject_credits.insert(0, "3")
        self.admin_subject_credits.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=15)
        
        ttk.Button(button_frame, text="➕ Add Subject", command=self.admin_add_subject,
                  bootstyle="success").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Update", command=self.admin_update_subject,
                  bootstyle="warning").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.admin_delete_subject,
                  bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Clear", command=self.admin_clear_subject_form,
                  bootstyle="secondary").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="📋 View All", command=self.admin_load_subjects,
                  bootstyle="info").pack(side=LEFT, padx=5)
        
        # Subjects table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        columns = ("ID", "Code", "Name", "Teacher", "Class", "Credits")
        self.admin_subjects_tree = ttk.Treeview(tree_frame, columns=columns,
                                               show="headings", yscrollcommand=scrollbar.set,
                                               height=12)
        scrollbar.config(command=self.admin_subjects_tree.yview)
        
        for col in columns:
            self.admin_subjects_tree.heading(col, text=col)
            self.admin_subjects_tree.column(col, width=120, anchor=CENTER)
        
        self.admin_subjects_tree.pack(fill=BOTH, expand=True)
        self.admin_subjects_tree.bind('<<TreeviewSelect>>', self.admin_on_subject_select)
        
        # Load data
        self.load_teachers_for_subjects()
        self.load_classes_for_subjects()
        self.admin_load_subjects()
    
    def load_teachers_for_subjects(self):
        """Load teachers for subject form"""
        self.cursor.execute("SELECT id, name FROM teachers ORDER BY name")
        teachers = self.cursor.fetchall()
        teacher_list = ["None"] + [f"{t[0]} - {t[1]}" for t in teachers]
        self.admin_subject_teacher['values'] = teacher_list
        self.admin_subject_teacher.set("None")
    
    def load_classes_for_subjects(self):
        """Load classes for subject form"""
        self.cursor.execute("SELECT class_name FROM classes ORDER BY class_name")
        classes = [c[0] for c in self.cursor.fetchall()]
        self.admin_subject_class['values'] = classes
        if classes:
            self.admin_subject_class.set(classes[0])
    
    def admin_load_subjects(self):
        """Load all subjects for admin"""
        for item in self.admin_subjects_tree.get_children():
            self.admin_subjects_tree.delete(item)
        
        self.cursor.execute('''
            SELECT s.id, s.subject_code, s.subject_name, 
                   COALESCE(t.name, 'Not Assigned'), 
                   COALESCE(s.class, 'All Classes'), s.credits
            FROM subjects s
            LEFT JOIN teachers t ON s.teacher_id = t.id
            ORDER BY s.subject_name
        ''')
        
        subjects = self.cursor.fetchall()
        
        for subject in subjects:
            self.admin_subjects_tree.insert("", END, values=subject)
    
    def admin_on_subject_select(self, event):
        """Handle subject selection in admin tree"""
        selected = self.admin_subjects_tree.selection()
        if selected:
            item = self.admin_subjects_tree.item(selected[0])
            values = item['values']
            
            # Get full subject details
            self.cursor.execute(
                "SELECT * FROM subjects WHERE id = ?", (values[0],)
            )
            subject = self.cursor.fetchone()
            columns = [description[0] for description in self.cursor.description]
            
            # Fill form
            self.admin_subject_code.delete(0, END)
            self.admin_subject_code.insert(0, subject[columns.index('subject_code')])
            self.admin_subject_name.delete(0, END)
            self.admin_subject_name.insert(0, subject[columns.index('subject_name')])
            
            # Set teacher
            teacher_id = subject[columns.index('teacher_id')]
            if teacher_id:
                self.cursor.execute("SELECT name FROM teachers WHERE id = ?", (teacher_id,))
                teacher_name = self.cursor.fetchone()[0]
                self.admin_subject_teacher.set(f"{teacher_id} - {teacher_name}")
            else:
                self.admin_subject_teacher.set("None")
            
            # Set class
            class_name = subject[columns.index('class')]
            if class_name:
                self.admin_subject_class.set(class_name)
            else:
                self.admin_subject_class.set("")
            
            self.admin_subject_credits.delete(0, END)
            self.admin_subject_credits.insert(0, str(subject[columns.index('credits')] or "3"))
    
    def admin_add_subject(self):
        """Add new subject from admin panel"""
        # Get form data
        subject_code = self.admin_subject_code.get().strip()
        subject_name = self.admin_subject_name.get().strip()
        teacher_text = self.admin_subject_teacher.get().strip()
        class_name = self.admin_subject_class.get().strip()
        credits = self.admin_subject_credits.get().strip()
        
        # Validation
        if not subject_code or not subject_name:
            messagebox.showerror("Error", "Subject Code and Name are required")
            return
        
        # Check if subject code already exists
        self.cursor.execute(
            "SELECT id FROM subjects WHERE subject_code = ?", (subject_code,)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Subject Code already exists")
            return
        
        # Parse teacher ID
        teacher_id = None
        if teacher_text != "None":
            try:
                teacher_id = int(teacher_text.split(" - ")[0])
            except:
                messagebox.showerror("Error", "Invalid teacher selection")
                return
        
        # Parse credits
        try:
            credits_int = int(credits) if credits else 3
        except ValueError:
            messagebox.showerror("Error", "Credits must be a number")
            return
        
        # Insert subject
        try:
            self.cursor.execute('''
                INSERT INTO subjects (subject_code, subject_name, teacher_id, class, credits)
                VALUES (?, ?, ?, ?, ?)
            ''', (subject_code, subject_name, teacher_id, class_name, credits_int))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Subject added successfully!")
            self.admin_clear_subject_form()
            self.admin_load_subjects()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_update_subject(self):
        """Update existing subject"""
        selected = self.admin_subjects_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a subject to update")
            return
        
        item = self.admin_subjects_tree.item(selected[0])
        subject_db_id = item['values'][0]
        
        # Get form data
        subject_code = self.admin_subject_code.get().strip()
        subject_name = self.admin_subject_name.get().strip()
        teacher_text = self.admin_subject_teacher.get().strip()
        class_name = self.admin_subject_class.get().strip()
        credits = self.admin_subject_credits.get().strip()
        
        # Validation
        if not subject_code or not subject_name:
            messagebox.showerror("Error", "Subject Code and Name are required")
            return
        
        # Check if subject code already exists (excluding current subject)
        self.cursor.execute(
            "SELECT id FROM subjects WHERE subject_code = ? AND id != ?",
            (subject_code, subject_db_id)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Subject Code already exists")
            return
        
        # Parse teacher ID
        teacher_id = None
        if teacher_text != "None":
            try:
                teacher_id = int(teacher_text.split(" - ")[0])
            except:
                messagebox.showerror("Error", "Invalid teacher selection")
                return
        
        # Parse credits
        try:
            credits_int = int(credits) if credits else 3
        except ValueError:
            messagebox.showerror("Error", "Credits must be a number")
            return
        
        # Update subject
        try:
            self.cursor.execute('''
                UPDATE subjects 
                SET subject_code = ?, subject_name = ?, teacher_id = ?, class = ?, credits = ?
                WHERE id = ?
            ''', (subject_code, subject_name, teacher_id, class_name, credits_int, subject_db_id))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Subject updated successfully!")
            self.admin_load_subjects()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_delete_subject(self):
        """Delete subject from admin panel"""
        selected = self.admin_subjects_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a subject to delete")
            return
        
        item = self.admin_subjects_tree.item(selected[0])
        subject_id = item['values'][0]
        subject_name = item['values'][2]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete subject:\n{subject_name}?\n\nThis will also delete all related results!"):
            try:
                # Delete related results first
                self.cursor.execute("DELETE FROM results WHERE subject_id = ?", (subject_id,))
                # Delete subject
                self.cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
                self.conn.commit()
                
                messagebox.showinfo("Success", "Subject deleted successfully!")
                self.admin_clear_subject_form()
                self.admin_load_subjects()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_clear_subject_form(self):
        """Clear admin subject form"""
        self.admin_subject_code.delete(0, END)
        self.admin_subject_name.delete(0, END)
        self.admin_subject_teacher.set("None")
        if self.admin_subject_class['values']:
            self.admin_subject_class.set(self.admin_subject_class['values'][0])
        self.admin_subject_credits.delete(0, END)
        self.admin_subject_credits.insert(0, "3")
    
    def create_admin_classes_tab(self, parent):
        """Create classes management tab for admin"""
        # Form frame
        form_frame = ttk.Labelframe(parent, text="Add/Edit Class", padding=15)
        form_frame.pack(fill=X, padx=10, pady=10)
        
        # Form fields
        ttk.Label(form_frame, text="Class Name:*").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.admin_class_name = ttk.Entry(form_frame, width=25)
        self.admin_class_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Level:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.admin_class_level = ttk.Combobox(form_frame, width=25, 
                                             values=["Primary", "Middle School", "High School", "University"])
        self.admin_class_level.set("High School")
        self.admin_class_level.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Capacity:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.admin_class_capacity = ttk.Entry(form_frame, width=25)
        self.admin_class_capacity.insert(0, "30")
        self.admin_class_capacity.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Academic Year:").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        self.admin_class_year = ttk.Entry(form_frame, width=25)
        self.admin_class_year.insert(0, "2023-2024")
        self.admin_class_year.grid(row=1, column=3, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        ttk.Button(button_frame, text="➕ Add Class", command=self.admin_add_class,
                  bootstyle="success").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Update", command=self.admin_update_class,
                  bootstyle="warning").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.admin_delete_class,
                  bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Clear", command=self.admin_clear_class_form,
                  bootstyle="secondary").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="📋 View All", command=self.admin_load_classes,
                  bootstyle="info").pack(side=LEFT, padx=5)
        
        # Classes table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        columns = ("ID", "Class Name", "Level", "Capacity", "Year", "Student Count")
        self.admin_classes_tree = ttk.Treeview(tree_frame, columns=columns,
                                              show="headings", yscrollcommand=scrollbar.set,
                                              height=12)
        scrollbar.config(command=self.admin_classes_tree.yview)
        
        for col in columns:
            self.admin_classes_tree.heading(col, text=col)
            self.admin_classes_tree.column(col, width=120, anchor=CENTER)
        
        self.admin_classes_tree.pack(fill=BOTH, expand=True)
        self.admin_classes_tree.bind('<<TreeviewSelect>>', self.admin_on_class_select)
        
        # Load classes
        self.admin_load_classes()
    
    def admin_load_classes(self):
        """Load all classes for admin"""
        for item in self.admin_classes_tree.get_children():
            self.admin_classes_tree.delete(item)
        
        self.cursor.execute('''
            SELECT c.id, c.class_name, c.level, c.capacity, c.year,
                   (SELECT COUNT(*) FROM students s WHERE s.class = c.class_name) as student_count
            FROM classes c
            ORDER BY c.class_name
        ''')
        
        classes = self.cursor.fetchall()
        
        for class_item in classes:
            self.admin_classes_tree.insert("", END, values=class_item)
    
    def admin_on_class_select(self, event):
        """Handle class selection in admin tree"""
        selected = self.admin_classes_tree.selection()
        if selected:
            item = self.admin_classes_tree.item(selected[0])
            values = item['values']
            
            # Get full class details
            self.cursor.execute(
                "SELECT * FROM classes WHERE id = ?", (values[0],)
            )
            class_item = self.cursor.fetchone()
            columns = [description[0] for description in self.cursor.description]
            
            # Fill form
            self.admin_class_name.delete(0, END)
            self.admin_class_name.insert(0, class_item[columns.index('class_name')])
            self.admin_class_level.set(class_item[columns.index('level')] or "High School")
            self.admin_class_capacity.delete(0, END)
            self.admin_class_capacity.insert(0, str(class_item[columns.index('capacity')] or "30"))
            self.admin_class_year.delete(0, END)
            self.admin_class_year.insert(0, class_item[columns.index('year')] or "2023-2024")
    
    def admin_add_class(self):
        """Add new class from admin panel"""
        # Get form data
        class_name = self.admin_class_name.get().strip()
        level = self.admin_class_level.get().strip()
        capacity = self.admin_class_capacity.get().strip()
        year = self.admin_class_year.get().strip()
        
        # Validation
        if not class_name:
            messagebox.showerror("Error", "Class Name is required")
            return
        
        # Check if class already exists
        self.cursor.execute(
            "SELECT id FROM classes WHERE class_name = ?", (class_name,)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Class already exists")
            return
        
        # Parse capacity
        try:
            capacity_int = int(capacity) if capacity else 30
        except ValueError:
            messagebox.showerror("Error", "Capacity must be a number")
            return
        
        # Insert class
        try:
            self.cursor.execute('''
                INSERT INTO classes (class_name, level, capacity, year)
                VALUES (?, ?, ?, ?)
            ''', (class_name, level, capacity_int, year))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Class added successfully!")
            self.admin_clear_class_form()
            self.admin_load_classes()
            # Refresh class combobox in other forms
            self.load_classes_for_admin()
            self.load_classes_for_subjects()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_update_class(self):
        """Update existing class"""
        selected = self.admin_classes_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a class to update")
            return
        
        item = self.admin_classes_tree.item(selected[0])
        class_db_id = item['values'][0]
        old_class_name = item['values'][1]
        
        # Get form data
        class_name = self.admin_class_name.get().strip()
        level = self.admin_class_level.get().strip()
        capacity = self.admin_class_capacity.get().strip()
        year = self.admin_class_year.get().strip()
        
        # Validation
        if not class_name:
            messagebox.showerror("Error", "Class Name is required")
            return
        
        # Check if class already exists (excluding current class)
        self.cursor.execute(
            "SELECT id FROM classes WHERE class_name = ? AND id != ?",
            (class_name, class_db_id)
        )
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Class already exists")
            return
        
        # Parse capacity
        try:
            capacity_int = int(capacity) if capacity else 30
        except ValueError:
            messagebox.showerror("Error", "Capacity must be a number")
            return
        
        # Update class
        try:
            self.cursor.execute('''
                UPDATE classes 
                SET class_name = ?, level = ?, capacity = ?, year = ?
                WHERE id = ?
            ''', (class_name, level, capacity_int, year, class_db_id))
            
            # Update students' class if class name changed
            if old_class_name != class_name:
                self.cursor.execute('''
                    UPDATE students 
                    SET class = ? 
                    WHERE class = ?
                ''', (class_name, old_class_name))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Class updated successfully!")
            self.admin_load_classes()
            # Refresh class combobox in other forms
            self.load_classes_for_admin()
            self.load_classes_for_subjects()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_delete_class(self):
        """Delete class from admin panel"""
        selected = self.admin_classes_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a class to delete")
            return
        
        item = self.admin_classes_tree.item(selected[0])
        class_id = item['values'][0]
        class_name = item['values'][1]
        
        # Check if class has students
        self.cursor.execute(
            "SELECT COUNT(*) FROM students WHERE class = ?", (class_name,)
        )
        student_count = self.cursor.fetchone()[0]
        
        if student_count > 0:
            messagebox.showerror("Error", 
                               f"Cannot delete class '{class_name}' because it has {student_count} student(s).\n"
                               "Please reassign or delete the students first.")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete class:\n{class_name}?"):
            try:
                # Delete class
                self.cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
                self.conn.commit()
                
                messagebox.showinfo("Success", "Class deleted successfully!")
                self.admin_clear_class_form()
                self.admin_load_classes()
                # Refresh class combobox in other forms
                self.load_classes_for_admin()
                self.load_classes_for_subjects()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")
    
    def admin_clear_class_form(self):
        """Clear admin class form"""
        self.admin_class_name.delete(0, END)
        self.admin_class_level.set("High School")
        self.admin_class_capacity.delete(0, END)
        self.admin_class_capacity.insert(0, "30")
        self.admin_class_year.delete(0, END)
        self.admin_class_year.insert(0, "2023-2024")
    
    def create_admin_settings_tab(self, parent):
        """Create system settings tab for admin"""
        # Database management frame
        db_frame = ttk.Labelframe(parent, text="Database Management", padding=20)
        db_frame.pack(fill=X, padx=20, pady=20)
        
        ttk.Button(db_frame, text="💾 Backup Database", command=self.backup_database,
                  bootstyle="info", width=20).pack(side=LEFT, padx=10)
        ttk.Button(db_frame, text="🔄 Reset Database", command=self.reset_database,
                  bootstyle="danger", width=20).pack(side=LEFT, padx=10)
        ttk.Button(db_frame, text="📊 Export to Excel", command=self.export_to_excel,
                  bootstyle="success", width=20).pack(side=LEFT, padx=10)
        
        # System info frame
        info_frame = ttk.Labelframe(parent, text="System Information", padding=20)
        info_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Get system statistics
        self.cursor.execute("SELECT COUNT(*) FROM students")
        total_students = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM teachers")
        total_teachers = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM results")
        total_results = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM subjects")
        total_subjects = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM classes")
        total_classes = self.cursor.fetchone()[0]
        
        info_text = f"""
        📊 System Statistics:
        
        • Total Students: {total_students}
        • Total Teachers: {total_teachers}
        • Total Results: {total_results}
        • Total Subjects: {total_subjects}
        • Total Classes: {total_classes}
        
        ⚙️ System Information:
        
        • Database: SQLite3
        • Frontend: Tkinter with ttkbootstrap
        • Version: 1.0.0
        • Developed for: Moroccan Education System
        
        👑 Admin Account:
        
        • Username: admin
        • Password: admin123 (Change recommended)
        """
        
        ttk.Label(info_frame, text=info_text, font=("Consolas", 10)).pack(anchor=W)
    
    def backup_database(self):
        """Create a backup of the database"""
        import shutil
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"massar_backup_{timestamp}.db"
        
        try:
            shutil.copy2('massar_system.db', backup_file)
            messagebox.showinfo("Backup Successful", 
                              f"Database backed up successfully to:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Error creating backup: {e}")
    
    def reset_database(self):
        """Reset the database (warning: will delete all data!)"""
        if messagebox.askyesno("⚠️ Danger Zone", 
                              "Are you absolutely sure you want to reset the database?\n\n"
                              "This will DELETE ALL DATA and cannot be undone!"):
            if messagebox.askyesno("Confirm Reset", 
                                  "LAST WARNING: This will delete ALL students, teachers, results, etc.\n"
                                  "Are you really sure?"):
                try:
                    # Close current connection
                    self.conn.close()
                    
                    # Delete database file
                    if os.path.exists('massar_system.db'):
                        os.remove('massar_system.db')
                    
                    # Reinitialize database
                    self.init_database()
                    
                    messagebox.showinfo("Reset Complete", 
                                      "Database has been reset to initial state.\n"
                                      "Default admin account: admin / admin123")
                    
                    # Reload login screen
                    self.logout()
                except Exception as e:
                    messagebox.showerror("Reset Failed", f"Error resetting database: {e}")
    
    def export_to_excel(self):
        """Export data to Excel file"""
        try:
            # Create a Pandas Excel writer
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_file = f"massar_export_{timestamp}.xlsx"
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Export each table
                tables = ['students', 'teachers', 'subjects', 'results', 'classes', 'attendance']
                
                for table in tables:
                    df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)
                    if not df.empty:
                        df.to_excel(writer, sheet_name=table, index=False)
                
                # Adjust column widths
                workbook = writer.book
                for table in tables:
                    if table in writer.sheets:
                        worksheet = writer.sheets[table]
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[column_letter].width = adjusted_width
            
            messagebox.showinfo("Export Successful", 
                              f"Data exported successfully to:\n{excel_file}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error exporting to Excel: {e}")
    
    def __del__(self):
        """Destructor to close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    # Create and run the application
    root = ttk.Window(themename="cosmo")
    app = StudentManagementSystem(root)
    root.mainloop()

