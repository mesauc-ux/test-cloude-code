"""
Ders Programı Uygulaması - Route Handler Modülü
Route handlers module for the Course Schedule Application
"""
from flask import Blueprint, render_template, request, jsonify, send_file, make_response
from datetime import datetime
import io
import json
import random
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from weasyprint import HTML

import database as db

# Blueprint oluştur
main_bp = Blueprint('main', __name__)

# Global değişken - ders programı verisi
schedule_data = None

@main_bp.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

# ============= ÖĞRETMEN İŞLEMLERİ (TEACHER OPERATIONS) =============

@main_bp.route('/teachers', methods=['GET'])
def get_teachers():
    """Tüm öğretmenleri getir"""
    teachers = db.get_teachers()
    return jsonify([dict(teacher) for teacher in teachers])

@main_bp.route('/teachers', methods=['POST'])
def add_teacher():
    """Yeni öğretmen ekle"""
    data = request.get_json()
    teacher_id = db.add_teacher(
        data['name'],
        data['surname'],
        data['branch'],
        data.get('schedule', '{}')
    )
    return jsonify({'success': True, 'id': teacher_id})

@main_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    """Öğretmen bilgilerini güncelle"""
    data = request.get_json()
    db.update_teacher(
        teacher_id,
        data['name'],
        data['surname'],
        data['branch'],
        data.get('schedule', '{}'),
        data.get('blocked_slots')
    )
    return jsonify({'success': True})

@main_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Öğretmeni sil"""
    db.delete_teacher(teacher_id)
    return jsonify({'success': True})

# ============= ÖĞRENCİ İŞLEMLERİ (STUDENT OPERATIONS) =============

@main_bp.route('/students', methods=['GET'])
def get_students():
    """Tüm öğrencileri getir"""
    students = db.get_students()
    return jsonify([dict(student) for student in students])

@main_bp.route('/students', methods=['POST'])
def add_student():
    """Yeni öğrenci ekle"""
    data = request.get_json()
    student_id = db.add_student(
        data['name'],
        data['surname'],
        data['class'],
        data.get('restrictions', ''),
        data.get('priorities', ''),
        data.get('manual_lessons', '')
    )
    return jsonify({'success': True, 'id': student_id})

@main_bp.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Öğrenci bilgilerini güncelle"""
    data = request.get_json()
    db.update_student(
        student_id,
        data['name'],
        data['surname'],
        data['class'],
        data.get('restrictions', ''),
        data.get('priorities', ''),
        data.get('manual_lessons', ''),
        data.get('teacher_blocks', '')
    )
    return jsonify({'success': True})

@main_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Öğrenciyi sil"""
    db.delete_student(student_id)
    return jsonify({'success': True})

# ============= DERS PROGRAMI İŞLEMLERİ (SCHEDULE OPERATIONS) =============

@main_bp.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    """
    Ders programı oluştur

    NOT: Bu fonksiyon orijinal app.py'den alınacak
    scheduling algoritması buraya eklenecek
    """
    global schedule_data

    # TODO: Orijinal scheduling algoritmasını buraya ekle
    # Bu sadece bir placeholder
    data = request.get_json()

    # Örnek yanıt - gerçek algoritma ile değiştirilmeli
    schedule_data = {
        'status': 'success',
        'message': 'Program oluşturuldu (placeholder)',
        'schedule': {}
    }

    return jsonify(schedule_data)

@main_bp.route('/update_schedule', methods=['POST'])
def update_schedule():
    """Ders programını güncelle (drag-drop için)"""
    global schedule_data

    data = request.get_json()
    # TODO: Schedule güncelleme mantığını ekle

    return jsonify({'success': True})

# ============= KAYDETME İŞLEMLERİ (SAVE OPERATIONS) =============

@main_bp.route('/save_schedule', methods=['POST'])
def save_schedule():
    """Ders programını veritabanına kaydet"""
    global schedule_data

    data = request.get_json()
    schedule_name = data.get('name', f'Program_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

    # Öğretmen ve öğrenci snapshot'larını al
    teachers = db.get_teachers()
    students = db.get_students()

    teachers_snapshot = json.dumps([dict(t) for t in teachers])
    students_snapshot = json.dumps([dict(s) for s in students])

    schedule_id = db.save_schedule(
        schedule_name,
        json.dumps(schedule_data),
        teachers_snapshot,
        students_snapshot
    )

    return jsonify({'success': True, 'id': schedule_id})

@main_bp.route('/saved_schedules', methods=['GET'])
def get_saved_schedules():
    """Kaydedilmiş tüm programları getir"""
    schedules = db.get_saved_schedules()
    return jsonify([dict(s) for s in schedules])

@main_bp.route('/saved_schedules/<int:schedule_id>', methods=['GET'])
def load_saved_schedule(schedule_id):
    """Kaydedilmiş programı yükle"""
    global schedule_data

    schedule = db.get_saved_schedule_by_id(schedule_id)
    if schedule:
        schedule_data = json.loads(schedule['schedule_data'])
        return jsonify({
            'success': True,
            'schedule': schedule_data,
            'teachers': json.loads(schedule['teachers_snapshot']) if schedule['teachers_snapshot'] else [],
            'students': json.loads(schedule['students_snapshot']) if schedule['students_snapshot'] else []
        })
    return jsonify({'success': False, 'message': 'Program bulunamadı'})

@main_bp.route('/saved_schedules/<int:schedule_id>', methods=['DELETE'])
def delete_saved_schedule(schedule_id):
    """Kaydedilmiş programı sil"""
    db.delete_saved_schedule(schedule_id)
    return jsonify({'success': True})

# ============= EXPORT İŞLEMLERİ (EXPORT OPERATIONS) =============

@main_bp.route('/export/excel', methods=['POST'])
def export_excel():
    """
    Ders programını Excel olarak indir

    NOT: Orijinal export_excel fonksiyonu buraya taşınacak
    """
    # TODO: Orijinal Excel export mantığını ekle

    # Placeholder
    wb = Workbook()
    ws = wb.active
    ws.title = "Ders Programı"
    ws['A1'] = "Ders Programı - Placeholder"

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'ders_programi_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@main_bp.route('/export/pdf', methods=['POST'])
def export_pdf():
    """
    Ders programını PDF olarak indir

    NOT: Orijinal export_pdf fonksiyonu buraya taşınacak
    """
    # TODO: Orijinal PDF export mantığını ekle

    html_content = """
    <html>
    <body>
        <h1>Ders Programı</h1>
        <p>Placeholder PDF içeriği</p>
    </body>
    </html>
    """

    pdf = HTML(string=html_content).write_pdf()

    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'ders_programi_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

@main_bp.route('/export/html', methods=['POST'])
def export_html():
    """Ders programını HTML olarak indir"""
    # TODO: Orijinal HTML export mantığını ekle

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Ders Programı</title>
    </head>
    <body>
        <h1>Ders Programı</h1>
        <p>Placeholder HTML içeriği</p>
    </body>
    </html>
    """

    return send_file(
        io.BytesIO(html_content.encode('utf-8')),
        mimetype='text/html',
        as_attachment=True,
        download_name=f'ders_programi_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    )
