"""
Ders Programı Uygulaması - Yapılandırma Ayarları
Configuration settings for the Course Schedule Application
"""
import os

class Config:
    """Temel yapılandırma sınıfı / Base configuration class"""

    # Flask ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Veritabanı ayarları
    # Geliştirme ortamı için yerel yol, production için PythonAnywhere yolu
    if os.path.exists('/home/mesauc/mysite'):
        # PythonAnywhere ortamı
        DATABASE_PATH = '/home/mesauc/mysite/ders_programi.db'
    else:
        # Yerel geliştirme ortamı
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        DATABASE_PATH = os.path.join(BASE_DIR, 'ders_programi.db')

    # Uygulama ayarları
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Dosya yükleme ayarları
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB maksimum dosya boyutu

class DevelopmentConfig(Config):
    """Geliştirme ortamı yapılandırması"""
    DEBUG = True

class ProductionConfig(Config):
    """Production ortamı yapılandırması"""
    DEBUG = False

# Yapılandırma sözlüğü
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
