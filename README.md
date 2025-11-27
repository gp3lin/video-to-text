# Video-to-Text Dönüştürücü

Video dosyalarından konuşmaları metne çeviren ve konuşmacılara göre ayıran açık kaynak bir Python projesi.

## Özellikler

- **Video'dan Ses Çıkarma**: FFmpeg kullanarak video dosyalarından ses çıkarma
- **Konuşma Tanıma**: OpenAI Whisper ile Türkçe konuşmaları metne çevirme
- **Konuşmacı Ayırma**: pyannote.audio ile hangi kısmı kimin konuştuğunu belirleme
- **Web Arayüzü**: Streamlit ile kolay kullanım
- **JSON Çıktı**: Yapılandırılmış, detaylı sonuç formatı

## Teknolojiler

- **FFmpeg**: Video/ses işleme
- **OpenAI Whisper**: Speech-to-text (offline, ücretsiz)
- **pyannote.audio**: Speaker diarization
- **Streamlit**: Web arayüzü
- **PyTorch**: AI model altyapısı

## Kurulum

### 1. FFmpeg Kurulumu

**Windows:**
1. https://ffmpeg.org/download.html adresinden FFmpeg indir
2. ZIP dosyasını çıkar
3. `bin` klasörünü sistem PATH'ine ekle
4. Terminalde test et: `ffmpeg -version`

**MacOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 2. Python Sanal Ortamı

```bash
# Sanal ortam oluştur
python -m venv venv

# Aktif et (Windows)
venv\Scripts\activate

# Aktif et (MacOS/Linux)
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 3. Hugging Face Token

pyannote.audio kullanmak için ücretsiz Hugging Face token gereklidir:

1. https://huggingface.co/ adresinde hesap oluştur
2. Settings > Access Tokens > New token (Read yetkisiyle)
3. `.env.example` dosyasını `.env` olarak kopyala
4. Token'ı `.env` dosyasına ekle:
```
HUGGINGFACE_TOKEN=your_actual_token_here
```

## Kullanım

### Web Arayüzü (Streamlit)

```bash
streamlit run app/web_interface.py
```

Tarayıcıda açılan arayüzden:
1. Video dosyasını yükle
2. Model boyutunu seç (small/medium/large)
3. "Dönüştür" butonuna tıkla
4. JSON sonucu indir

### Komut Satırı

```bash
python v_to_t.py video.mp4 --model medium --language tr
```

## Proje Yapısı

```
video-to-text/
├── app/                    # Ana uygulama kodu
│   ├── video_processor.py  # Video/ses işleme
│   ├── transcriber.py      # Speech-to-text
│   ├── diarizer.py         # Speaker diarization
│   ├── output_formatter.py # JSON çıktı
│   └── web_interface.py    # Streamlit UI
├── config/                 # Konfigürasyon
├── models/                 # AI modelleri (otomatik indirilir)
├── uploads/                # Yüklenen videolar
├── outputs/                # Üretilen JSON dosyaları
└── logs/                   # Log dosyaları
```

## Çıktı Formatı

```json
{
  "metadata": {
    "video_name": "example.mp4",
    "duration_seconds": 125.5,
    "language": "tr",
    "num_speakers": 2
  },
  "timeline": [
    {
      "start": 0.0,
      "end": 15.5,
      "speaker": "SPEAKER_00",
      "text": "Merhaba, bugün sizlere..."
    }
  ],
  "full_transcript": "Tam metin..."
}
```

## Geliştirme Aşaması

Bu proje şu anda geliştirilme aşamasındadır. İlerleyen bölümlerde:
- [ ] Core modüller (video işleme, transcription, diarization)
- [ ] Web arayüzü
- [ ] Logging sistemi
- [ ] Test coverage

## Katkıda Bulunma

Bu bir öğrenme projesidir. Öneriler ve katkılar memnuniyetle karşılanır!

## Lisans

MIT License

## İletişim

Sorular ve öneriler için Issue açabilirsiniz.
