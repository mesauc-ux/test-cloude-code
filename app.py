from flask import Flask, render_template_string, request, jsonify, send_file, make_response
from datetime import datetime
import io
import sqlite3
import json
import random
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from weasyprint import HTML

app = Flask(__name__)

# SQLite veritabanı bağlantısı
def get_db():
    conn = sqlite3.connect('/home/mesauc/mysite/ders_programi.db')
    conn.row_factory = sqlite3.Row
    return conn

# Veritabanı tablolarını oluştur
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            branch TEXT NOT NULL,
            schedule TEXT NOT NULL
        )
    ''')

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
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN priorities TEXT')
    except:
        pass

    try:
        cursor.execute('ALTER TABLE students ADD COLUMN manual_lessons TEXT')
    except:
        pass

    try:
        cursor.execute('ALTER TABLE students ADD COLUMN teacher_blocks TEXT')
    except:
        pass  # Kolon zaten varsa hata verme

    # 🆕 ÖĞRETMEN TABLOSUNA BLOKLAMA KOLONU EKLE
    try:
        cursor.execute('ALTER TABLE teachers ADD COLUMN blocked_slots TEXT')
    except:
        pass  # Kolon zaten varsa hata verme

    # 🆕 GEÇMİŞ PROGRAMLAR TABLOSU
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

# Uygulama başlatıldığında veritabanını oluştur
init_db()

schedule_data = None

# HTML_TEMPLATE burada çok uzun olduğu için dosyanın geri kalanına bakın...
# (Kod çok uzun olduğu için devam ediyor)
