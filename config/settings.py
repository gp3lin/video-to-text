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

# Offline mod için environment variables ayarla
# Bu sayede modeller sadece yerel dizinden yüklenir, internet kullanılmaz
MODEL_CACHE_DIR = str(Path(__file__).parent.parent / "models")

# Hugging Face cache dizinlerini ayarla
os.environ.setdefault("HF_HOME", MODEL_CACHE_DIR)
os.environ.setdefault("TRANSFORMERS_CACHE", MODEL_CACHE_DIR)
os.environ.setdefault("HF_DATASETS_CACHE", MODEL_CACHE_DIR)
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", MODEL_CACHE_DIR)

# Offline mod ayarları (.env dosyasından okur, yoksa varsayılan değerleri kullanır)
# "1" değeri offline modu aktif eder, "0" veya boş bırakılırsa online mod aktif olur
if os.getenv("HF_HUB_OFFLINE", "0") == "1":
    os.environ["HF_HUB_OFFLINE"] = "1"
if os.getenv("TRANSFORMERS_OFFLINE", "0") == "1":
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
if os.getenv("HF_DATASETS_OFFLINE", "0") == "1":
    os.environ["HF_DATASETS_OFFLINE"] = "1"

# Symlink devre dışı bırakma (Windows izin hatası için)
# Windows'ta symlink oluşturma yetkisi yoksa bu ayar symlink yerine dosya kopyası yapar
if os.getenv("HF_HUB_DISABLE_SYMLINKS", "0") == "1":
    os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

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

# faster-whisper (Speech-to-Text) Ayarları
# os.getenv("KEY", "default") -> .env'den KEY'i oku, yoksa default kullan
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "large-v3-turbo")
# Model boyutları: tiny, base, small, medium, large-v3, large-v3-turbo
# large-v3-turbo = 809MB, en iyi doğruluk ve hız dengesi (ÖNERİLEN)
# large-v3 = 1550MB, en yüksek doğruluk (yavaş)
# medium = 769MB, iyi doğruluk
# small = 244MB, hızlı ama düşük doğruluk

WHISPER_LANGUAGE = os.getenv("LANGUAGE", "tr")
# Dil kodu: tr=Türkçe, en=İngilizce
# Dil belirtmek Whisper'ın doğruluğunu artırır

# faster-whisper Optimizasyon Ayarları
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "auto")
# Device: "cpu", "cuda", "auto"
# CUDA varsa GPU kullanmak için "cuda" veya "auto"

WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "float16")
# Compute type: "float32", "float16", "int8", "int8_float16"
# CPU için: "int8" (önerilen - 2x hızlı)
# GPU için: "float16" veya "int8_float16" (önerilen)

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
