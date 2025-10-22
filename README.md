# Ders Programı Yönetim Sistemi
# Course Schedule Management System

## 📋 Genel Bakış / Overview

Bu proje, öğretmen ve öğrenci ders programlarını yönetmek için geliştirilmiş modüler bir Flask uygulamasıdır.

This project is a modular Flask application developed for managing teacher and student course schedules.

## 🏗️ Modüler Yapı / Modular Structure

Uygulama, bakım ve geliştirmeyi kolaylaştırmak için modüler bir yapıya sahiptir:

```
test-cloude-code/
├── app.py                  # Ana uygulama dosyası / Main application file
├── config.py               # Yapılandırma ayarları / Configuration settings
├── database.py             # Veritabanı işlemleri / Database operations
├── routes.py               # Route handler'lar / Route handlers
├── requirements.txt        # Python bağımlılıkları / Python dependencies
├── templates/              # HTML şablonları / HTML templates
│   └── index.html
├── static/                 # Statik dosyalar / Static files
│   ├── css/
│   │   └── style.css      # CSS stilleri / CSS styles
│   └── js/
│       └── main.js        # JavaScript kodu / JavaScript code
└── README.md              # Bu dosya / This file
```

### Dosya Açıklamaları / File Descriptions

#### `app.py` - Ana Uygulama
- Flask uygulamasını başlatır
- Yapılandırmayı yükler
- Blueprint'leri kaydeder
- Veritabanını initialize eder

#### `config.py` - Yapılandırma
- Uygulama ayarları (development, production)
- Veritabanı yolu yapılandırması
- Ortam değişkenleri

#### `database.py` - Veritabanı Modülü
Tüm veritabanı işlemlerini içerir:
- `get_db()` - Veritabanı bağlantısı
- `init_db()` - Tablo oluşturma
- `get_teachers()`, `add_teacher()`, `update_teacher()`, `delete_teacher()`
- `get_students()`, `add_student()`, `update_student()`, `delete_student()`
- `save_schedule()`, `get_saved_schedules()`, vb.

#### `routes.py` - Route Handler'lar
Tüm HTTP endpoint'lerini içerir:
- `/` - Ana sayfa
- `/teachers` - Öğretmen CRUD işlemleri
- `/students` - Öğrenci CRUD işlemleri
- `/generate_schedule` - Program oluşturma
- `/save_schedule` - Program kaydetme
- `/export/*` - Export işlemleri (Excel, PDF, HTML)

#### `templates/index.html` - Ana Şablon
- Uygulamanın HTML yapısı
- Tab-based kullanıcı arayüzü
- Modal yapıları

#### `static/css/style.css` - Stiller
- Responsive tasarım
- Dark mode desteği
- Modern UI bileşenleri

#### `static/js/main.js` - İstemci Tarafı JavaScript
- AJAX istekleri
- Dynamic UI güncellemeleri
- Form yönetimi
- Dark mode toggle

## 🚀 Kurulum / Installation

### 1. Bağımlılıkları Yükle / Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Çalıştır / Run Application

**Geliştirme ortamı / Development:**
```bash
python app.py
```

**Production ortamı / Production (PythonAnywhere):**
```python
# WSGI configuration dosyasında / In WSGI config file
from app import app as application
```

### 3. Tarayıcıda Aç / Open in Browser

```
http://localhost:5000
```

## 📝 Orijinal Koddan Migration / Migration from Original Code

### ⚠️ ÖNEMLİ NOTLAR / IMPORTANT NOTES

Modülerleştirme sırasında orijinal `app.py` dosyasındaki bazı özellikler placeholder olarak bırakılmıştır. Aşağıdaki özellikler orijinal koddan taşınmalıdır:

During modularization, some features from the original `app.py` were left as placeholders. The following features need to be migrated from the original code:

### 1. HTML Template İçeriği / HTML Template Content

**Konum / Location:** `templates/index.html`

Orijinal `app.py` dosyasındaki `HTML_TEMPLATE` değişkenindeki içerik, `templates/index.html` dosyasına eklenmelidir. Özellikle:
- Detaylı form yapıları
- Ders programı görüntüleme tablosu
- Drag-and-drop özellikleri
- Modal içerikleri

### 2. Ders Programı Oluşturma Algoritması / Schedule Generation Algorithm

**Konum / Location:** `routes.py` → `generate_schedule()` fonksiyonu

```python
@main_bp.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    # TODO: Orijinal scheduling algoritmasını buraya ekle
    # Şu özellikleri içermeli:
    # - 4 haftalık program oluşturma
    # - Çakışma kontrolü
    # - Öğretmen kısıtlamaları
    # - Öğrenci öncelikleri
    pass
```

### 3. Export Fonksiyonları / Export Functions

**Konum / Location:** `routes.py`

#### Excel Export
```python
@main_bp.route('/export/excel', methods=['POST'])
def export_excel():
    # TODO: Orijinal Excel export mantığını ekle
    # - Haftalık sayfalar
    # - Stil formatlaması
    # - Öğretmen/öğrenci bazlı görünümler
    pass
```

#### PDF Export
```python
@main_bp.route('/export/pdf', methods=['POST'])
def export_pdf():
    # TODO: Orijinal PDF export mantığını ekle
    # - WeasyPrint ile HTML to PDF
    # - Özel stil şablonu
    pass
```

### 4. Gelişmiş Özellikler / Advanced Features

Orijinal kodda bulunan ancak henüz eklenmemiş özellikler:

- **Öğretmen Slot Bloklama:** Öğretmenlerin belirli saatleri bloke etme özelliği
- **Öğrenci Kısıtlamaları:** Öğrencilerin uygun olmayan saatler
- **Manuel Ders Atama:** Drag-and-drop ile manuel düzenleme
- **Çakışma Tespiti:** Gerçek zamanlı çakışma uyarıları
- **Program Karşılaştırma:** Farklı programları karşılaştırma

## 🔧 Yapılandırma / Configuration

### Veritabanı Yolu / Database Path

`config.py` dosyasında otomatik olarak algılanır:
- **PythonAnywhere:** `/home/mesauc/mysite/ders_programi.db`
- **Local:** `./ders_programi.db`

Manuel ayar için:
```python
# config.py
DATABASE_PATH = '/your/custom/path/ders_programi.db'
```

### Debug Modu / Debug Mode

```bash
# Geliştirme / Development
export FLASK_ENV=development

# Production
export FLASK_ENV=production
```

## 📦 Bağımlılıklar / Dependencies

- **Flask 3.0.0** - Web framework
- **openpyxl 3.1.2** - Excel dosya işlemleri
- **weasyprint 60.1** - PDF oluşturma
- **Werkzeug 3.0.1** - WSGI utilities

## 🎯 Sonraki Adımlar / Next Steps

1. **Orijinal app.py'yi Gözden Geçir:** `app.py.backup` dosyasındaki orijinal kodu incele
2. **Eksik Özellikleri Ekle:** Yukarıda belirtilen TODO'ları tamamla
3. **Test Et:** Tüm özelliklerin çalıştığından emin ol
4. **PythonAnywhere'e Deploy:** WSGI yapılandırmasını güncelle

## 📚 Kullanım Kılavuzu / User Guide

### Öğretmen Ekleme / Adding Teacher
1. "Öğretmenler" sekmesine git
2. "+ Yeni Öğretmen Ekle" butonuna tıkla
3. Formu doldur (Ad, Soyad, Branş)
4. "Ekle" butonuna tıkla

### Öğrenci Ekleme / Adding Student
1. "Öğrenciler" sekmesine git
2. "+ Yeni Öğrenci Ekle" butonuna tıkla
3. Formu doldur (Ad, Soyad, Sınıf)
4. "Ekle" butonuna tıkla

### Program Oluşturma / Creating Schedule
1. "Ders Programı" sekmesine git
2. "Program Oluştur" butonuna tıkla
3. Algoritma çalışacak (tamamlandığında TODO eklenecek)
4. Program görüntülenecek

### Program Kaydetme / Saving Schedule
1. Program oluşturduktan sonra
2. "Programı Kaydet" butonuna tıkla
3. İsim gir
4. "Kayıtlı Programlar" sekmesinden erişebilirsin

## 🎨 Dark Mode

Karanlık mod desteği mevcuttur:
- Sağ üstteki buton ile aktif/pasif
- Tercihiniz tarayıcıda saklanır

## 🐛 Hata Ayıklama / Debugging

### Veritabanı sorunları:
```python
# database.py'de bağlantıyı test et
conn = get_db()
print(conn)
```

### Route sorunları:
```bash
# Flask debug modunu aktif et
export FLASK_ENV=development
python app.py
```

## 📄 Lisans / License

Bu proje mesauc tarafından geliştirilmiştir.

## 🤝 Katkıda Bulunma / Contributing

1. Değişiklik yap
2. Test et
3. Commit et
4. Push et

## 📞 İletişim / Contact

Sorular için GitHub issues kullanın.

---

**Son Güncelleme / Last Updated:** 2024
**Versiyon / Version:** 2.0 (Modüler)
