from flask import Flask, render_template_string, request, jsonify, send_file, make_response
from datetime import datetime
import io
import sqlite3
import json
import random
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from weasyprint import HTML

# 🆕 WHATSAPP İÇİN TWILIO IMPORT
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️ Twilio kütüphanesi bulunamadı. WhatsApp özellikleri çalışmayacak.")
    print("Yüklemek için: pip install twilio")

app = Flask(__name__)

# 🆕 TWILIO WHATSAPP AYARLARI
# Not: Bu bilgileri .env dosyasından veya environment variable'dan çekmelisiniz
TWILIO_ACCOUNT_SID = 'your_account_sid_here'  # Twilio hesabınızdan alın
TWILIO_AUTH_TOKEN = 'your_auth_token_here'   # Twilio hesabınızdan alın
TWILIO_WHATSAPP_FROM = 'whatsapp:+14155238886'  # Twilio WhatsApp numarası (sandbox için)

# Twilio client'ı başlat
if TWILIO_AVAILABLE:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except:
        twilio_client = None
        print("⚠️ Twilio client başlatılamadı. Lütfen credentials'ları kontrol edin.")
else:
    twilio_client = None

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
        pass

    try:
        cursor.execute('ALTER TABLE teachers ADD COLUMN blocked_slots TEXT')
    except:
        pass

    # 🆕 WHATSAPP NUMARALARI İÇİN YENİ KOLONLAR
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN whatsapp_number TEXT')
    except:
        pass

    try:
        cursor.execute('ALTER TABLE students ADD COLUMN whatsapp_enabled INTEGER DEFAULT 1')
    except:
        pass

    try:
        cursor.execute('ALTER TABLE teachers ADD COLUMN whatsapp_number TEXT')
    except:
        pass

    try:
        cursor.execute('ALTER TABLE teachers ADD COLUMN whatsapp_enabled INTEGER DEFAULT 1')
    except:
        pass

    # GEÇMİŞ PROGRAMLAR TABLOSU
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

    # 🆕 WHATSAPP BİLDİRİM GEÇMİŞİ TABLOSU
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS whatsapp_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_type TEXT NOT NULL,
            recipient_id INTEGER NOT NULL,
            recipient_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Uygulama başlatıldığında veritabanını oluştur
init_db()

schedule_data = None

# 🆕 WHATSAPP FONKSİYONLARI
def send_whatsapp_message(to_number, message):
    """
    WhatsApp mesajı gönder
    to_number: +90XXXXXXXXXX formatında
    message: Gönderilecek mesaj
    """
    if not TWILIO_AVAILABLE or not twilio_client:
        return {
            'success': False,
            'error': 'Twilio kütüphanesi kurulu değil veya client başlatılamadı'
        }

    try:
        # Numara formatını kontrol et
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'

        message_obj = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=message,
            to=to_number
        )

        return {
            'success': True,
            'sid': message_obj.sid,
            'status': message_obj.status
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def log_whatsapp_notification(recipient_type, recipient_id, recipient_name, phone_number, message, status, error_message=None):
    """WhatsApp bildirimini veritabanına kaydet"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO whatsapp_notifications
        (recipient_type, recipient_id, recipient_name, phone_number, message, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (recipient_type, recipient_id, recipient_name, phone_number, message, status, error_message))

    conn.commit()
    conn.close()

def send_schedule_notification_to_student(student, week_num=None):
    """Öğrenciye program bildirimini gönder"""
    if not student.get('whatsapp_number') or not student.get('whatsapp_enabled'):
        return {'success': False, 'error': 'WhatsApp numarası yok veya bildirim kapalı'}

    if not schedule_data:
        return {'success': False, 'error': 'Program bulunamadı'}

    student_name = f"{student['name']} {student['surname']}"

    # Öğrencinin derslerini topla
    lessons_summary = []
    for w_num, week in enumerate(schedule_data['weeks']):
        if week_num and w_num + 1 != week_num:
            continue

        week_lessons = [l for l in week if l['student_name'] == student_name]
        if week_lessons:
            lessons_summary.append(f"📅 Hafta {w_num + 1}: {len(week_lessons)} ders")

    if not lessons_summary:
        return {'success': False, 'error': 'Bu öğrenci için ders bulunamadı'}

    message = f"""🎓 Ders Programı Bildirimi

Sayın {student_name},

Ders programınız oluşturulmuştur:

{chr(10).join(lessons_summary)}

Detaylı programı web üzerinden görüntüleyebilirsiniz.

İyi çalışmalar dileriz! 📚"""

    result = send_whatsapp_message(student['whatsapp_number'], message)

    # Loglama
    log_whatsapp_notification(
        'student',
        student['id'],
        student_name,
        student['whatsapp_number'],
        message,
        'sent' if result['success'] else 'failed',
        result.get('error')
    )

    return result

def send_schedule_notification_to_teacher(teacher):
    """Öğretmene program bildirimini gönder"""
    if not teacher.get('whatsapp_number') or not teacher.get('whatsapp_enabled'):
        return {'success': False, 'error': 'WhatsApp numarası yok veya bildirim kapalı'}

    if not schedule_data:
        return {'success': False, 'error': 'Program bulunamadı'}

    teacher_name = f"{teacher['name']} {teacher['surname']}"

    # Öğretmenin derslerini topla
    lessons_summary = []
    for w_num, week in enumerate(schedule_data['weeks']):
        week_lessons = [l for l in week if l['teacher_name'] == teacher_name]
        if week_lessons:
            lessons_summary.append(f"📅 Hafta {w_num + 1}: {len(week_lessons)} ders")

    if not lessons_summary:
        return {'success': False, 'error': 'Bu öğretmen için ders bulunamadı'}

    message = f"""👨‍🏫 Ders Programı Bildirimi

Sayın {teacher_name},

{teacher['branch']} dersi programınız oluşturulmuştur:

{chr(10).join(lessons_summary)}

Detaylı programı web üzerinden görüntüleyebilirsiniz.

İyi dersler dileriz! 📚"""

    result = send_whatsapp_message(teacher['whatsapp_number'], message)

    # Loglama
    log_whatsapp_notification(
        'teacher',
        teacher['id'],
        teacher_name,
        teacher['whatsapp_number'],
        message,
        'sent' if result['success'] else 'failed',
        result.get('error')
    )

    return result

# 🆕 WHATSAPP ROUTE'LARI
@app.route('/send_test_whatsapp', methods=['POST'])
def send_test_whatsapp():
    """Test WhatsApp mesajı gönder"""
    data = request.json
    phone_number = data.get('phone_number')
    recipient_name = data.get('name', 'Değerli Kullanıcı')

    if not phone_number:
        return jsonify({'error': 'Telefon numarası gerekli!'}), 400

    message = f"""🎓 Test Bildirimi

Merhaba {recipient_name},

Bu bir test mesajıdır. WhatsApp bildirim sisteminiz başarıyla çalışıyor! ✅

Ders programı sistemi tarafından gönderilmiştir."""

    result = send_whatsapp_message(phone_number, message)

    if result['success']:
        return jsonify({
            'message': 'Test mesajı başarıyla gönderildi!',
            'sid': result.get('sid')
        })
    else:
        return jsonify({'error': result.get('error')}), 500

@app.route('/send_schedule_notifications', methods=['POST'])
def send_schedule_notifications():
    """Tüm öğrenci ve öğretmenlere program bildirimini gönder"""
    if not schedule_data:
        return jsonify({'error': 'Önce program oluşturun!'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Öğrencileri çek
    cursor.execute('SELECT * FROM students WHERE whatsapp_enabled = 1 AND whatsapp_number IS NOT NULL')
    students = []
    for row in cursor.fetchall():
        students.append({
            'id': row['id'],
            'name': row['name'],
            'surname': row['surname'],
            'whatsapp_number': row['whatsapp_number'],
            'whatsapp_enabled': row['whatsapp_enabled']
        })

    # Öğretmenleri çek
    cursor.execute('SELECT * FROM teachers WHERE whatsapp_enabled = 1 AND whatsapp_number IS NOT NULL')
    teachers = []
    for row in cursor.fetchall():
        teachers.append({
            'id': row['id'],
            'name': row['name'],
            'surname': row['surname'],
            'branch': row['branch'],
            'whatsapp_number': row['whatsapp_number'],
            'whatsapp_enabled': row['whatsapp_enabled']
        })

    conn.close()

    results = {
        'students_sent': 0,
        'students_failed': 0,
        'teachers_sent': 0,
        'teachers_failed': 0,
        'errors': []
    }

    # Öğrencilere gönder
    for student in students:
        result = send_schedule_notification_to_student(student)
        if result['success']:
            results['students_sent'] += 1
        else:
            results['students_failed'] += 1
            results['errors'].append(f"{student['name']} {student['surname']}: {result.get('error')}")

    # Öğretmenlere gönder
    for teacher in teachers:
        result = send_schedule_notification_to_teacher(teacher)
        if result['success']:
            results['teachers_sent'] += 1
        else:
            results['teachers_failed'] += 1
            results['errors'].append(f"{teacher['name']} {teacher['surname']}: {result.get('error')}")

    return jsonify({
        'message': 'Bildirimler gönderildi!',
        'summary': results
    })

@app.route('/get_whatsapp_history')
def get_whatsapp_history():
    """WhatsApp bildirim geçmişini getir"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM whatsapp_notifications
        ORDER BY sent_at DESC
        LIMIT 100
    ''')

    history = []
    for row in cursor.fetchall():
        history.append({
            'id': row['id'],
            'recipient_type': row['recipient_type'],
            'recipient_name': row['recipient_name'],
            'phone_number': row['phone_number'],
            'message': row['message'],
            'status': row['status'],
            'sent_at': row['sent_at'],
            'error_message': row['error_message']
        })

    conn.close()
    return jsonify({'history': history})

# MEVCUT KODUN DEVAMI (hiçbir değişiklik yapılmadı)
# ... (önceki tüm route'lar ve fonksiyonlar aynen kalacak)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Özel Ders Programı Yönetim Sistemi</title>
    <style>
        /* MEVCUT STILLER AYNEN KALACAK */
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        @media screen {
            /* ... tüm mevcut stil kodları ... */
        }

        /* 🆕 WHATSAPP STILLER */
        .whatsapp-input {
            position: relative;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .whatsapp-input input {
            flex: 1;
            padding-left: 45px !important;
        }

        .whatsapp-icon {
            position: absolute;
            left: 15px;
            font-size: 1.2em;
            color: #25D366;
        }

        .whatsapp-toggle {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            user-select: none;
        }

        .whatsapp-toggle input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }

        .whatsapp-btn {
            background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .whatsapp-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
        }

        .whatsapp-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .whatsapp-status.enabled {
            background: #dcfce7;
            color: #166534;
        }

        .whatsapp-status.disabled {
            background: #fee2e2;
            color: #991b1b;
        }
    </style>

    <!-- PDF Export Kütüphaneleri -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.5.3/jspdf.min.js"></script>

    <!-- Font Awesome İkonlar -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <!-- Chart.js Grafikler -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>

    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Özel Ders Programı Yönetim Sistemi</h1>
            <p>Modern ve Akıllı Ders Programı Oluşturma Platformu</p>

            <!-- Dark Mode Toggle -->
            <div style="position: absolute; top: 20px; right: 30px;">
                <button id="darkModeToggle" onclick="toggleDarkMode()" style="background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.3); color: white; padding: 12px 20px; border-radius: 50px; cursor: pointer; font-weight: 700; font-size: 1em; transition: all 0.3s; backdrop-filter: blur(10px); display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-moon" id="darkModeIcon"></i>
                    <span id="darkModeText">Koyu Tema</span>
                </button>
            </div>
        </div>
        <div class="main-content">
            <div class="success-message" id="successMessage"></div>
            <div class="error-message" id="errorMessage"></div>
            <div class="button-grid">
                <button class="main-btn" onclick="openTeacherModal()">
                    <i class="fas fa-chalkboard-teacher"></i> Öğretmen Ekle
                </button>
                <button class="main-btn" onclick="openStudentModal()">
                    <i class="fas fa-user-graduate"></i> Öğrenci Ekle
                </button>
                <button class="main-btn" onclick="generateSchedule()">
                    <i class="fas fa-calendar-alt"></i> Yeni Program Oluştur
                </button>
                <button class="main-btn" onclick="openSaveScheduleModal()" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <i class="fas fa-save"></i> Programı Kaydet
                </button>

                <!-- 🆕 WHATSAPP BUTON -->
                <button class="main-btn whatsapp-btn" onclick="openWhatsAppPanel()">
                    <i class="fab fa-whatsapp"></i> WhatsApp Bildirimleri
                </button>

                <button class="main-btn" onclick="openSavedSchedulesModal()" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                    <i class="fas fa-history"></i> Geçmiş Programlar
                </button>
                <button class="main-btn" onclick="exportToExcel()">
                    <i class="fas fa-file-excel"></i> Excel İndir
                </button>
                <button class="main-btn" onclick="exportToHTML()">
                    <i class="fas fa-file-code"></i> HTML İndir
                </button>
                <button class="main-btn" onclick="openConflictDashboard()" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
                    <i class="fas fa-exclamation-triangle"></i> Çakışma Kontrolü
                    <span id="conflictBadge" style="display: none; position: absolute; top: 10px; right: 10px; background: #fbbf24; color: #000; padding: 4px 8px; border-radius: 50%; font-size: 0.8em; font-weight: bold;">0</span>
                </button>
            </div>

            <!-- MEVCUT İÇERİK AYNEN KALACAK -->
            <!-- ... -->

        </div>
    </div>

    <!-- 🆕 WHATSAPP PANEL MODAL -->
    <div class="modal" id="whatsappPanelModal">
        <div class="modal-content" style="max-width: 900px;">
            <span class="close-btn" onclick="closeWhatsAppPanel()">&times;</span>
            <h2 style="color: #25D366; display: flex; align-items: center; gap: 10px;">
                <i class="fab fa-whatsapp"></i> WhatsApp Bildirim Paneli
            </h2>

            <div style="background: linear-gradient(135deg, #dcfce7 0%, #f0fdf4 100%); padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #25D366;">
                <h3 style="margin-bottom: 10px; color: #166534;">ℹ️ Bilgilendirme</h3>
                <p style="color: #166534; line-height: 1.6;">
                    WhatsApp bildirimleri için Twilio WhatsApp API kullanılmaktadır. Bildirimlerin gönderilmesi için öğrenci ve öğretmenlerin WhatsApp numaralarını eklemeniz gerekmektedir.
                </p>
            </div>

            <!-- Test Mesajı Gönder -->
            <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #25D366;">
                <h3 style="margin-bottom: 15px; color: #25D366;">📱 Test Mesajı Gönder</h3>
                <div style="display: grid; gap: 15px;">
                    <div class="whatsapp-input">
                        <i class="whatsapp-icon fab fa-whatsapp"></i>
                        <input type="text" id="testWhatsAppNumber" placeholder="+905XXXXXXXXX" style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 10px;">
                    </div>
                    <input type="text" id="testWhatsAppName" placeholder="İsim" style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 10px;">
                    <button onclick="sendTestWhatsApp()" class="whatsapp-btn" style="width: 100%;">
                        <i class="fas fa-paper-plane"></i> Test Mesajı Gönder
                    </button>
                </div>
            </div>

            <!-- Toplu Bildirim Gönder -->
            <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #25D366;">
                <h3 style="margin-bottom: 15px; color: #25D366;">📢 Toplu Bildirim Gönder</h3>
                <p style="color: #666; margin-bottom: 15px;">
                    Mevcut programa göre tüm öğrenci ve öğretmenlere bildirim gönderir.
                </p>
                <button onclick="sendBulkNotifications()" class="whatsapp-btn" style="width: 100%;">
                    <i class="fas fa-users"></i> Herkese Bildirim Gönder
                </button>
            </div>

            <!-- Bildirim Geçmişi -->
            <div style="background: white; padding: 20px; border-radius: 12px; border: 2px solid #25D366;">
                <h3 style="margin-bottom: 15px; color: #25D366;">📋 Bildirim Geçmişi</h3>
                <div id="whatsappHistory" style="max-height: 300px; overflow-y: auto;">
                    <p style="text-align: center; color: #999; padding: 20px;">Yükleniyor...</p>
                </div>
                <button onclick="loadWhatsAppHistory()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 8px; margin-top: 10px; cursor: pointer; width: 100%;">
                    <i class="fas fa-sync-alt"></i> Geçmişi Yenile
                </button>
            </div>
        </div>
    </div>

    <script>
        // MEVCUT TÜM JAVASCRIPT KODLARI AYNEN KALACAK
        // ...

        // 🆕 WHATSAPP FONKSİYONLARI

        function openWhatsAppPanel() {
            document.getElementById('whatsappPanelModal').style.display = 'block';
            loadWhatsAppHistory();
        }

        function closeWhatsAppPanel() {
            document.getElementById('whatsappPanelModal').style.display = 'none';
        }

        async function sendTestWhatsApp() {
            const number = document.getElementById('testWhatsAppNumber').value.trim();
            const name = document.getElementById('testWhatsAppName').value.trim() || 'Değerli Kullanıcı';

            if (!number) {
                showError('Lütfen telefon numarası girin!');
                return;
            }

            if (!number.startsWith('+')) {
                showError('Telefon numarası + ile başlamalıdır! (Örn: +905XXXXXXXXX)');
                return;
            }

            try {
                const response = await fetch('/send_test_whatsapp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone_number: number, name: name })
                });

                const result = await response.json();

                if (response.ok) {
                    showSuccess('Test mesajı başarıyla gönderildi! WhatsApp\'tan kontrol edin.');
                    document.getElementById('testWhatsAppNumber').value = '';
                    document.getElementById('testWhatsAppName').value = '';
                    loadWhatsAppHistory();
                } else {
                    showError('Hata: ' + result.error);
                }
            } catch (error) {
                showError('Mesaj gönderilirken hata oluştu: ' + error);
            }
        }

        async function sendBulkNotifications() {
            if (!confirm('Tüm öğrenci ve öğretmenlere WhatsApp bildirimi gönderilecek. Onaylıyor musunuz?')) {
                return;
            }

            if (!globalScheduleData) {
                showError('Önce program oluşturun!');
                return;
            }

            try {
                showSuccess('Bildirimler gönderiliyor, lütfen bekleyin...');

                const response = await fetch('/send_schedule_notifications', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const result = await response.json();

                if (response.ok) {
                    const summary = result.summary;
                    let message = `✅ Bildirimler gönderildi!\n\n`;
                    message += `Öğrenciler: ${summary.students_sent} başarılı, ${summary.students_failed} başarısız\n`;
                    message += `Öğretmenler: ${summary.teachers_sent} başarılı, ${summary.teachers_failed} başarısız`;

                    if (summary.errors.length > 0) {
                        message += `\n\nHatalar:\n${summary.errors.slice(0, 3).join('\n')}`;
                    }

                    alert(message);
                    loadWhatsAppHistory();
                } else {
                    showError('Hata: ' + result.error);
                }
            } catch (error) {
                showError('Bildirim gönderilirken hata oluştu: ' + error);
            }
        }

        async function loadWhatsAppHistory() {
            const container = document.getElementById('whatsappHistory');
            container.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">Yükleniyor...</p>';

            try {
                const response = await fetch('/get_whatsapp_history');
                const data = await response.json();

                if (data.history.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">Henüz bildirim gönderilmemiş.</p>';
                    return;
                }

                let html = '';
                data.history.forEach(item => {
                    const statusClass = item.status === 'sent' ? 'enabled' : 'disabled';
                    const statusText = item.status === 'sent' ? '✅ Gönderildi' : '❌ Başarısız';
                    const icon = item.recipient_type === 'student' ? '👨‍🎓' : '👨‍🏫';

                    html += `
                        <div style="border-left: 4px solid ${item.status === 'sent' ? '#25D366' : '#ef4444'}; padding: 15px; margin-bottom: 10px; background: #f9fafb; border-radius: 8px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <strong>${icon} ${item.recipient_name}</strong>
                                <span class="whatsapp-status ${statusClass}">${statusText}</span>
                            </div>
                            <div style="font-size: 0.9em; color: #666; margin-bottom: 5px;">
                                📱 ${item.phone_number}
                            </div>
                            <div style="font-size: 0.85em; color: #999;">
                                🕐 ${new Date(item.sent_at).toLocaleString('tr-TR')}
                            </div>
                            ${item.error_message ? `<div style="color: #ef4444; font-size: 0.85em; margin-top: 5px;">⚠️ ${item.error_message}</div>` : ''}
                        </div>
                    `;
                });

                container.innerHTML = html;
            } catch (error) {
                container.innerHTML = '<p style="text-align: center; color: #ef4444; padding: 20px;">Geçmiş yüklenirken hata oluştu!</p>';
            }
        }

        // MEVCUT KODUN DEVAMI...
        window.onload = function() {
            loadTeachers();
            loadStudents();
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# MEVCUT TÜM ROUTE'LAR AYNEN KALACAK
# (Kodun geri kalanı öncekiyle aynı)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
