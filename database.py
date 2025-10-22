"""
Ders Programı Uygulaması - Veritabanı Modülü
Database module for the Course Schedule Application
"""
import sqlite3
from config import Config

def get_db():
    """
    SQLite veritabanı bağlantısı oluşturur
    Creates SQLite database connection
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Veritabanı tablolarını oluşturur
    Creates database tables
    """
    conn = get_db()
    cursor = conn.cursor()

    # Öğretmenler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            branch TEXT NOT NULL,
            schedule TEXT NOT NULL
        )
    ''')

    # Öğrenciler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            class TEXT NOT NULL,
            restrictions TEXT,
            priorities TEXT,
            manual_lessons TEXT
        )
    ''')

    # Mevcut tabloya yeni kolonları ekle (eğer yoksa)
    # Add new columns to existing table (if not exists)
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN priorities TEXT')
    except sqlite3.OperationalError:
        pass  # Kolon zaten var / Column already exists

    try:
        cursor.execute('ALTER TABLE students ADD COLUMN manual_lessons TEXT')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE students ADD COLUMN teacher_blocks TEXT')
    except sqlite3.OperationalError:
        pass

    # Öğretmen tablosuna bloklama kolonu ekle
    try:
        cursor.execute('ALTER TABLE teachers ADD COLUMN blocked_slots TEXT')
    except sqlite3.OperationalError:
        pass

    # Kaydedilmiş programlar tablosu
    # Saved schedules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            schedule_data TEXT NOT NULL,
            teachers_snapshot TEXT,
            students_snapshot TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_teachers():
    """
    Tüm öğretmenleri getirir
    Retrieves all teachers
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teachers ORDER BY name, surname')
    teachers = cursor.fetchall()
    conn.close()
    return teachers

def get_students():
    """
    Tüm öğrencileri getirir
    Retrieves all students
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students ORDER BY name, surname')
    students = cursor.fetchall()
    conn.close()
    return students

def get_teacher_by_id(teacher_id):
    """
    ID'ye göre öğretmen getirir
    Retrieves teacher by ID
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teachers WHERE id = ?', (teacher_id,))
    teacher = cursor.fetchone()
    conn.close()
    return teacher

def get_student_by_id(student_id):
    """
    ID'ye göre öğrenci getirir
    Retrieves student by ID
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def add_teacher(name, surname, branch, schedule):
    """
    Yeni öğretmen ekler
    Adds new teacher
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO teachers (name, surname, branch, schedule) VALUES (?, ?, ?, ?)',
        (name, surname, branch, schedule)
    )
    conn.commit()
    teacher_id = cursor.lastrowid
    conn.close()
    return teacher_id

def add_student(name, surname, class_name, restrictions='', priorities='', manual_lessons=''):
    """
    Yeni öğrenci ekler
    Adds new student
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO students (name, surname, class, restrictions, priorities, manual_lessons) VALUES (?, ?, ?, ?, ?, ?)',
        (name, surname, class_name, restrictions, priorities, manual_lessons)
    )
    conn.commit()
    student_id = cursor.lastrowid
    conn.close()
    return student_id

def update_teacher(teacher_id, name, surname, branch, schedule, blocked_slots=None):
    """
    Öğretmen bilgilerini günceller
    Updates teacher information
    """
    conn = get_db()
    cursor = conn.cursor()
    if blocked_slots is not None:
        cursor.execute(
            'UPDATE teachers SET name = ?, surname = ?, branch = ?, schedule = ?, blocked_slots = ? WHERE id = ?',
            (name, surname, branch, schedule, blocked_slots, teacher_id)
        )
    else:
        cursor.execute(
            'UPDATE teachers SET name = ?, surname = ?, branch = ?, schedule = ? WHERE id = ?',
            (name, surname, branch, schedule, teacher_id)
        )
    conn.commit()
    conn.close()

def update_student(student_id, name, surname, class_name, restrictions='', priorities='', manual_lessons='', teacher_blocks=''):
    """
    Öğrenci bilgilerini günceller
    Updates student information
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE students SET name = ?, surname = ?, class = ?, restrictions = ?, priorities = ?, manual_lessons = ?, teacher_blocks = ? WHERE id = ?',
        (name, surname, class_name, restrictions, priorities, manual_lessons, teacher_blocks, student_id)
    )
    conn.commit()
    conn.close()

def delete_teacher(teacher_id):
    """
    Öğretmeni siler
    Deletes teacher
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM teachers WHERE id = ?', (teacher_id,))
    conn.commit()
    conn.close()

def delete_student(student_id):
    """
    Öğrenciyi siler
    Deletes student
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()

def save_schedule(name, schedule_data, teachers_snapshot, students_snapshot):
    """
    Ders programını kaydeder
    Saves course schedule
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO saved_schedules (name, schedule_data, teachers_snapshot, students_snapshot) VALUES (?, ?, ?, ?)',
        (name, schedule_data, teachers_snapshot, students_snapshot)
    )
    conn.commit()
    schedule_id = cursor.lastrowid
    conn.close()
    return schedule_id

def get_saved_schedules():
    """
    Kaydedilmiş tüm programları getirir
    Retrieves all saved schedules
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, created_at FROM saved_schedules ORDER BY created_at DESC')
    schedules = cursor.fetchall()
    conn.close()
    return schedules

def get_saved_schedule_by_id(schedule_id):
    """
    ID'ye göre kaydedilmiş programı getirir
    Retrieves saved schedule by ID
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM saved_schedules WHERE id = ?', (schedule_id,))
    schedule = cursor.fetchone()
    conn.close()
    return schedule

def delete_saved_schedule(schedule_id):
    """
    Kaydedilmiş programı siler
    Deletes saved schedule
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM saved_schedules WHERE id = ?', (schedule_id,))
    conn.commit()
    conn.close()
