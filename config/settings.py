"""
Konfigürasyon Yönetimi
======================
Bu dosya projedeki tüm ayarları merkezi olarak yönetir.
- Dosya yolları
- Model ayarları
- Ses işleme parametreleri
- Environment variables (.env dosyasından)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle (HUGGINGFACE_TOKEN gibi gizli bilgiler için)
# load_dotenv() bulunduğu klasörde .env dosyasını arar ve içindeki
# değişkenleri environment variables olarak yükler
load_dotenv()

# Proje Ana Dizini
# __file__ bu dosyanın (settings.py) tam yolunu verir
# .parent bir üst klasöre çıkar (config/ -> proje root)
# .resolve() mutlak (absolute) path'e çevirir
BASE_DIR = Path(__file__).parent.parent.resolve()

# Klasör Yolları
# BASE_DIR / "klasor_adi" ile yolları birleştiriyoruz
# Bu şekilde Windows/Mac/Linux'ta çalışan platformdan bağımsız yollar olur
UPLOAD_DIR = BASE_DIR / "uploads"        # Yüklenen videolar buraya
OUTPUT_DIR = BASE_DIR / "outputs"        # Üretilen JSON dosyaları
MODEL_DIR = BASE_DIR / "models"          # İndirilen AI modelleri
LOG_DIR = BASE_DIR / "logs"              # Log dosyaları

# Klasörlerin var olduğundan emin ol
# exist_ok=True: Klasör zaten varsa hata verme
for directory in [UPLOAD_DIR, OUTPUT_DIR, MODEL_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Whisper (Speech-to-Text) Ayarları
# os.getenv("KEY", "default") -> .env'den KEY'i oku, yoksa default kullan
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
# Model boyutları: tiny, base, small, medium, large
# small = 244MB, iyi performans/doğruluk dengesi

WHISPER_LANGUAGE = os.getenv("LANGUAGE", "tr")
# Dil kodu: tr=Türkçe, en=İngilizce
# Dil belirtmek Whisper'ın doğruluğunu artırır

# Pyannote (Speaker Diarization) Ayarları
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
# Hugging Face token - pyannote.audio modeli indirmek için gerekli
# .env dosyasından okunur (GÜVENLİK: Bu token asla Git'e eklenmemeli!)

# Ses İşleme Ayarları
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
# Sample rate: Saniyede kaç ses örneği
# 16000 Hz = 16 kHz, konuşma tanıma için optimal
# Daha yüksek değerler (44100) müzik için, ama dosya boyutunu artırır

AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
# Kanal sayısı: 1=Mono, 2=Stereo
# Konuşma tanıma için mono yeterli, dosya boyutu yarı yarıya iner

# Video İşleme Ayarları
SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
# Desteklenen video formatları
# FFmpeg bunların hepsini işleyebilir

SUPPORTED_AUDIO_FORMATS = [".wav", ".mp3", ".m4a", ".flac"]
# Desteklenen ses formatları

# Logging Ayarları
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# Log seviyeleri: DEBUG < INFO < WARNING < ERROR < CRITICAL
# DEBUG: Her şeyi logla (geliştirme için)
# INFO: Normal bilgiler (production için)
# ERROR: Sadece hatalar

LOG_ROTATION = "1 day"  # Her gün yeni log dosyası
LOG_RETENTION = "7 days"  # 7 günden eski logları sil

# Uygulama Ayarları
MAX_FILE_SIZE_MB = 500  # Maksimum video boyutu (MB)
# Çok büyük videolar belleği doldurabilir

TEMP_FILE_CLEANUP = True  # İşlem sonrası geçici dosyaları sil
# True: Temiz tutmak için sil
# False: Debug için sakla
