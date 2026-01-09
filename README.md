# 🎥 Video Mülakat Transkripsiyon Sistemi

Video mülakatlardan konuşmaları metne çeviren ve soruları cevaplarla eşleştiren açık kaynak Python projesi.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51.0-red.svg)](https://streamlit.io/)

---

## 🎯 Proje Amacı

**Video mülakatlar** için tasarlanmış transkripsiyon sistemi:
- Adaylar soruları video ile cevaplıyor
- Sistem videoyu metne çeviriyor
- Soruları cevaplarla otomatik eşleştiriyor
- İnsan kaynakları için okunabilir rapor oluşturuluyor

**Hedef Kullanıcılar:** İK departmanları, işe alım platformları, mülakat yapan şirketler

---

## ✨ Özellikler

### 🎬 Video Transkripsiyon
- **Ses Çıkarma:** FFmpeg ile profesyonel kalite
- **Konuşma Tanıma:** faster-whisper (OpenAI Whisper optimizasyonu)
  - 4-5x daha hızlı
- **Model:** large-v3-turbo (809 MB, en iyi doğruluk/hız dengesi)
- **Dil Desteği:** 99 dil (Türkçe, İngilizce, otomatik algılama)
- **Doğruluk:** %85+ (Türkçe için)

### 👥 Konuşmacı Ayırma
- **pyannote.audio 3.1** ile speaker diarization
- Otomatik konuşmacı tespiti
- Zaman damgalı segmentler
- Konuşmacı istatistikleri (süre, kelime sayısı, yüzde)

### 🔍 Soru-Cevap Eşleştirme
- **Eşit Zaman Segmentasyonu** algoritması
- questions.txt desteği (her satırda bir soru)
- Otomatik eşleştirme (video_duration / soru_sayısı)
- JSON + Markdown çıktı

### 🎨 Web Arayüzü (Streamlit)
- Drag & drop video upload
- 3 soru girişi metodu:
  - Yok (sadece transkripsiyon)
  - Dosya yükle (questions.txt)
  - Manuel giriş (textarea)
- Ayarlar:
  - Model boyutu (tiny → large-v3-turbo)
  - Dil (Türkçe, İngilizce, otomatik)
  - Konuşmacı sayısı (0 = otomatik)
- Canlı önizleme ve istatistikler
- 4 format indirme (JSON, TXT, QA JSON, QA Markdown)

### 📊 Çıktı Formatları
- **JSON:** Yapılandırılmış veri (API/programatik kullanım)
- **TXT:** Okunabilir transkript (timeline + istatistikler)
- **QA JSON:** Soru-cevap çiftleri (yapılandırılmış)
- **QA Markdown:** Profesyonel mülakat raporu (insan kaynakları için)

---

## 🚀 Hızlı Başlangıç

### 📋 Gereksinimler

- **Python 3.8+**
- **FFmpeg** (ses çıkarma için)
- **CUDA** (opsiyonel, GPU desteği için)
- **10 GB disk** (modeller için)

### 🔧 Kurulum

#### 1. FFmpeg Kurulumu

**Windows:**
```bash
# Chocolatey ile (önerilen)
choco install ffmpeg

# veya https://ffmpeg.org/download.html adresinden manuel indirin
```

**MacOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

Doğrulama:
```bash
ffmpeg -version
```

#### 2. Projeyi Klonlayın

```bash
git clone https://github.com/gp3lin/video-to-text.git
cd video-to-text
```

#### 3. Sanal Ortam Oluşturun

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 4. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

#### 5. Hugging Face Token (pyannote.audio için)

1. https://huggingface.co/ hesap oluşturun (ücretsiz)
2. Settings → Access Tokens → New Token (Read yetkisiyle)
3. `.env.example` dosyasını `.env` olarak kopyalayın:
   ```bash
   cp .env.example .env
   ```
4. Token'ı `.env` dosyasına ekleyin:
   ```
   HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxx
   ```

---
## 💻 Kullanım

### 🎨 Web Arayüzü (Önerilen)

#### Windows:
```bash
# Çift tıklayın:
run_ui.bat
```

#### Linux/Mac:
```bash
./run_ui.sh
```

#### Manuel:
```bash
streamlit run app_ui.py
```

**Tarayıcıda:** http://localhost:8501

#### Adımlar:
1. Video yükle (MP4, AVI, MOV, MKV, WEBM)
2. Sorular ekle (opsiyonel):
   - Dosya yükle (questions.txt)
   - veya Manuel gir
3. Ayarları seç (model, dil, konuşmacı sayısı)
4. "İşleme Başla" butonuna tıkla
5. Sonuçları indir (4 format)

---

### 🖥️ Komut Satırı (CLI)

#### Temel Kullanım:
```bash
python v_to_t.py video.mp4
```

#### QA Matching ile:
```bash
python v_to_t.py video.mp4 --questions questions.txt
```

#### Tam Kontrol:
```bash
python v_to_t.py interview.mp4 \
  --questions questions.txt \
  --model large-v3-turbo \
  --language tr \
  --num-speakers 2 \
  --output mülakat_sonuc.json \
  --verbose
```

#### Parametreler:

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `video.mp4` | Video dosyası (zorunlu) | - |
| `--questions` | Soru dosyası (.txt) | None |
| `--model` | Model boyutu | large-v3-turbo |
| `--language` | Dil kodu (tr, en) | Otomatik |
| `--num-speakers` | Konuşmacı sayısı (0=oto) | 0 |
| `--output` | Çıktı dosyası | outputs/{video}_output.json |
| `--no-text` | TXT dosyası oluşturma | False |
| `--verbose` | Detaylı log | False |

#### Model Boyutları:

| Model | Boyut | Hız | Doğruluk | Önerilen |
|-------|-------|-----|----------|----------|
| `tiny` | 39 MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Hızlı test |
| `base` | 74 MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Test |
| `small` | 244 MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Geliştirme |
| `medium` | 769 MB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Production |
| `large-v3-turbo` | 809 MB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ✅ ÖNERİLEN |
| `large-v3` | 1550 MB | ⚡ | ⭐⭐⭐⭐⭐ | Maksimum doğruluk |

---

## 📝 questions.txt Formatı

**Basit Text Dosyası** (her satırda bir soru):

```
Kendinizden bahseder misiniz?
Neden bu pozisyonda çalışmak istiyorsunuz?
En büyük başarınız nedir?
Zayıf yönleriniz nelerdir?
5 yıl sonra kendinizi nerede görüyorsunuz?
```

**Notlar:**
- Her satırda tek bir soru
- Boş satırlar otomatik filtrelenir
- UTF-8 encoding (Türkçe karakter desteği)
- Soru numarası gerekmez

---

## 📊 Çıktı Örnekleri

### JSON Output (Normal Transkript)

```json
{
  "metadata": {
    "video_name": "interview.mp4",
    "duration_seconds": 180.0,
    "language": "tr",
    "num_speakers": 2,
    "num_segments": 15
  },
  "timeline": [
    {
      "start": 0.0,
      "end": 15.5,
      "speaker": "SPEAKER_00",
      "text": "Merhaba, kendinizden bahseder misiniz?",
      "confidence": 0.95
    },
    {
      "start": 15.8,
      "end": 45.2,
      "speaker": "SPEAKER_01",
      "text": "Merhaba, ben Ali. 5 yıldır yazılım geliştiriyorum...",
      "confidence": 0.92
    }
  ],
  "speakers": {
    "SPEAKER_00": {
      "total_duration": 30.0,
      "total_words": 50,
      "percentage": 16.7
    },
    "SPEAKER_01": {
      "total_duration": 150.0,
      "total_words": 250,
      "percentage": 83.3
    }
  }
}
```

### QA JSON (Soru-Cevap Eşleştirme)

```json
{
  "metadata": {
    "total_questions": 3,
    "avg_segment_duration": 60.0,
    "matching_method": "equal_time_segmentation"
  },
  "qa_pairs": [
    {
      "question_number": 1,
      "question": "Kendinizden bahseder misiniz?",
      "time_segment": {
        "start": 0.0,
        "end": 60.0
      },
      "answer": {
        "text": "Merhaba, ben Ali. 5 yıldır yazılım geliştiriyorum...",
        "speakers": {
          "SPEAKER_00": "Merhaba, kendinizden bahseder misiniz?",
          "SPEAKER_01": "Ben Ali. 5 yıldır..."
        },
        "word_count": 85
      }
    }
  ]
}
```

### Markdown Rapor (QA)

```markdown
# Mülakat Soru-Cevap Raporu

**Video:** interview.mp4
**Süre:** 180 saniye (3:00)
**Soru Sayısı:** 3

---

## Soru 1: Kendinizden bahseder misiniz?

**Zaman Aralığı:** 0:00 - 1:00 (60 saniye)
**Kelime Sayısı:** 85

### Cevap:
Merhaba, ben Ali. 5 yıldır yazılım geliştiriyorum...

### Konuşmacı Bazlı Detay:
**SPEAKER_00:** Merhaba, kendinizden bahseder misiniz?
**SPEAKER_01:** Ben Ali. 5 yıldır yazılım geliştiriyorum...
```

---

## 🏗️ Proje Yapısı

```
video-to-text/
├── app/
│   ├── video_processor.py      # Video/audio işleme
│   ├── transcriber.py           # faster-whisper entegrasyonu
│   ├── diarizer.py              # pyannote.audio entegrasyonu
│   ├── output_formatter.py      # JSON/TXT formatı
│   └── qa_matcher.py            # Soru-cevap eşleştirme
├── config/
│   └── settings.py              # Konfigürasyon
├── outputs/                     # Çıktı dosyaları
├── Günlük/                      # Geliştirme günlükleri
├── app_ui.py                    # Web UI (Streamlit)
├── v_to_t.py                    # CLI
├── test_qa_matcher.py           # Mock test scripti
├── run_ui.bat                   # Windows launcher
├── run_ui.sh                    # Linux/Mac launcher
├── questions.txt                # Örnek sorular
├── requirements.txt             # Bağımlılıklar
└── .env.example                 # Konfigürasyon örneği
```

---

## 🛠️ Teknoloji Stack

| Kategori | Teknoloji | Amaç |
|----------|-----------|------|
| **Speech-to-Text** | faster-whisper | Transkripsiyon (4-5x hızlı) |
| **Diarization** | pyannote.audio 3.1 | Konuşmacı ayırma |
| **Video İşleme** | moviepy, pydub | Video/audio dönüşüm |
| **Web UI** | Streamlit 1.51.0 | Kullanıcı arayüzü |
| **AI Backend** | PyTorch, CUDA | Model inference |
| **Veri İşleme** | numpy, pandas | Veri analizi |
| **Logging** | loguru | Loglama |

---

## 📈 Performans

**Test Sistemi:** AMD Ryzen 7 / 16GB RAM / CPU only

| Video Süresi | Model | İşlem Süresi | Real-time Factor |
|--------------|-------|--------------|------------------|
| 1 dakika | large-v3-turbo | ~45 saniye | 0.75x |
| 5 dakika | large-v3-turbo | ~3.5 dakika | 0.7x |
| 10 dakika | large-v3-turbo | ~7 dakika | 0.7x |

**GPU ile:** 3-5x daha hızlı (RTX 3060 ile test edildi)

---

## 🧪 Test

### Mock Test (Video Olmadan)

```bash
python test_qa_matcher.py
```

**Amaç:** QA matching algoritmasını mock data ile test et

**Çıktı:**
- `outputs/test_qa.json`
- `outputs/test_qa.md`

---

## 📝 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.


---

## 🙏 Teşekkürler

- **OpenAI** - Whisper model
- **pyannote.audio** - Speaker diarization
- **Streamlit** - Web framework
- **Hugging Face** - Model hosting

---

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**
