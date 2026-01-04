# B-LΞXIS - Proje Dökümantasyonu

> **Lexical Intelligence System** - Video Mülakat Transkripsiyon ve Analiz Sistemi

---

## 📁 Proje Yapısı

```
video-to-text/
├── app/                    # Ana uygulama modülleri
│   ├── __init__.py
│   ├── video_processor.py  # Video → Ses dönüştürme
│   ├── transcriber.py      # Ses → Metin (faster-whisper)
│   ├── diarizer.py         # Konuşmacı ayırma (pyannote)
│   ├── output_formatter.py # Sonuçları birleştirme
│   └── qa_matcher.py       # Soru-cevap eşleştirme
│
├── config/
│   └── settings.py         # Merkezi ayarlar (GPU, model, log)
│
├── .streamlit/
│   └── config.toml         # UI tema ayarları
│
├── logs/                   # Log dosyaları (otomatik)
├── models/                 # AI modelleri (otomatik indirilir)
├── outputs/                # İşlenmiş çıktılar
├── uploads/                # Geçici yükleme klasörü
│
├── v_to_t.py              # CLI arayüzü
├── app_ui.py              # Web UI (Streamlit)
├── run_ui.bat/sh          # UI başlatma scriptleri
└── requirements.txt       # Python bağımlılıkları
```

---

## 📂 Klasör ve Dosya Açıklamaları

### `app/` - Ana Modüller

#### `video_processor.py`
**Görev:** Video dosyası işlemleri

**Fonksiyonlar:**
- `validate_video_file()` → Video formatını kontrol (.mp4, .avi, .mov, .mkv, .webm)
- `extract_audio_from_video()` → FFmpeg ile ses çıkarma (16kHz mono WAV)
- `get_audio_duration()` → Ses süresini hesaplama

#### `transcriber.py`
**Görev:** Konuşmayı metne çevirme (Speech-to-Text)

**Model:** faster-whisper large-v3-turbo (809MB)

**Önemli ayarlar:**
- `device="cuda"` → **GPU kullan** (v_to_t.py:161 hardcoded)
- `compute_type="float16"` → GPU optimizasyonu
- `beam_size=5` → Doğruluk/hız dengesi

**Performans:** 11 dk video → **1-2 dakika** (GPU ile 10x hızlanma)

#### `diarizer.py`
**Görev:** Konuşmacıları ayırma (Speaker Diarization)

**Model:** pyannote.audio 3.1 (~300MB)

**Ayarlar:**
- `num_speakers=None` → Otomatik tespit
- `min_duration=0.5s` → Gürültü filtresi
- `device="auto"` → GPU varsa kullan

#### `output_formatter.py`
**Görev:** Sonuçları birleştir ve formatla

**Fonksiyonlar:**
- `merge_results()` → Whisper + pyannote birleştir
- `export_to_json()` → JSON formatında kaydet
- `export_to_text()` → **Paragraf formatında TXT** oluştur ⭐

**Önemli değişiklik:**
- ❌ Eski: Timeline (zaman damgalı)
- ✅ Yeni: Konuşmacı paragrafları

**TXT formatı:**
```
TRANSKRİPT (PARAGRAF FORMATINDA)
========================================

SPEAKER_00
----------------------------------------
Konuşma Süresi: 45.2s (100%) | Kelime: 234

Merhaba ben Ali. Bugün sizlerle...
[tüm konuşma paragraf olarak]
```

#### `qa_matcher.py`
**Görev:** Soru-cevap eşleştirme

**Algoritma:** Eşit zaman segmentasyonu
- Video süresi ÷ Soru sayısı = Her sorunun süresi
- Her soruya o zaman aralığındaki transkript eşleşir

**Örnek:**
```
90 saniye video, 3 soru
→ Q1: [0:00-0:30], Q2: [0:30-1:00], Q3: [1:00-1:30]
```

**Çıktılar:**
- `{video}_qa.json` → Yapılandırılmış veri
- `{video}_qa.md` → Okunabilir rapor

---

### `config/settings.py`
**Görev:** Merkezi konfigürasyon

**GPU Ayarları (sizin değişiklik):**
```python
WHISPER_DEVICE = "auto"        # GPU otomatik tespit
WHISPER_COMPUTE_TYPE = "float16"  # GPU optimizasyonu
```

**Model:**
```python
WHISPER_MODEL_SIZE = "large-v3-turbo"
WHISPER_LANGUAGE = "tr"
```

**Klasörler:**
```python
UPLOAD_DIR = "uploads/"
OUTPUT_DIR = "outputs/"
MODEL_DIR = "models/"
LOG_DIR = "logs/"
```

**Logging:**
```python
LOG_LEVEL = "INFO"
LOG_ROTATION = "1 day"   # Her gün yeni log
LOG_RETENTION = "7 days" # 7 günlük tutma
```

---

### `.streamlit/config.toml`
**Görev:** Web UI tema ayarları

**Tema (sizin değişiklik):**
```toml
[theme]
primaryColor = "#9D4EDD"              # Mor
backgroundColor = "#FAF9FC"           # Beyazımsı ⭐
secondaryBackgroundColor = "#F5F0FA"  # Açık mor
textColor = "#2D2D2D"                 # Koyu gri
```

**Eski:** Dark theme (#0D1117)
**Yeni:** Light theme (#FAF9FC) ⭐

---

### `v_to_t.py` - CLI Arayüzü

**Görev:** Komut satırından video işleme

**Kullanım:**
```bash
python v_to_t.py video.mp4
python v_to_t.py video.mp4 --questions questions.txt
```

**Ana fonksiyon:** `process_video()`
1. Video validasyon
2. Ses çıkarma (FFmpeg)
3. Transcription (GPU)
4. Diarization (GPU)
5. Merge
6. QA matching (opsiyonel)
7. Export (JSON + TXT)

**Sizin değişiklikleriniz:**
- **Satır 138:** `setup_logging()` eklendi (UI için log)
- **Satır 161-162:** GPU hardcode

---

### `app_ui.py` - Web Arayüzü

**Görev:** Streamlit tabanlı kullanıcı dostu UI

**Özellikler:**
- Video yükleme (drag & drop)
- Soru girişi (manuel/dosya)
- Model/dil seçimi
- Sonuç görüntüleme
- Dosya indirme

**Sizin değişiklikleriniz:**

1. **Session State (satır 207-237, 252-354):**
   - Sonuçlar `st.session_state`'e kaydediliyor
   - Download sonrası kaybolma problemi çözüldü ✅

2. **Paragraf formatı (satır 329-354):**
   - Timeline tab'ları kaldırıldı
   - Konuşmacı bazlı paragraflar

**Akış:**
```
Video yükle → İşle → Session'a kaydet → Göster
→ Download → Page rerun → Session'dan yükle → Kaybolmaz ✅
```

---

## 🔄 İşlem Akışı (Pipeline)

### 1. Video Yükleme
- UI veya CLI'dan video seç
- Format validasyonu (.mp4, .avi, etc.)

### 2. Ses Çıkarma
- FFmpeg ile WAV'a dönüştür
- 16kHz mono format

### 3. Transcription (GPU)
- faster-whisper model
- CUDA float16 optimizasyon
- Çıktı: Zaman damgalı metin

### 4. Diarization (GPU)
- pyannote.audio model
- Konuşmacı tespiti
- Çıktı: SPEAKER_00, SPEAKER_01...

### 5. Merge
- Transkript + Diarization birleştir
- Konuşmacı istatistikleri

### 6. QA Matching (opsiyonel)
- Eşit zaman segmentasyonu
- Soru-cevap eşleştirme

### 7. Export
- JSON (yapılandırılmış)
- TXT (paragraf formatı)
- QA JSON/MD (opsiyonel)

---

## 🚀 Performans İyileştirmeleri

### GPU Optimizasyonu

**Öncesi (CPU):**
- Device: CPU
- Compute: int8
- **11 dk video → 9+ dakika**

**Sonrası (GPU):**
- Device: CUDA
- Compute: float16
- **11 dk video → 1-2 dakika** ⚡

**10x hızlanma!**

**Değişiklikler:**
1. PyTorch CUDA 12.1 kuruldu
2. `config/settings.py` → GPU ayarları
3. `v_to_t.py:161-162` → Hardcode

---

## 🐛 Düzeltilen Hatalar

### 1. Log Dosyaları Oluşmama
**Sorun:** UI'dan çalışınca log tutmuyordu
**Sebep:** `setup_logging()` sadece CLI'da çağrılıyordu
**Çözüm:** `process_video()` başına eklendi (v_to_t.py:138)

### 2. Download Sonrası Kaybolma
**Sorun:** İndir butonuna tıklayınca sonuçlar kayboluyordu
**Sebep:** Page rerun → `result` variable kayboluyor
**Çözüm:** `st.session_state` kullanımı (app_ui.py:234-237, 252-354)

### 3. NoneType Karşılaştırma Hatası
**Sorun:** `'>' not supported between instances of 'NoneType' and 'int'`
**Sebep:** Segment'lerde start/end None olabiliyordu
**Çözüm:** None kontrolü (qa_matcher.py:166-172, v_to_t.py:198)

### 4. CUDA Kütüphane Hatası
**Sorun:** `cublas64_12.dll not found`
**Sebep:** PyTorch CUDA 11.8 ama 12.x gerekli
**Çözüm:** PyTorch CUDA 12.1 yeniden kuruldu

---

## 📊 Çıktı Formatları

### JSON (`_output.json`)
```json
{
  "metadata": {
    "video_name": "interview.mp4",
    "duration_seconds": 83.0,
    "num_speakers": 2
  },
  "timeline": [...],      // Zaman bazlı
  "speakers": {...},      // İstatistikler
  "full_transcript": ""
}
```

### TXT (`_output.txt`) - Paragraf Formatı
```
TRANSKRİPT (PARAGRAF FORMATINDA)
============================

SPEAKER_00
----------------------------
Konuşma: 45.2s (100%) | Kelime: 234

[Tüm konuşma paragraf olarak]
```

### QA JSON (`_qa.json`)
```json
{
  "qa_pairs": [
    {
      "question": "Kendinizden bahseder misiniz?",
      "time_segment": {"start": 0, "end": 30},
      "answer": {"text": "...", "word_count": 150}
    }
  ]
}
```

---

## 🎯 Kullanım Örnekleri

### CLI:
```bash
# Basit
python v_to_t.py video.mp4

# Sorularla
python v_to_t.py video.mp4 --questions sorular.txt

# Özel ayarlar
python v_to_t.py video.mp4 \
  --model large-v3-turbo \
  --language tr \
  --output sonuc.json
```

### UI:
```bash
# Windows
run_ui.bat

# Linux/Mac
./run_ui.sh

# Tarayıcıda aç
http://localhost:8502
```

---

## 🔧 Kritik Kod Referansları

| Dosya | Satır | Değişiklik |
|-------|-------|------------|
| v_to_t.py | 138 | Logging kurulumu (UI için) |
| v_to_t.py | 161-162 | GPU hardcode |
| v_to_t.py | 198 | None kontrolü (num_speakers) |
| app_ui.py | 234-237 | Session state kayıt |
| app_ui.py | 252-354 | Session'dan gösterme |
| output_formatter.py | 380-398 | Paragraf formatı |
| qa_matcher.py | 166-172 | None kontrolü (segments) |
| settings.py | 77, 81 | GPU ayarları |
| config.toml | 9, 12, 15 | Light theme |

---

## 📚 Teknolojiler

- **faster-whisper:** Speech-to-Text (Whisper optimized)
- **pyannote.audio:** Speaker Diarization
- **PyTorch:** AI framework (CUDA 12.1)
- **Streamlit:** Web UI framework
- **FFmpeg:** Video/ses işleme
- **Loguru:** Logging sistemi

---

## 🎨 Tema Geçişi

| Özellik | Eski (Dark) | Yeni (Light) |
|---------|-------------|--------------|
| Arka plan | #0D1117 (siyah) | #FAF9FC (beyazımsı) |
| Sidebar | #161B22 (gri) | #F5F0FA (açık mor) |
| Metin | #E6EDF3 (açık) | #2D2D2D (koyu) |
| Vurgu | #9D4EDD (mor) | #9D4EDD (aynı) |

---

**Proje:** B-LΞXIS v2.1.0
**Güncelleme:** 2026-01-03
**Geliştirici:** Pelin + Claude Sonnet 4.5
**Repo:** https://github.com/gp3lin/video-to-text

🗣️ **Lexical Intelligence - Transforming speech into structured knowledge**
