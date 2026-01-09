# Mac Kurulum Rehberi - Token'sız Mod (Basitleştirilmiş)

**Son Güncelleme:** 2026-01-09
**Mod:** Token'sız (Sadece Transkripsiyon)

---

## 🎯 Bu Kurulum Kiminle İçin?

✅ **Sadece transkripsiyon** (konuşmayı metne çevirme) yapacaksanız
✅ **Konuşmacı ayırma** (kim ne zaman konuştu) gerektirmiyorsa
✅ **Hugging Face hesabı/token** istemiyorsanız
✅ **Kurumsal ortamda** dış hesap kullanılamıyorsa

❌ **Konuşmacı ayırma** gerekiyorsa → Normal kurulum yapın

---

## ⚡ Hızlı Kurulum (Token'sız)

### 1. Homebrew Kur

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Python ve FFmpeg Kur

```bash
brew install python3 ffmpeg git
```

Kontrol:
```bash
python3 --version  # Python 3.8+ olmalı
ffmpeg -version
```

### 3. Projeyi İndir

```bash
cd ~/Desktop
git clone https://github.com/gp3lin/video-to-text.git
cd video-to-text
```

**GitHub bağlantısını kesmek istiyorsanız:**
```bash
rm -rf .git
```

### 4. Virtual Environment Oluştur

```bash
python3 -m venv venv
source venv/bin/activate
```

Terminal başında `(venv)` görmelisiniz.

### 5. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

**Not:** 5-10 dakika sürebilir (~1.1 GB indirme)

---

## 🚀 Çalıştırma

### Web Arayüzü ile (Önerilen)

```bash
streamlit run app_ui.py
```

veya:

```bash
chmod +x run_ui.sh
./run_ui.sh
```

**Web UI açıldığında:**
1. Sol tarafta **"Konuşmacı Ayırma"** kutucuğu **KAPALI** olmalı ❌
2. Video yükleyin
3. "İşleme Başla" butonuna tıklayın

### Komut Satırı ile

```bash
python v_to_t.py video.mp4 --no-diarization
```

**Örnekler:**

```bash
# Basit kullanım (token'sız)
python v_to_t.py mülakat.mp4 --no-diarization

# Türkçe, medium model
python v_to_t.py mülakat.mp4 --no-diarization --model medium --language tr

# Çıktı yolu belirt
python v_to_t.py mülakat.mp4 --no-diarization --output sonuc.json
```

---

## 📊 Çıktı

Token'sız modda:
- ✅ **Tam transkript** (tüm konuşma metne çevrilir)
- ✅ **Zaman damgaları** (hangi saniyede ne söylendi)
- ✅ **Güven skorları** (transcription accuracy)
- ❌ **Konuşmacı ayırma YOK** (tümü "SPEAKER_00" olarak işaretlenir)

**Örnek JSON Çıktısı:**

```json
{
  "metadata": {
    "video_name": "mülakat.mp4",
    "duration_seconds": 180.0,
    "language": "tr",
    "num_speakers": 1,
    "num_segments": 25,
    "model_info": {
      "transcription": "faster-whisper (OpenAI Whisper)",
      "diarization": "Disabled (Token-free mode)"
    }
  },
  "speakers": {
    "SPEAKER_00": {
      "total_duration": 180.0,
      "total_words": 450,
      "percentage": 100.0
    }
  },
  "timeline": [
    {
      "start": 0.0,
      "end": 5.5,
      "speaker": "SPEAKER_00",
      "text": "Merhaba, ben Ali. Yazılım mühendisiyim.",
      "confidence": 0.95
    }
  ]
}
```

---

## ✅ Test Et

Kurulumun düzgün çalıştığını test edin:

```bash
python test_token_free.py
```

**Beklenen çıktı:**
```
TUM TESTLER BASARILI!
Token'siz mod sorunsuz calisiyor.
```

---

## 🔧 Sorun Giderme

### "FFmpeg not found"
```bash
# FFmpeg kurulu mu?
ffmpeg -version

# Yoksa:
brew install ffmpeg

# Terminal'i yeniden başlat
```

### "ModuleNotFoundError"
```bash
# Virtual environment aktif mi?
# Terminal başında (venv) görünmeli

# Aktif değilse:
source venv/bin/activate

# Tekrar yükle:
pip install -r requirements.txt
```

### "pyannote.audio hatası" veya "Hugging Face token"
```bash
# Web UI'da "Konuşmacı Ayırma" KAPALI olmalı
# veya CLI'da --no-diarization flag kullanın

python v_to_t.py video.mp4 --no-diarization
```

### İlk çalıştırmada yavaş
- İlk kullanımda faster-whisper modeli indirilir (~809 MB)
- 10-15 dakika sürebilir
- İnternet bağlantınız stabil olmalı
- Sonraki kullanımlarda hızlıdır

---

## 📦 Disk Alanı Gereksinimi (Token'sız)

| Kategori | Boyut |
|----------|-------|
| Python kütüphaneleri | ~1.1 GB |
| faster-whisper model | ~809 MB |
| Proje dosyaları | ~50 MB |
| **TOPLAM** | **~2 GB** |

**Önerilen boş alan:** 3-4 GB

---

## 🆚 Token'sız vs Normal Mod

| Özellik | Token'sız Mod | Normal Mod |
|---------|---------------|------------|
| **Transkripsiyon** | ✅ Tam | ✅ Tam |
| **Konuşmacı Ayırma** | ❌ Yok | ✅ Var |
| **Hugging Face Token** | ❌ Gerekmez | ✅ Gerekli |
| **Disk Alanı** | ~2 GB | ~3.2 GB |
| **Kurulum Süresi** | 15-20 dk | 30-45 dk |
| **Kullanım** | Basit | Tam özellikli |

---

## 🔄 Sonraki Kullanımlar

Her yeni terminal oturumunda:

```bash
cd ~/Desktop/video-to-text
source venv/bin/activate
streamlit run app_ui.py
```

veya kısayol:

```bash
./run_ui.sh
```

---

## 📝 Notlar

- ✅ **İnternet** sadece ilk kurulumda gerekli
- ✅ **Videolar** yerel bilgisayarda işlenir (internete gönderilmez)
- ✅ **Offline çalışır** (modeller indirildikten sonra)
- ✅ **Kurumsal ortama uygun** (dış hesap gerekmez)

---

## 🚀 Sonraki Adım

Konuşmacı ayırma özelliğine ihtiyacınız olursa:
1. Hugging Face hesabı oluşturun (ücretsiz)
2. Token alın
3. `.env` dosyasına ekleyin
4. Web UI'da "Konuşmacı Ayırma" kutucuğunu aktifleştirin

Detaylı talimatlar: `README.md`

---

**Sorularınız için:** https://github.com/gp3lin/video-to-text/issues
