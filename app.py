"""
Ders Programı Yönetim Sistemi - Ana Uygulama Dosyası
Course Schedule Management System - Main Application File

Modüler Flask Uygulaması
Modular Flask Application
"""

from flask import Flask
from config import config
import database as db
from routes import main_bp

# Flask uygulamasını oluştur
app = Flask(__name__)

# Yapılandırmayı yükle
# Development veya production ortamı seç
import os
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Blueprint'leri kaydet
app.register_blueprint(main_bp)

# Veritabanını başlat
with app.app_context():
    db.init_db()

if __name__ == '__main__':
    # Geliştirme sunucusunu başlat
    # Development server
    debug_mode = app.config.get('DEBUG', True)
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
