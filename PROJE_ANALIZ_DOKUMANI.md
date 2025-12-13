# Video-to-Text Projesi - Detaylı Analiz ve Dokümantasyon

**Tarih:** 30 Kasım 2025
**Proje Durumu:** Faz 2 Tamamlandı - Core Modüller İmplemente Edildi
**Geliştirme Ortamı:** Python 3.x, Windows

---

## İçindekiler

1. [Proje Genel Bakış](#proje-genel-bakış)
2. [Klasör ve Dosya Yapısı](#klasör-ve-dosya-yapısı)
3. [Modül Bazlı Detaylı Analiz](#modül-bazlı-detaylı-analiz)
4. [Veri Akışı ve Mimari](#veri-akışı-ve-mimari)
5. [Kullanılan Teknolojiler](#kullanılan-teknolojiler)
6. [Konfigürasyon Sistemi](#konfigürasyon-sistemi)
7. [Güvenlik ve Best Practices](#güvenlik-ve-best-practices)
8. [Eksik Bileşenler ve Sonraki Adımlar](#eksik-bileşenler-ve-sonraki-adımlar)

---

## 1. Proje Genel Bakış

### Amaç
Video dosyalarından konuşmaları metne çeviren ve konuşmacılara göre ayıran açık kaynak bir Python projesi.

### Temel Özellikler
- ✅ **Video'dan Ses Çıkarma**: FFmpeg kullanarak video dosyalarından ses extraction
- ✅ **Konuşma Tanıma (Speech-to-Text)**: OpenAI Whisper ile çoklu dil desteği
- ✅ **Konuşmacı Ayırma (Speaker Diarization)**: pyannote.audio ile kim-ne-zaman konuştu analizi
- ✅ **Akıllı Birleştirme**: Transcription ve diarization sonuçlarını overlap mantığıyla birleştirme
- ✅ **Çoklu Format Desteği**: JSON ve Text formatında çıktı
- ⏳ **Web Arayüzü**: Streamlit (henüz implement edilmedi)
- ⏳ **CLI Arayüzü**: Komut satırı arabirimi (kısmi implement)

### Kullanım Senaryoları
1. **Röportaj Transkriptleri**: İki veya daha fazla kişinin konuştuğu röportajları metne çevirme
2. **Podcast Dökümantasyonu**: Podcast bölümlerini metin formatında arşivleme
3. **Toplantı Kayıtları**: Video toplantılarının metinlerini konuşmacılara göre ayırarak kaydetme
4. **Eğitim İçerikleri**: Ders videolarından not çıkarma
5. **Araştırma**: Sözel içeriklerin nicel analizi için veri hazırlama

---

## 2. Klasör ve Dosya Yapısı

### Proje Dizin Ağacı

```
video-to-text/
│
├── 📁 app/                          # Ana uygulama modülleri
│   ├── __init__.py                  # Package tanımı (boş)
│   ├── video_processor.py           # Video/ses işleme (243 satır)
│   ├── transcriber.py               # Konuşma tanıma (336 satır)
│   ├── diarizer.py                  # Konuşmacı ayırma (423 satır)
│   └── output_formatter.py          # Çıktı formatlama (452 satır)
│
├── 📁 config/                       # Konfigürasyon yönetimi
│   ├── __init__.py                  # Package tanımı (boş)
│   └── settings.py                  # Tüm ayarlar (89 satır)
│
├── 📁 uploads/                      # Yüklenen video dosyaları
│   └── .gitkeep                     # (Boş klasörü Git'te tutmak için)
│
├── 📁 outputs/                      # Üretilen JSON/TXT dosyaları
│   └── .gitkeep
│
├── 📁 models/                       # İndirilen AI modelleri
│   └── .gitkeep                     # (Whisper ve pyannote modelleri buraya indirilir)
│
├── 📁 logs/                         # Log dosyaları
│   └── .gitkeep
│
├── 📁 venv/                         # Python sanal ortamı (Git'te yok)
│
├── 📁 .git/                         # Git version control
│
├── 📁 .claude/                      # Claude Code konfigürasyonu
│   └── settings.local.json
│
├── 📄 v_to_t.py                     # Ana CLI programı (18 satır - henüz iskelet)
├── 📄 requirements.txt              # Python bağımlılıkları (24 satır)
├── 📄 .env.example                  # Örnek environment variables (16 satır)
├── 📄 .gitignore                    # Git ignore kuralları (83 satır)
└── 📄 README.md                     # Proje README (147 satır)
```

### Dosya Boyutları ve Karmaşıklık

| Modül | Satır Sayısı | Fonksiyon/Sınıf | Karmaşıklık |
|-------|-------------|----------------|------------|
| video_processor.py | 243 | 3 fonksiyon | Orta |
| transcriber.py | 336 | 1 sınıf (6 metod) + 1 yardımcı fonksiyon | Yüksek |
| diarizer.py | 423 | 1 sınıf (5 metod) + 1 yardımcı fonksiyon | Yüksek |
| output_formatter.py | 452 | 1 sınıf (8 static metod) | Yüksek |
| settings.py | 89 | 0 (sadece konfigürasyon) | Düşük |
| **TOPLAM** | **1,543** | **3 sınıf, 22 metod/fonksiyon** | - |

---

## 3. Modül Bazlı Detaylı Analiz

### 3.1. config/settings.py

**Amaç:** Merkezi konfigürasyon yönetimi

**Sorumluluklar:**
- Environment variables yönetimi (.env dosyasından)
- Klasör yolları tanımlama ve oluşturma
- Model parametreleri
- Ses işleme ayarları
- Logging konfigürasyonu

**Önemli Değişkenler:**

```python
# Klasör Yolları (pathlib.Path nesneleri)
BASE_DIR = Path(__file__).parent.parent.resolve()
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"
LOG_DIR = BASE_DIR / "logs"

# Whisper Ayarları
WHISPER_MODEL_SIZE = "small"  # tiny, base, small, medium, large
WHISPER_LANGUAGE = "tr"       # tr, en, vb.

# Pyannote Ayarları
HUGGINGFACE_TOKEN = ""        # .env'den okunur (GİZLİ)

# Ses İşleme
AUDIO_SAMPLE_RATE = 16000     # 16 kHz (konuşma için optimal)
AUDIO_CHANNELS = 1            # Mono

# Limitler
MAX_FILE_SIZE_MB = 500
```

**Tasarım Kararları:**
1. ✅ **pathlib.Path kullanımı**: Platform bağımsız yol yönetimi (Windows/Linux/Mac)
2. ✅ **Otomatik klasör oluşturma**: `directory.mkdir(exist_ok=True)` ile
3. ✅ **Environment variables**: Gizli bilgiler (token) .env dosyasında
4. ✅ **Type hints yok**: Basit konfigürasyon, type gerekmiyor
5. ✅ **Default değerler**: `os.getenv("KEY", "default")` ile fallback

**İyileştirme Önerileri:**
- ⚠️ Dataclass veya Pydantic kullanarak tip güvenliği eklenebilir
- ⚠️ Validation logic eklenebilir (örn: MAX_FILE_SIZE_MB > 0)

---

### 3.2. app/video_processor.py

**Amaç:** Video dosyalarından ses çıkarma ve ön işleme

**Fonksiyonlar:**

#### 1. `extract_audio_from_video(video_path, output_path=None) -> Path`

**Ne Yapar:**
- Video dosyasından ses kanalını çıkarır
- WAV formatına dönüştürür
- 16 kHz sample rate, mono kanal ayarlar

**Kullanılan Kütüphaneler:**
- `moviepy.editor.VideoFileClip`: Video yükleme
- FFmpeg (arka planda): Ses kodlama

**İş Akışı:**
```
Video Dosyası
    ↓
Video yükleme (VideoFileClip)
    ↓
Ses kanalını al (.audio)
    ↓
WAV formatında kaydet (write_audiofile)
    ├── Sample rate: 16 kHz
    ├── Codec: pcm_s16le (16-bit PCM)
    ├── Kanal: Mono (1 kanal)
    └── FFmpeg parametreleri: -ac 1
    ↓
Kaynakları temizle (close)
    ↓
Ses Dosyası (WAV)
```

**Hata Yönetimi:**
- ✅ Dosya bulunamadı kontrolü
- ✅ Video'da ses yoksa hata
- ✅ Yarım kalmış dosya silme (exception durumunda)
- ✅ Detaylı loglama (loguru)

**Örnek Kullanım:**
```python
audio_path = extract_audio_from_video("video.mp4")
# Çıktı: uploads/video_audio.wav
```

#### 2. `get_audio_duration(audio_path) -> float`

**Ne Yapar:**
- Ses dosyasının süresini saniye cinsinden döndürür

**Kullanım:**
```python
duration = get_audio_duration("audio.wav")
# Çıktı: 125.50 (saniye)
```

#### 3. `validate_video_file(video_path) -> bool`

**Ne Yapar:**
- Video dosyasını doğrular (var mı, format destekleniyor mu, boyut uygun mu)

**Kontroller:**
- ✅ Dosya varlığı
- ✅ Format kontrolü (`.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`)
- ✅ Boyut limiti (MAX_FILE_SIZE_MB)

**Tasarım Kalitesi:**
- ✅ **Separation of Concerns**: Her fonksiyon tek bir iş yapıyor
- ✅ **Type hints**: Parametreler ve dönüş değerleri belirtilmiş
- ✅ **Docstrings**: Her fonksiyon detaylı dokümante edilmiş
- ✅ **Error handling**: Try-except blokları ve temizlik
- ✅ **Logging**: Her adım loglanıyor (debug, info, error, success)
- ✅ **Resource management**: Video/audio nesneleri düzgün kapatılıyor

---

### 3.3. app/transcriber.py

**Amaç:** Ses dosyalarını metne çevirme (Speech-to-Text)

**Ana Sınıf: `Transcriber`**

#### Sınıf Yapısı

```python
class Transcriber:
    def __init__(self, model_size=None, language=None)
    def load_model(self)
    def transcribe(self, audio_path, **kwargs) -> Dict
    def _process_result(self, raw_result) -> Dict
    def _calculate_confidence(self, segment) -> float
    def transcribe_with_progress(self, audio_path, **kwargs) -> Dict
```

#### Model Yönetimi

**Whisper Model Boyutları:**
| Boyut | Dosya | Hız | Doğruluk | Kullanım |
|-------|-------|-----|----------|----------|
| tiny | 39 MB | En hızlı | Düşük | Test |
| base | 74 MB | Hızlı | Orta | Hızlı işler |
| small | 244 MB | Orta | İyi | **ÖNERİLEN** |
| medium | 769 MB | Yavaş | Çok İyi | Yüksek doğruluk |
| large | 1550 MB | En yavaş | En İyi | Kritik işler |

**Model Yükleme:**
```python
def load_model(self):
    self.model = whisper.load_model(
        self.model_size,
        download_root=str(settings.MODEL_DIR)
    )
```

- İlk kullanımda model internet üzerinden indirilir (~/.cache/whisper/)
- Sonraki kullanımlarda cache'den yüklenir (hızlı)
- Lazy loading: Model sadece gerektiğinde yüklenir

#### Transcription İşlemi

**Ana Fonksiyon:**
```python
def transcribe(self, audio_path, **kwargs) -> Dict:
    result = self.model.transcribe(
        str(audio_path),
        language=self.language,
        verbose=False,
        **kwargs
    )
    return self._process_result(result)
```

**Whisper Çıktısı (Ham):**
```python
{
    "text": "Tam metin...",
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 3.5,
            "text": " Merhaba",
            "avg_logprob": -0.15,
            "no_speech_prob": 0.05
        }
    ],
    "language": "tr"
}
```

**İşlenmiş Çıktı:**
```python
{
    "text": "Tam metin...",
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 3.5,
            "text": "Merhaba",  # strip() uygulanmış
            "confidence": 0.95  # Hesaplanmış güven skoru
        }
    ],
    "language": "tr"
}
```

#### Güven Skoru Hesaplama

**Algoritma:**
```python
def _calculate_confidence(self, segment) -> float:
    avg_logprob = segment.get("avg_logprob", -1.0)
    no_speech_prob = segment.get("no_speech_prob", 0.0)

    # avg_logprob'a göre base confidence
    if avg_logprob > -0.5:
        base_confidence = 0.95
    elif avg_logprob > -1.0:
        base_confidence = 0.85
    elif avg_logprob > -1.5:
        base_confidence = 0.75
    else:
        base_confidence = 0.65

    # Sessizlik olasılığıyla azalt
    confidence = base_confidence * (1 - no_speech_prob)

    return max(0.0, min(1.0, confidence))
```

**Neden Gerekli:**
- Whisper doğrudan confidence skoru vermez
- `avg_logprob` ve `no_speech_prob` kullanarak yaklaşık hesaplama
- Kullanıcıya sonuçların güvenilirliği hakkında bilgi

**Tasarım Kalitesi:**
- ✅ **OOP tasarım**: Model yönetimi için sınıf kullanımı
- ✅ **Lazy loading**: Model sadece gerektiğinde yüklenir
- ✅ **Encapsulation**: Private metodlar (_process_result, _calculate_confidence)
- ✅ **Flexibility**: **kwargs ile ekstra parametre desteği
- ✅ **Progress tracking**: İsteğe bağlı ilerleme çubuğu

---

### 3.4. app/diarizer.py

**Amaç:** Konuşmacıları ayırma ve kim-ne-zaman konuştu analizi

**Ana Sınıf: `SpeakerDiarizer`**

#### Sınıf Yapısı

```python
class SpeakerDiarizer:
    def __init__(self, hf_token=None, device="auto")
    def load_model(self)
    def diarize(self, audio_path, num_speakers=None, ...) -> List[Dict]
    def _process_diarization(self, diarization) -> List[Dict]
    def get_speaker_statistics(self, segments) -> Dict
```

#### pyannote.audio Pipeline

**Model:**
- `pyannote/speaker-diarization-3.1` (Hugging Face'de hosted)
- ~300 MB boyutunda
- Hugging Face token gerektirir (ücretsiz hesap)

**Token Gerekliliği:**
```python
# .env dosyasında
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx

# settings.py'de
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
```

**Token Alma:**
1. https://huggingface.co/ → Hesap oluştur
2. Settings → Access Tokens
3. New token (Read yetkisi yeterli)
4. Token'ı `.env` dosyasına ekle

#### GPU vs CPU

**Device Yönetimi:**
```python
def __init__(self, hf_token=None, device="auto"):
    if device == "auto":
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        self.device = device
```

**Performans Farkı:**
| Cihaz | 10 dakikalık ses | Hız |
|-------|------------------|-----|
| CPU (i7) | ~8-10 dakika | 1x |
| GPU (NVIDIA) | ~1-2 dakika | 5-8x |

**GPU Kurulumu (Windows):**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

#### Diarization İşlemi

**Ana Fonksiyon:**
```python
def diarize(self, audio_path, num_speakers=None,
            min_speakers=None, max_speakers=None) -> List[Dict]:

    params = {}
    if num_speakers is not None:
        params["num_speakers"] = num_speakers
    else:
        if min_speakers is not None:
            params["min_speakers"] = min_speakers
        if max_speakers is not None:
            params["max_speakers"] = max_speakers

    diarization = self.pipeline(str(audio_path), **params)
    segments = self._process_diarization(diarization)
    return segments
```

**Kullanım Senaryoları:**

1. **Konuşmacı sayısı biliniyor:**
```python
segments = diarizer.diarize("audio.wav", num_speakers=2)
```

2. **Aralık biliniyor:**
```python
segments = diarizer.diarize("audio.wav", min_speakers=2, max_speakers=5)
```

3. **Otomatik tespit:**
```python
segments = diarizer.diarize("audio.wav")  # pyannote otomatik belirler
```

**Çıktı Formatı:**
```python
[
    {
        "speaker": "SPEAKER_00",
        "start": 0.0,
        "end": 15.5,
        "duration": 15.5
    },
    {
        "speaker": "SPEAKER_01",
        "start": 15.5,
        "end": 32.1,
        "duration": 16.6
    },
    ...
]
```

**Not:** pyannote konuşmacı isimlerini bilmez, sadece `SPEAKER_00`, `SPEAKER_01` gibi etiketler verir.

#### İstatistik Hesaplama

**Fonksiyon:**
```python
def get_speaker_statistics(self, segments) -> Dict:
    # Her konuşmacı için:
    # - Toplam konuşma süresi
    # - Kaç kez konuştu
    # - Ortalama segment süresi
    # - Yüzde oranı
```

**Örnek Çıktı:**
```python
{
    "SPEAKER_00": {
        "total_duration": 125.5,
        "num_segments": 10,
        "avg_segment_duration": 12.55,
        "percentage": 45.2
    },
    "SPEAKER_01": {
        "total_duration": 152.0,
        "num_segments": 12,
        "avg_segment_duration": 12.67,
        "percentage": 54.8
    }
}
```

**Kullanım:**
```python
segments = diarizer.diarize("audio.wav")
stats = diarizer.get_speaker_statistics(segments)
print(f"SPEAKER_00: %{stats['SPEAKER_00']['percentage']}")
```

**Tasarım Kalitesi:**
- ✅ **Token validation**: Token yoksa açıklayıcı hata mesajı
- ✅ **Device flexibility**: Auto/manual GPU/CPU seçimi
- ✅ **Speaker flexibility**: num_speakers veya min/max aralığı
- ✅ **Sorted output**: Segmentler zaman sırasına göre
- ✅ **Statistics**: Kullanışlı istatistik hesaplama

---

### 3.5. app/output_formatter.py

**Amaç:** Transcription ve diarization sonuçlarını birleştirme ve formatlama

**Ana Sınıf: `OutputFormatter` (Tüm metodlar static)**

#### Neden Static Metodlar?

```python
class OutputFormatter:
    @staticmethod
    def merge_results(...): ...

    @staticmethod
    def save_to_json(...): ...
```

**Avantajları:**
- State tutmaya gerek yok (instance variable yok)
- Utility class olarak kullanım
- `OutputFormatter.merge_results()` şeklinde direkt çağrı
- Test etmesi kolay

#### Ana Fonksiyonlar

**1. merge_results() - En Kritik Fonksiyon**

**Sorun:**
- Transcription: "0.0-3.5s arası: 'Merhaba bugün...'"
- Diarization: "0.0-15.5s arası: SPEAKER_00 konuşuyor"
- **Zaman aralıkları tam örtüşmüyor!**

**Çözüm: Overlap (Örtüşme) Mantığı**

```python
def _find_speaker_for_segment(start, end, diarization) -> str:
    max_overlap = 0
    best_speaker = "SPEAKER_UNKNOWN"

    for dia_seg in diarization:
        # Örtüşme hesapla
        overlap_start = max(start, dia_seg["start"])
        overlap_end = min(end, dia_seg["end"])
        overlap = max(0, overlap_end - overlap_start)

        # En çok örtüşeni bul
        if overlap > max_overlap:
            max_overlap = overlap
            best_speaker = dia_seg["speaker"]

    return best_speaker
```

**Görsel Örnek:**
```
Transcription:     [----Segment 1----]
                   0.0              3.5

Diarization:    [--------SPEAKER_00--------]
                0.0                      15.5

Overlap:           [----3.5s----]
                   0.0          3.5

Sonuç: Segment 1 → SPEAKER_00 (3.5s overlap)
```

**Edge Case: Örtüşme Yoksa**

```python
# Örtüşme yoksa en yakın konuşmacıyı bul
if max_overlap == 0:
    min_distance = float('inf')
    for dia_seg in diarization:
        distance = min(
            abs(start - dia_seg["start"]),
            abs(end - dia_seg["end"])
        )
        if distance < min_distance:
            min_distance = distance
            best_speaker = dia_seg["speaker"]
```

**2. _group_by_speaker() - İstatistik**

```python
def _group_by_speaker(merged_segments, diarization) -> Dict:
    speakers = {}

    for seg in merged_segments:
        speaker = seg["speaker"]

        # İlk kez görülüyor
        if speaker not in speakers:
            speakers[speaker] = {
                "total_duration": 0,
                "total_words": 0,
                "num_segments": 0,
                "segments": []
            }

        # Ekle ve hesapla
        speakers[speaker]["segments"].append(seg)
        speakers[speaker]["total_duration"] += seg["duration"]
        speakers[speaker]["num_segments"] += 1
        speakers[speaker]["total_words"] += len(seg["text"].split())

    # Yüzde hesapla
    total_duration = merged_segments[-1]["end"] if merged_segments else 0
    for speaker, data in speakers.items():
        data["percentage"] = round(
            (data["total_duration"] / total_duration) * 100, 1
        )

    return speakers
```

**3. save_to_json() - JSON Kaydetme**

```python
def save_to_json(result, output_path, pretty=True) -> Path:
    with open(output_path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(
                result,
                f,
                indent=2,              # 2 boşluk girintili
                ensure_ascii=False,   # Türkçe karakterler korunur
                sort_keys=False       # Metadata üstte kalsın
            )
        else:
            json.dump(result, f, ensure_ascii=False)
```

**ensure_ascii=False Önemi:**
```python
# ensure_ascii=True (default)
{"text": "Merhaba d\\u00fcnya"}

# ensure_ascii=False
{"text": "Merhaba dünya"}
```

**4. export_to_text() - Okunabilir Metin**

**Çıktı Formatı:**
```
Video: example.mp4
Süre: 125.5s
Dil: tr
Konuşmacı Sayısı: 2
İşlenme Zamanı: 2025-11-30T16:30:45.123456

============================================================
ZAMAN ÇİZELGESİ
============================================================

[0.00s - 3.50s] SPEAKER_00:
  Merhaba, bugün sizlere yeni projemizi anlatacağım.

[3.50s - 15.20s] SPEAKER_01:
  Çok güzel, merak ettim. Detayları dinleyelim.

============================================================
KONUŞMACI İSTATİSTİKLERİ
============================================================

SPEAKER_00:
  Toplam Süre: 65.2s
  Kelime Sayısı: 450
  Segment Sayısı: 10
  Yüzde: %45.2

SPEAKER_01:
  Toplam Süre: 60.3s
  Kelime Sayısı: 420
  Segment Sayısı: 8
  Yüzde: %54.8

============================================================
TAM METİN
============================================================

Merhaba, bugün sizlere yeni projemizi anlatacağım...
```

**Final JSON Yapısı:**

```json
{
  "metadata": {
    "video_name": "example.mp4",
    "duration_seconds": 125.5,
    "language": "tr",
    "num_speakers": 2,
    "num_segments": 18,
    "processed_at": "2025-11-30T16:30:45.123456",
    "model_info": {
      "transcription": "OpenAI Whisper",
      "diarization": "pyannote.audio 3.1"
    }
  },
  "speakers": {
    "SPEAKER_00": {
      "total_duration": 65.2,
      "total_words": 450,
      "num_segments": 10,
      "percentage": 45.2,
      "segments": [...]
    },
    "SPEAKER_01": { ... }
  },
  "timeline": [
    {
      "start": 0.0,
      "end": 3.5,
      "duration": 3.5,
      "speaker": "SPEAKER_00",
      "text": "Merhaba, bugün sizlere...",
      "confidence": 0.95
    },
    ...
  ],
  "full_transcript": "Tam metin..."
}
```

**Tasarım Kalitesi:**
- ✅ **Akıllı eşleştirme**: Overlap mantığı ile robust birleştirme
- ✅ **Edge case handling**: Örtüşme yoksa fallback
- ✅ **Kapsamlı istatistikler**: Konuşmacı bazlı detaylı analiz
- ✅ **Çoklu format**: JSON ve Text export
- ✅ **Türkçe desteği**: ensure_ascii=False ile karakter korunumu
- ✅ **Metadata**: İşlem bilgileri, model bilgileri

---

## 4. Veri Akışı ve Mimari

### 4.1. Genel İş Akışı (Pipeline)

```
┌─────────────────┐
│  Video Dosyası  │
│    (MP4, AVI)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   1. VIDEO PROCESSOR            │
│   video_processor.py            │
├─────────────────────────────────┤
│  • Ses çıkarma (extract_audio)  │
│  • WAV formatına dönüştürme     │
│  • 16kHz, Mono ayarlama         │
└────────┬────────────────────────┘
         │
         ▼
    ┌────────┐
    │ WAV    │
    │ Dosyası│
    └───┬────┘
        │
        ├───────────────────────┬────────────────────────┐
        │                       │                        │
        ▼                       ▼                        │
┌──────────────────┐    ┌──────────────────┐           │
│  2A. TRANSCRIBER │    │  2B. DIARIZER    │           │
│  transcriber.py  │    │  diarizer.py     │           │
├──────────────────┤    ├──────────────────┤           │
│ • Whisper model  │    │ • pyannote model │           │
│ • Ses → Metin    │    │ • Konuşmacı ayır │           │
│ • Zaman damgası  │    │ • Zaman damgası  │           │
└────────┬─────────┘    └────────┬─────────┘           │
         │                       │                      │
         │                       │                      │
         ▼                       ▼                      │
   ┌──────────┐          ┌──────────────┐              │
   │Transcript│          │  Diarization │              │
   │  Result  │          │    Result    │              │
   └─────┬────┘          └──────┬───────┘              │
         │                      │                       │
         └──────────┬───────────┘                       │
                    ▼                                   │
         ┌───────────────────────┐                     │
         │ 3. OUTPUT FORMATTER   │                     │
         │ output_formatter.py   │                     │
         ├───────────────────────┤                     │
         │ • Sonuçları birleştir │                     │
         │ • Overlap hesapla     │                     │
         │ • İstatistik oluştur  │                     │
         └──────────┬────────────┘                     │
                    │                                   │
                    ▼                                   │
         ┌─────────────────────┐                       │
         │   Final Result      │                       │
         │   (JSON + Text)     │                       │
         └──────────┬──────────┘                       │
                    │                                   │
              ┌─────┴─────┐                            │
              │           │                             │
              ▼           ▼                             │
         ┌────────┐  ┌────────┐                        │
         │  JSON  │  │  TXT   │                        │
         │ output │  │ output │                        │
         └────────┘  └────────┘                        │
                                                        │
                                                        ▼
                                               ┌────────────────┐
                                               │ 4. WEB UI      │
                                               │ (Gelecek)      │
                                               │ Streamlit      │
                                               └────────────────┘
```

### 4.2. Paralel İşlem Fırsatı

**Mevcut Durum:**
```python
# Sıralı işlem (sequential)
audio = extract_audio(video)
transcription = transcriber.transcribe(audio)  # 3 dakika
diarization = diarizer.diarize(audio)          # 2 dakika
# Toplam: 5 dakika
```

**İyileştirme (Threading/Multiprocessing):**
```python
# Paralel işlem
import concurrent.futures

audio = extract_audio(video)

with concurrent.futures.ThreadPoolExecutor() as executor:
    future_trans = executor.submit(transcriber.transcribe, audio)
    future_diar = executor.submit(diarizer.diarize, audio)

    transcription = future_trans.result()  # 3 dakika
    diarization = future_diar.result()     # 3 dakika (paralel)
# Toplam: 3 dakika (max(3, 2))
```

**Performans Kazancı:** %40

### 4.3. Mimari Prensipler

#### Separation of Concerns (SoC)

| Modül | Sorumluluk | Bağımlılık |
|-------|-----------|-----------|
| video_processor | Sadece video/ses işleme | moviepy, FFmpeg |
| transcriber | Sadece ses→metin | Whisper |
| diarizer | Sadece konuşmacı ayırma | pyannote |
| output_formatter | Sadece formatlama | json, datetime |
| settings | Sadece konfigürasyon | dotenv, os |

**Avantajları:**
- ✅ Bir modül değiştiğinde diğerleri etkilenmiyor
- ✅ Test edilebilirlik yüksek
- ✅ Kod tekrarı minimal

#### Single Responsibility Principle (SRP)

**Örnek: video_processor.py**
- ✅ `extract_audio_from_video()`: Sadece ses çıkarma
- ✅ `get_audio_duration()`: Sadece süre hesaplama
- ✅ `validate_video_file()`: Sadece validasyon

**Kötü Tasarım Olsaydı:**
```python
# ❌ Kötü: Her şeyi yapan dev fonksiyon
def process_video_and_transcribe_and_save(video_path):
    # Ses çıkar
    # Metne çevir
    # Konuşmacı ayır
    # Kaydet
    # ...
```

#### Dependency Injection

**Örnek:**
```python
class Transcriber:
    def __init__(self, model_size=None, language=None):
        # settings'ten değil, parametre olarak alıyor
        self.model_size = model_size or settings.WHISPER_MODEL_SIZE
```

**Avantaj:** Test sırasında farklı değerler inject edebilirsiniz:
```python
# Production
transcriber = Transcriber()  # settings'ten alır

# Test
transcriber = Transcriber(model_size="tiny", language="en")
```

#### Error Handling Stratejisi

**Katmanlı Hata Yönetimi:**

1. **Validation Layer (En Dışta):**
```python
def validate_video_file(video_path):
    if not video_path.exists():
        raise FileNotFoundError(...)
    if not is_supported_format():
        raise ValueError(...)
```

2. **Processing Layer (İçeride):**
```python
def extract_audio(video_path):
    try:
        video = VideoFileClip(...)
        audio.write_audiofile(...)
    except Exception as e:
        logger.error(...)
        # Temizlik
        if output_path.exists():
            output_path.unlink()
        raise  # Hatayı yukarı fırlat
```

3. **User Layer (En Dışta - CLI/Web):**
```python
try:
    result = process_video(video_path)
except FileNotFoundError as e:
    print(f"Video bulunamadı: {e}")
except ValueError as e:
    print(f"Geçersiz format: {e}")
except Exception as e:
    print(f"Beklenmeyen hata: {e}")
```

**Prensip:** Low-level modüller hata fırlatır, high-level modüller yakalar ve kullanıcıya bildirir.

---

## 5. Kullanılan Teknolojiler

### 5.1. Ana Kütüphaneler

#### Video/Ses İşleme

**1. moviepy (v1.x)**
- **Kullanım:** Video dosyalarından ses çıkarma
- **Backend:** FFmpeg (arka planda)
- **Avantajları:**
  - ✅ Pythonic API
  - ✅ Çok sayıda format desteği
  - ✅ Ses işleme parametrelerine kolay erişim
- **Dezavantajları:**
  - ⚠️ Büyük videolarda yavaş olabilir
  - ⚠️ Bellek kullanımı yüksek

**Alternatif:**
```python
# Direkt FFmpeg kullanımı (daha hızlı ama low-level)
import subprocess
subprocess.run([
    "ffmpeg", "-i", "video.mp4",
    "-vn", "-acodec", "pcm_s16le",
    "-ar", "16000", "-ac", "1", "audio.wav"
])
```

**2. pydub**
- **Kullanım:** Ses formatı dönüşümleri (şu an aktif kullanılmıyor)
- **Potansiyel kullanım:** MP3 → WAV, ses normalizasyonu

#### AI/ML Modelleri

**3. openai-whisper**
- **Versiyon:** En son (GitHub'dan)
- **Model Mimarisi:** Transformer (Encoder-Decoder)
- **Eğitim Verisi:** 680,000 saat çok dilli veri
- **Dil Desteği:** 99 dil (Türkçe dahil)
- **Lisans:** MIT (Ücretsiz, ticari kullanım OK)

**Özellikler:**
- ✅ Offline çalışır (internet gerekmez)
- ✅ Yüksek doğruluk (özellikle medium/large)
- ✅ Zaman damgalı çıktı (word-level)
- ✅ Dil otomatik algılama
- ⚠️ GPU olmadan yavaş (medium model ~5-10x realtime)

**4. pyannote.audio**
- **Versiyon:** 3.1 (En son)
- **Model:** Speaker diarization pipeline
- **Lisans:** MIT
- **Token:** Hugging Face (ücretsiz)

**Pipeline Bileşenleri:**
1. **Segmentation:** Ses aktivitesi tespit (VAD - Voice Activity Detection)
2. **Embedding:** Her segment için konuşmacı embedding'i çıkar
3. **Clustering:** Embedding'leri grupla (aynı konuşmacılar)
4. **Resegmentation:** Kesin sınırları belirle

**Performans:**
- ✅ State-of-the-art doğruluk (DER ~5-10%)
- ✅ Dil-bağımsız
- ⚠️ GPU öneriliyor (CPU'da 5-8x yavaş)

**5. torch & torchaudio**
- **Kullanım:** pyannote ve Whisper için backend
- **CPU vs GPU:**
  - CPU: Her sistemde çalışır
  - GPU: NVIDIA CUDA gerektirir (5-10x hızlı)

**GPU Kurulumu:**
```bash
# Windows, CUDA 11.8
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# macOS (MPS - Metal)
pip install torch torchaudio
```

#### Web Arayüzü (Gelecek)

**6. streamlit**
- **Kullanım:** Web UI (henüz implement edilmedi)
- **Avantajları:**
  - ✅ Hızlı prototyping
  - ✅ Python-only (HTML/CSS/JS bilgisi gerekmez)
  - ✅ Otomatik reactivity

**Planlanan Özellikler:**
- Drag & drop video upload
- Real-time progress tracking
- JSON/TXT indirme
- Konuşmacı renklendirme
- İstatistik grafikleri

#### Yardımcı Kütüphaneler

**7. loguru**
- **Kullanım:** Gelişmiş logging
- **Özellikler:**
  - ✅ Kolay syntax: `logger.info()`, `logger.error()`
  - ✅ Renkli konsol çıktısı
  - ✅ Otomatik log rotation
  - ✅ Exception tracking

**Örnek:**
```python
from loguru import logger

logger.add(
    "logs/app_{time}.log",
    rotation="1 day",    # Her gün yeni dosya
    retention="7 days",  # 7 günden eski logları sil
    level="INFO"
)

logger.info("İşlem başladı")
logger.success("Başarılı!")
logger.error("Hata oluştu!")
```

**8. python-dotenv**
- **Kullanım:** .env dosyasından environment variables okuma
- **Güvenlik:** Token'ları kodda saklamaktan kaçınma

**9. tqdm**
- **Kullanım:** İlerleme çubukları
- **Örnek:**
```python
from tqdm import tqdm
for i in tqdm(range(100), desc="İşleniyor"):
    # İşlem
```

**10. numpy & pandas**
- **Kullanım:** Veri analizi (şu an pasif)
- **Potansiyel:** İstatistiksel analizler, grafik oluşturma

### 5.2. Sistem Gereksinimleri

**Minimum:**
- Python 3.8+
- 4 GB RAM
- 5 GB disk (modeller için)
- FFmpeg kurulu

**Önerilen:**
- Python 3.10+
- 8-16 GB RAM
- NVIDIA GPU (CUDA destekli) - 4GB+ VRAM
- SSD

**Platform Desteği:**
- ✅ Windows 10/11
- ✅ macOS (M1/M2 MPS desteği)
- ✅ Linux (Ubuntu, Debian, etc.)

---

## 6. Konfigürasyon Sistemi

### 6.1. Environment Variables (.env)

**Dosya Yapısı:**
```bash
# .env (GİT'E EKLENMEMELİ!)
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx
WHISPER_MODEL=small
LANGUAGE=tr
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
```

**Yönetim:**
```python
# settings.py
from dotenv import load_dotenv
import os

load_dotenv()  # .env dosyasını yükle

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
```

**Güvenlik:**
- ✅ `.env` dosyası `.gitignore`'da
- ✅ `.env.example` şablon olarak sunuluyor
- ✅ Token'lar asla kod içinde hardcoded değil

### 6.2. Klasör Yapısı Yönetimi

**Otomatik Oluşturma:**
```python
# settings.py
for directory in [UPLOAD_DIR, OUTPUT_DIR, MODEL_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)
```

**exist_ok=True Önemi:**
- Klasör varsa hata vermiyor
- Klasör yoksa oluşturuyor
- İdempotent (her çalıştırmada güvenli)

### 6.3. Konfigürasyon Best Practices

**✅ İyi Uygulamalar:**
1. Merkezi settings.py dosyası
2. Environment variables için .env
3. Default değerler her zaman var
4. Path'ler pathlib.Path ile
5. Tüm ayarlar UPPERCASE (konvansiyon)

**❌ Kötü Uygulamalar:**
1. ~~Hardcoded paths~~ → pathlib.Path kullan
2. ~~Token'ları kod içinde~~ → .env'de tut
3. ~~Magic numbers~~ → Sabitler tanımla
4. ~~Her modülde ayrı config~~ → Merkezi yönetim

---

## 7. Güvenlik ve Best Practices

### 7.1. Güvenlik Önlemleri

#### Token Yönetimi

**✅ Güvenli:**
```python
# .env
HUGGINGFACE_TOKEN=hf_xxxxx

# .gitignore
.env
.env.local

# settings.py
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
```

**❌ GÜVENSİZ:**
```python
# ❌ Asla yapma!
HUGGINGFACE_TOKEN = "hf_xxxxxxxxxxxxx"  # Hardcoded
```

#### Dosya Yükleme Güvenliği

**Validasyon Kontrolleri:**
```python
def validate_video_file(video_path):
    # 1. Dosya var mı?
    if not video_path.exists():
        raise FileNotFoundError()

    # 2. Desteklenen format mı?
    if video_path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
        raise ValueError("Desteklenmeyen format")

    # 3. Boyut limiti
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError("Dosya çok büyük")

    # 4. MIME type kontrolü (opsiyonel, gelecek)
    # import magic
    # mime = magic.from_file(str(video_path), mime=True)
    # if mime not in ALLOWED_MIMES:
    #     raise ValueError("Geçersiz dosya tipi")
```

**DoS (Denial of Service) Koruması:**
- ✅ MAX_FILE_SIZE_MB limiti (500 MB)
- ⏳ Rate limiting (web UI'da eklenecek)
- ⏳ Timeout mekanizması (uzun işlemler için)

#### Geçici Dosya Yönetimi

**Temizlik:**
```python
try:
    audio = extract_audio(video)
    result = process(audio)
finally:
    # settings.TEMP_FILE_CLEANUP = True ise
    if settings.TEMP_FILE_CLEANUP and audio.exists():
        audio.unlink()
```

### 7.2. Code Quality Best Practices

#### Type Hints

**✅ İyi:**
```python
from pathlib import Path
from typing import Union, Dict, List

def extract_audio(
    video_path: Union[str, Path],
    output_path: Union[str, Path] = None
) -> Path:
    ...
```

**Avantajları:**
- IDE autocomplete
- Statik tip kontrolü (mypy)
- Dokümantasyon olarak

#### Docstrings

**Format:** Google Style

```python
def extract_audio_from_video(
    video_path: Union[str, Path],
    output_path: Union[str, Path] = None
) -> Path:
    """
    Video dosyasından ses çıkarır ve WAV formatında kaydeder.

    Args:
        video_path: Video dosyasının yolu (str veya Path)
            Örnek: "video.mp4" veya Path("videos/sample.mp4")

        output_path: Çıktı ses dosyasının yolu (opsiyonel)
            Verilmezse otomatik oluşturulur
            Örnek: "audio.wav"

    Returns:
        Path: Oluşturulan ses dosyasının yolu

    Raises:
        FileNotFoundError: Video dosyası bulunamazsa
        Exception: Video işleme hatası

    Örnek Kullanım:
        >>> audio_path = extract_audio_from_video("video.mp4")
        >>> print(audio_path)
        Path('uploads/video_audio.wav')
    """
```

#### Logging Seviyeleri

**Kullanım:**
```python
logger.debug("Video yükleniyor...")       # Geliştirme sırasında
logger.info("Video işleniyor: video.mp4") # Normal işlem akışı
logger.success("Ses başarıyla çıkarıldı") # Başarılı işlem
logger.warning("CPU kullanılıyor...")     # Uyarı (hata değil)
logger.error("Video işleme hatası: ...")  # Hata (işlem devam eder)
logger.critical("Sistem hatası!")         # Kritik (uygulama durabilir)
```

#### Exception Handling

**Principle:** Fail fast, fail loudly

```python
# ✅ İyi: Spesifik exception'lar
try:
    video = VideoFileClip(video_path)
except FileNotFoundError:
    logger.error("Dosya bulunamadı")
    raise
except PermissionError:
    logger.error("Dosya erişim izni yok")
    raise
except Exception as e:
    logger.error(f"Beklenmeyen hata: {e}")
    raise

# ❌ Kötü: Sessizce geç
try:
    video = VideoFileClip(video_path)
except:
    pass  # Hata yutuldu, debug zor!
```

#### Resource Management

**Context Managers:**
```python
# ✅ İyi: Otomatik temizlik
with open(file_path, 'r') as f:
    data = f.read()
# Dosya otomatik kapanır

# ❌ Kötü: Manuel
f = open(file_path, 'r')
data = f.read()
f.close()  # Unutulabilir!
```

**Video/Audio Cleanup:**
```python
video = VideoFileClip(video_path)
audio = video.audio
try:
    audio.write_audiofile(output_path)
finally:
    audio.close()
    video.close()  # Her durumda kapat
```

### 7.3. Performance Best Practices

#### Lazy Loading

**✅ İyi:**
```python
class Transcriber:
    def __init__(self):
        self.model = None  # Henüz yüklenmedi

    def load_model(self):
        if self.model is None:  # İlk kullanımda yükle
            self.model = whisper.load_model(...)
```

**Avantaj:** Model kullanılmayacaksa bellekte yer kaplamıyor.

#### Caching

**Model Caching:**
```python
# Whisper modelleri otomatik cache'leniyor
# İlk çalıştırma: Model indirilir (~2 dakika)
# Sonraki: Cache'den yüklenir (~5 saniye)

# Cache lokasyonu:
# Windows: C:\Users\USERNAME\.cache\whisper\
# Linux/Mac: ~/.cache/whisper/
```

#### Memory Management

**Büyük dosyalar için:**
```python
# ❌ Kötü: Tüm dosya belleğe
data = open("huge_file.wav", "rb").read()  # OOM riski

# ✅ İyi: Chunk'lar halinde
with open("huge_file.wav", "rb") as f:
    while chunk := f.read(8192):
        process(chunk)
```

---

## 8. Eksik Bileşenler ve Sonraki Adımlar

### 8.1. Tamamlanmış Bileşenler ✅

1. **✅ Video İşleme Modülü** (video_processor.py)
   - Ses extraction
   - Format dönüşümü
   - Validasyon

2. **✅ Speech-to-Text Modülü** (transcriber.py)
   - Whisper entegrasyonu
   - Güven skoru hesaplama
   - Çoklu dil desteği

3. **✅ Speaker Diarization Modülü** (diarizer.py)
   - pyannote entegrasyonu
   - İstatistik hesaplama
   - GPU/CPU desteği

4. **✅ Output Formatter** (output_formatter.py)
   - Overlap mantığı
   - JSON/Text export
   - İstatistik raporlama

5. **✅ Konfigürasyon Sistemi** (settings.py)
   - Environment variables
   - Klasör yönetimi
   - Default ayarlar

### 8.2. Eksik/Tamamlanmamış Bileşenler ⏳

#### 1. Ana CLI Programı (v_to_t.py)

**Mevcut Durum:**
```python
# Sadece iskelet kod
def main():
    print("Video-to-Text Dönüştürücü")
    print("Proje kurulum aşamasında...")
```

**Olması Gereken:**
```python
import argparse
from app.video_processor import extract_audio_from_video
from app.transcriber import Transcriber
from app.diarizer import SpeakerDiarizer
from app.output_formatter import OutputFormatter

def main():
    parser = argparse.ArgumentParser(
        description='Video-to-Text Dönüştürücü'
    )
    parser.add_argument('video', help='Video dosyası yolu')
    parser.add_argument('--model', default='small',
                       choices=['tiny', 'small', 'medium', 'large'])
    parser.add_argument('--language', default='tr')
    parser.add_argument('--num-speakers', type=int,
                       help='Konuşmacı sayısı (opsiyonel)')
    parser.add_argument('--output', help='Çıktı dosyası yolu')

    args = parser.parse_args()

    # 1. Ses çıkar
    audio = extract_audio_from_video(args.video)

    # 2. Transcribe et
    transcriber = Transcriber(model_size=args.model,
                             language=args.language)
    transcription = transcriber.transcribe(audio)

    # 3. Diarize et
    diarizer = SpeakerDiarizer()
    diarization = diarizer.diarize(audio,
                                   num_speakers=args.num_speakers)

    # 4. Birleştir
    result = OutputFormatter.merge_results(
        transcription, diarization,
        video_name=args.video
    )

    # 5. Kaydet
    output_path = args.output or "output.json"
    OutputFormatter.save_to_json(result, output_path)

    print(f"✅ İşlem tamamlandı: {output_path}")

if __name__ == "__main__":
    main()
```

**Kullanım:**
```bash
python v_to_t.py video.mp4 --model small --language tr --num-speakers 2
```

#### 2. Web Arayüzü (app/web_interface.py)

**Hiç oluşturulmamış.**

**Planlanan Özellikler:**

```python
# app/web_interface.py
import streamlit as st
from pathlib import Path
import tempfile

st.set_page_config(page_title="Video-to-Text", layout="wide")

st.title("🎥 Video-to-Text Dönüştürücü")

# Dosya yükleme
uploaded_file = st.file_uploader(
    "Video dosyası yükleyin",
    type=['mp4', 'avi', 'mov', 'mkv']
)

col1, col2 = st.columns(2)
with col1:
    model_size = st.selectbox("Model Boyutu",
                              ['tiny', 'small', 'medium', 'large'])
with col2:
    language = st.selectbox("Dil", ['tr', 'en'])

num_speakers = st.number_input("Konuşmacı Sayısı (opsiyonel)",
                                min_value=0, max_value=10, value=0)

if st.button("🚀 Dönüştür"):
    if uploaded_file:
        # Geçici dosya kaydet
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix='.mp4') as tmp:
            tmp.write(uploaded_file.read())
            video_path = tmp.name

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # İşlem
        status_text.text("1/4: Ses çıkarılıyor...")
        progress_bar.progress(25)
        audio = extract_audio_from_video(video_path)

        status_text.text("2/4: Konuşma metne çevriliyor...")
        progress_bar.progress(50)
        transcriber = Transcriber(model_size=model_size,
                                 language=language)
        transcription = transcriber.transcribe(audio)

        status_text.text("3/4: Konuşmacılar ayırılıyor...")
        progress_bar.progress(75)
        diarizer = SpeakerDiarizer()
        diarization = diarizer.diarize(audio,
                                      num_speakers=num_speakers or None)

        status_text.text("4/4: Sonuç hazırlanıyor...")
        progress_bar.progress(90)
        result = OutputFormatter.merge_results(
            transcription, diarization,
            video_name=uploaded_file.name
        )

        progress_bar.progress(100)
        status_text.text("✅ Tamamlandı!")

        # Sonuç göster
        st.success(f"İşlem başarılı! {len(result['speakers'])} konuşmacı tespit edildi.")

        # Timeline
        st.subheader("Zaman Çizelgesi")
        for seg in result['timeline'][:10]:  # İlk 10
            with st.expander(
                f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['speaker']}"
            ):
                st.write(seg['text'])
                st.caption(f"Güven: {seg['confidence']:.0%}")

        # İstatistikler
        st.subheader("Konuşmacı İstatistikleri")
        for speaker, stats in result['speakers'].items():
            col1, col2, col3 = st.columns(3)
            col1.metric(speaker, f"{stats['total_duration']:.1f}s")
            col2.metric("Kelime", stats['total_words'])
            col3.metric("Yüzde", f"%{stats['percentage']}")

        # İndirme
        st.subheader("İndir")
        col1, col2 = st.columns(2)

        with col1:
            json_str = json.dumps(result, ensure_ascii=False, indent=2)
            st.download_button(
                "📥 JSON İndir",
                data=json_str,
                file_name="sonuc.json",
                mime="application/json"
            )

        with col2:
            # Text export
            txt_path = Path(tempfile.mktemp(suffix='.txt'))
            OutputFormatter.export_to_text(result, txt_path)
            with open(txt_path, 'r', encoding='utf-8') as f:
                txt_content = f.read()
            st.download_button(
                "📥 Text İndir",
                data=txt_content,
                file_name="sonuc.txt",
                mime="text/plain"
            )
```

**Çalıştırma:**
```bash
streamlit run app/web_interface.py
```

#### 3. Logging Sistemi

**Eksik:**
- Merkezi logging konfigürasyonu
- Log rotation
- Log seviyeleri ayarı

**Eklenmeli:**

```python
# app/logger.py
from loguru import logger
import sys
from config import settings

# Konsol handler
logger.remove()  # Default'u kaldır
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True
)

# Dosya handler
logger.add(
    settings.LOG_DIR / "app_{time}.log",
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    level=settings.LOG_LEVEL,
    encoding="utf-8"
)

# Error log (sadece hatalar)
logger.add(
    settings.LOG_DIR / "errors_{time}.log",
    rotation=settings.LOG_ROTATION,
    retention="30 days",
    level="ERROR",
    encoding="utf-8"
)
```

**Kullanım:**
```python
# Her modülde
from app.logger import logger

logger.info("İşlem başladı")
```

#### 4. Test Suite

**Hiç test yok!**

**Eklenmeli:**

```python
# tests/test_video_processor.py
import pytest
from pathlib import Path
from app.video_processor import extract_audio_from_video

def test_extract_audio_success():
    video_path = Path("tests/fixtures/sample.mp4")
    audio_path = extract_audio_from_video(video_path)

    assert audio_path.exists()
    assert audio_path.suffix == ".wav"

def test_extract_audio_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_audio_from_video("nonexistent.mp4")

def test_validate_video_file():
    from app.video_processor import validate_video_file

    # Geçerli format
    assert validate_video_file("test.mp4") == True

    # Geçersiz format
    with pytest.raises(ValueError):
        validate_video_file("test.txt")
```

**Test Komutları:**
```bash
# Tüm testler
pytest

# Coverage raporu
pytest --cov=app --cov-report=html

# Tek test
pytest tests/test_video_processor.py::test_extract_audio_success
```

#### 5. Performans İyileştirmeleri

**Paralel İşleme:**
```python
# utils/parallel_processor.py
import concurrent.futures

def process_video_parallel(video_path):
    audio = extract_audio(video_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Paralel çalıştır
        future_trans = executor.submit(transcribe, audio)
        future_diar = executor.submit(diarize, audio)

        transcription = future_trans.result()
        diarization = future_diar.result()

    return merge_results(transcription, diarization)
```

**Batch Processing:**
```python
def process_multiple_videos(video_paths):
    results = []
    for video in video_paths:
        result = process_video(video)
        results.append(result)
    return results
```

#### 6. Dokümantasyon

**Eksikler:**
- ⏳ API dokümantasyonu (Sphinx)
- ⏳ Kullanım örnekleri
- ⏳ Deployment rehberi
- ⏳ Troubleshooting guide

### 8.3. Öncelikli To-Do Listesi

**Faz 3: CLI ve Web UI (Şu an öncelik)**

1. **v_to_t.py CLI implement** (2-3 saat)
   - argparse entegrasyonu
   - Progress indicator
   - Error handling

2. **web_interface.py Streamlit UI** (4-6 saat)
   - Dosya upload
   - Progress tracking
   - Sonuç görüntüleme
   - İndirme butonları

3. **Merkezi logging sistemi** (1-2 saat)
   - app/logger.py oluşturma
   - Tüm modüllerde kullanım

**Faz 4: Test ve Kalite (Sonrası)**

4. **Test suite** (8-10 saat)
   - Unit tests
   - Integration tests
   - Fixtures oluşturma

5. **Dokümantasyon** (4-6 saat)
   - Sphinx setup
   - API docs
   - Kullanım kılavuzu

**Faz 5: İyileştirmeler (Opsiyonel)**

6. **Performans optimizasyonu**
   - Paralel işleme
   - Caching stratejileri
   - Memory optimization

7. **Deployment**
   - Docker containerization
   - Requirements freeze
   - Production config

---

## 9. Sonuç ve Değerlendirme

### 9.1. Proje Güçlü Yönleri

1. **✅ Temiz Mimari**
   - Separation of Concerns
   - Single Responsibility
   - Modüler tasarım

2. **✅ İyi Dokümantasyon**
   - Detaylı docstrings
   - Kod içi yorumlar (Türkçe)
   - README.md

3. **✅ Modern Teknolojiler**
   - State-of-the-art AI modelleri (Whisper, pyannote)
   - Type hints
   - Loguru logging
   - pathlib kullanımı

4. **✅ Güvenlik Bilinci**
   - Token'lar .env'de
   - Dosya validasyonu
   - Boyut limitleri

5. **✅ Error Handling**
   - Try-except blokları
   - Resource cleanup
   - Meaningful error messages

### 9.2. İyileştirilebilir Alanlar

1. **⚠️ Test Coverage**
   - Hiç test yok
   - CI/CD pipeline yok

2. **⚠️ Performans**
   - Paralel işleme yok
   - Batch processing yok
   - Progress tracking kısıtlı

3. **⚠️ Kullanılabilirlik**
   - CLI henüz minimal
   - Web UI yok
   - Hata mesajları geliştirilebilir

4. **⚠️ Deployment**
   - Docker yok
   - Production config yok
   - Monitoring/logging merkezi değil

### 9.3. Kod Kalitesi Metrikleri

| Metrik | Değer | Durum |
|--------|-------|-------|
| Toplam Satır | ~1,543 | ✅ Orta boyut |
| Docstring Coverage | ~90% | ✅ Çok iyi |
| Type Hints | ~80% | ✅ İyi |
| Test Coverage | 0% | ❌ Yok |
| Cyclomatic Complexity | Düşük-Orta | ✅ Basit |
| Code Duplication | Minimal | ✅ DRY |
| Comment Ratio | Yüksek | ✅ Eğitici |

### 9.4. Tavsiyeler

**Geliştiriciler İçin:**

1. **Öncelik 1:** CLI ve Web UI'yi tamamlayın (kullanılabilir hale getirin)
2. **Öncelik 2:** Test suite ekleyin (güvenilirlik)
3. **Öncelik 3:** Performans optimizasyonu (kullanıcı deneyimi)

**Yeni Başlayanlar İçin:**

1. README.md'yi okuyun
2. requirements.txt'i kurun
3. .env.example → .env yapın
4. Her modülün `if __name__ == "__main__"` bölümünü çalıştırın (test)
5. Kod yorumlarını okuyun (eğitici)

**Katkıda Bulunacaklar İçin:**

1. Fork + feature branch yapın
2. Test yazın (pytest)
3. Docstring ekleyin (Google style)
4. Type hints kullanın
5. Loguru ile loglayın
6. Pull request gönderin

---

## 10. Kaynaklar ve Referanslar

### Kullanılan Kütüphaneler

- **Whisper:** https://github.com/openai/whisper
- **pyannote.audio:** https://github.com/pyannote/pyannote-audio
- **moviepy:** https://zulko.github.io/moviepy/
- **streamlit:** https://streamlit.io/
- **loguru:** https://github.com/Delgan/loguru

### Faydalı Dökümanlar

- Whisper model kartı: https://huggingface.co/openai/whisper-large-v3
- pyannote kullanım: https://huggingface.co/pyannote/speaker-diarization-3.1
- FFmpeg komutları: https://ffmpeg.org/documentation.html

### Benzer Projeler

- WhisperX: https://github.com/m-bain/whisperX
- Faster Whisper: https://github.com/guillaumekln/faster-whisper

---

**Analiz Tamamlandı!**
**Toplam Dosya Sayısı:** 10 Python dosyası
**Toplam Satır:** ~1,543 satır kod
**Analiz Zamanı:** 30 Kasım 2025
**Versiyon:** Faz 2 (Core Modules Complete)
