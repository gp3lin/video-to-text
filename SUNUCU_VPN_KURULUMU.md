# Sunucu Kurulumu ve VPN Erişimi - B-LΞXIS

**Son Güncelleme:** 2026-01-09
**Platformlar:** Linux, Windows Server, macOS, Docker
**Erişim:** VPN üzerinden güvenli bağlantı

---

## 🎯 Amaç

B-LΞXIS uygulamasını bir sunucuda çalıştırıp, **sadece VPN üzerinden** erişilebilir hale getirmek.

**Güvenlik:**
- ✅ Sadece VPN bağlantısı ile erişim
- ✅ Internet'ten direkt erişim YOK
- ✅ Kurumsal ağ içinde güvenli

---

## 📋 Platform Seçimi

| Platform | Avantajlar | Dezavantajlar | Önerilen |
|----------|-----------|---------------|----------|
| **Linux (Ubuntu/Debian)** | Hafif, stabil, ücretsiz | Terminal bilgisi gerekli | ⭐⭐⭐⭐⭐ |
| **Docker** | Platform bağımsız, kolay kurulum | Docker bilgisi gerekli | ⭐⭐⭐⭐⭐ |
| **Windows Server** | GUI, tanıdık ortam | Lisans gerekebilir | ⭐⭐⭐ |
| **macOS** | GUI, Unix tabanlı | Pahalı, sunucu kullanımı sınırlı | ⭐⭐ |

**Önerimiz:** Linux (Ubuntu 22.04 LTS) veya Docker

---

## 🚀 Kurulum Adımları

### Platform seçin:
- [Linux (Ubuntu/Debian)](#1-linux-ubuntudebian-kurulumu)
- [Windows Server](#2-windows-server-kurulumu)
- [macOS](#3-macos-kurulumu)
- [Docker](#4-docker-kurulumu-önerilen)

---

## 1. Linux (Ubuntu/Debian) Kurulumu

### 1.1. Sistem Gereksinimleri

```bash
# Sistem bilgisi
uname -a
lsb_release -a

# Minimum: Ubuntu 20.04 LTS, 4GB RAM, 10GB disk
```

### 1.2. Python ve FFmpeg Kurulumu

```bash
# Sistem güncelleme
sudo apt update && sudo apt upgrade -y

# Python 3.10+ kurulum
sudo apt install -y python3 python3-pip python3-venv

# FFmpeg kurulum
sudo apt install -y ffmpeg

# Git kurulum
sudo apt install -y git

# Kontrol
python3 --version  # 3.8+ olmalı
ffmpeg -version
```

### 1.3. Projeyi İndirin

```bash
# Proje dizini oluştur
sudo mkdir -p /opt/blexis
sudo chown $USER:$USER /opt/blexis
cd /opt/blexis

# GitHub'dan klon
git clone https://github.com/gp3lin/video-to-text.git
cd video-to-text

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.4. Streamlit Konfigürasyonu

```bash
mkdir -p ~/.streamlit
nano ~/.streamlit/config.toml
```

**config.toml içeriği:**

```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### 1.5. Systemd Servisi (Otomatik Başlatma)

```bash
sudo nano /etc/systemd/system/blexis.service
```

**blexis.service içeriği:**

```ini
[Unit]
Description=B-LΞXIS Video Transcription Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/opt/blexis/video-to-text
Environment="PATH=/opt/blexis/video-to-text/venv/bin"
ExecStart=/opt/blexis/video-to-text/venv/bin/streamlit run app_ui.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Değiştir:** `your_username` yerine kullanıcı adınızı yazın

**Aktifleştir:**

```bash
# Servisi yeniden yükle
sudo systemctl daemon-reload

# Servisi başlat
sudo systemctl start blexis

# Otomatik başlatma aktif
sudo systemctl enable blexis

# Durumu kontrol et
sudo systemctl status blexis
```

### 1.6. Firewall Ayarları

```bash
# UFW firewall aktif mi?
sudo ufw status

# 8501 portunu sadece yerel ağa aç
sudo ufw allow from 192.168.0.0/16 to any port 8501 proto tcp

# Firewall'u aktif et
sudo ufw enable
```

---

## 2. Windows Server Kurulumu

### 2.1. Sistem Gereksinimleri

- Windows Server 2019/2022
- PowerShell 5.1+
- 4GB RAM, 10GB disk

### 2.2. Python ve FFmpeg Kurulumu

**Chocolatey ile (Önerilen):**

```powershell
# PowerShell'i Admin olarak aç

# Chocolatey kur (yoksa)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Python ve FFmpeg kur
choco install python ffmpeg git -y

# Kontrol
python --version
ffmpeg -version
```

### 2.3. Projeyi İndirin

```powershell
# Proje dizini
cd C:\
mkdir blexis
cd blexis

# Git clone
git clone https://github.com/gp3lin/video-to-text.git
cd video-to-text

# Virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Bağımlılıklar
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4. Windows Servisi Oluşturma

**NSSM (Non-Sucking Service Manager) ile:**

```powershell
# NSSM kur
choco install nssm -y

# Servisi oluştur
nssm install BLEXIS "C:\blexis\video-to-text\venv\Scripts\streamlit.exe" "run" "app_ui.py"

# Çalışma dizini ayarla
nssm set BLEXIS AppDirectory "C:\blexis\video-to-text"

# Servisi başlat
nssm start BLEXIS

# Durumu kontrol et
nssm status BLEXIS
```

### 2.5. Windows Firewall

```powershell
# Firewall kuralı ekle (sadece yerel ağ)
New-NetFirewallRule -DisplayName "BLEXIS-8501" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow -RemoteAddress LocalSubnet
```

---

## 3. macOS Kurulumu

### 3.1. Homebrew ve Gereksinimler

```bash
# Homebrew kur (yoksa)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python, FFmpeg, Git
brew install python3 ffmpeg git
```

### 3.2. Projeyi İndirin

```bash
cd /Applications
git clone https://github.com/gp3lin/video-to-text.git
cd video-to-text

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Bağımlılıklar
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3. LaunchAgent (Otomatik Başlatma)

```bash
nano ~/Library/LaunchAgents/com.blexis.streamlit.plist
```

**com.blexis.streamlit.plist:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.blexis.streamlit</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/video-to-text/venv/bin/streamlit</string>
        <string>run</string>
        <string>/Applications/video-to-text/app_ui.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Applications/video-to-text</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

**Aktifleştir:**

```bash
launchctl load ~/Library/LaunchAgents/com.blexis.streamlit.plist
launchctl start com.blexis.streamlit
```

---

## 4. Docker Kurulumu (ÖNERİLEN)

### 4.1. Dockerfile Oluşturun

```dockerfile
# Dockerfile
FROM python:3.11-slim

# FFmpeg kur
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Outputs klasörü oluştur
RUN mkdir -p outputs uploads logs

# Port
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Streamlit başlat
CMD ["streamlit", "run", "app_ui.py", "--server.address", "0.0.0.0"]
```

### 4.2. docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  blexis:
    build: .
    container_name: blexis
    ports:
      - "8501:8501"
    volumes:
      - ./outputs:/app/outputs
      - ./uploads:/app/uploads
    restart: unless-stopped
    environment:
      - WHISPER_MODEL=large-v3-turbo
      - LANGUAGE=tr
    networks:
      - blexis-network

networks:
  blexis-network:
    driver: bridge
```

### 4.3. Build ve Çalıştırma

```bash
# Docker build
docker-compose build

# Başlat
docker-compose up -d

# Logları görüntüle
docker-compose logs -f

# Durumu kontrol et
docker-compose ps
```

---

## 🌐 VPN Konfigürasyonu (Tüm Platformlar)

### Senaryo 1: Tailscale (ÖNERİLEN) 🌟

**Neden Tailscale?**
- ✅ En kolay kurulum
- ✅ Tüm platformlarda çalışır
- ✅ Otomatik şifreleme
- ✅ Firewall arkasında çalışır
- ✅ Ücretsiz (100 cihaza kadar)

**Sunucuda:**

```bash
# Linux
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# macOS
brew install tailscale
sudo tailscale up

# Windows
# https://tailscale.com/download/windows adresinden indir ve kur
```

**Tailscale IP öğren:**

```bash
tailscale ip -4
# Çıktı: 100.64.0.5
```

**Erişim:**
```
http://100.64.0.5:8501
```

---

### Senaryo 2: WireGuard VPN

**Sunucu kurulumu (Ubuntu):**

```bash
# WireGuard kur
sudo apt install wireguard

# Anahtar oluştur
wg genkey | tee privatekey | wg pubkey > publickey

# Konfigürasyon
sudo nano /etc/wireguard/wg0.conf
```

**wg0.conf:**

```ini
[Interface]
PrivateKey = <sunucu_private_key>
Address = 10.0.0.1/24
ListenPort = 51820

[Peer]
PublicKey = <istemci_public_key>
AllowedIPs = 10.0.0.2/32
```

**Başlat:**

```bash
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0
```

**Erişim:**
```
http://10.0.0.1:8501
```

---

### Senaryo 3: Kurumsal VPN (OpenVPN/Cisco)

Mevcut kurumsal VPN kullanıyorsanız:

1. Sunucunun VPN IP'sini öğrenin
   ```bash
   # Linux/macOS
   ip addr show | grep "10.0"

   # Windows
   ipconfig | findstr "10.0"
   ```

2. Streamlit'i bu IP'de başlatın
   ```bash
   streamlit run app_ui.py --server.address <VPN_IP>
   ```

3. İstemciden erişin
   ```
   http://<VPN_IP>:8501
   ```

---

## 🔒 Güvenlik En İyi Pratikleri

### 1. Port Yönlendirme YAPMAYIN ❌

**ASLA yapılmaması gerekenler:**
```bash
# Router'da port forwarding
# Public IP:8501 → Server:8501
# BU GÜVENLİK AÇIĞI OLUŞTURUR!
```

### 2. Firewall Kuralları

**Linux (UFW):**
```bash
# Sadece VPN IP aralığına izin ver
sudo ufw allow from 10.0.0.0/24 to any port 8501

# veya Tailscale
sudo ufw allow from 100.64.0.0/10 to any port 8501
```

**Windows:**
```powershell
# Sadece özel ağlara izin
New-NetFirewallRule -DisplayName "BLEXIS" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow -Profile Private
```

### 3. HTTPS Aktifleştirme (Opsiyonel)

**Self-signed sertifika:**

```bash
# Sertifika oluştur
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

**Streamlit başlat:**
```bash
streamlit run app_ui.py \
  --server.sslCertFile cert.pem \
  --server.sslKeyFile key.pem
```

**Erişim:**
```
https://<IP>:8501
```

### 4. Basic Authentication (Opsiyonel)

**requirements.txt'ye ekle:**
```
streamlit-authenticator
```

**app_ui.py başına ekle:**
```python
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('.streamlit/credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('Kullanıcı adı/şifre hatalı')
    st.stop()
elif authentication_status == None:
    st.warning('Lütfen giriş yapın')
    st.stop()
```

---

## 🧪 Test ve Doğrulama

### Sunucu Tarafında

**Linux:**
```bash
# Servis çalışıyor mu?
sudo systemctl status blexis

# Port dinliyor mu?
sudo netstat -tulpn | grep 8501

# Yerel erişim
curl http://localhost:8501
```

**Windows:**
```powershell
# Servis çalışıyor mu?
nssm status BLEXIS

# Port dinliyor mu?
netstat -ano | findstr 8501

# Yerel erişim
curl http://localhost:8501
```

**Docker:**
```bash
# Container çalışıyor mu?
docker ps | grep blexis

# Logları görüntüle
docker logs blexis

# Container'a gir
docker exec -it blexis /bin/bash
```

### İstemci Tarafında

```bash
# VPN bağlı mı?
ping <sunucu_vpn_ip>

# Port açık mı?
telnet <sunucu_vpn_ip> 8501

# veya
nc -zv <sunucu_vpn_ip> 8501

# Tarayıcıda test
curl http://<sunucu_vpn_ip>:8501
```

---

## 🐛 Sorun Giderme

### "Connection Refused" Hatası

**Kontroller:**
1. Servis çalışıyor mu?
   ```bash
   # Linux
   sudo systemctl status blexis

   # Windows
   nssm status BLEXIS

   # Docker
   docker ps
   ```

2. Firewall engelliyor mu?
   ```bash
   # Linux
   sudo ufw status

   # Windows
   Get-NetFirewallRule | Where DisplayName -like "*BLEXIS*"
   ```

3. Port doğru mu?
   ```bash
   # Linux
   sudo lsof -i :8501

   # Windows
   netstat -ano | findstr 8501
   ```

### "Timeout" Hatası

**Kontroller:**
1. VPN bağlı mı?
   ```bash
   # Tailscale
   tailscale status

   # WireGuard
   sudo wg show
   ```

2. Routing doğru mu?
   ```bash
   traceroute <sunucu_vpn_ip>
   ```

### Yavaş Çalışma

**Optimizasyonlar:**

1. **Model önbellekleme:**
   ```bash
   # İlk çalıştırmada modeli indir
   python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo')"
   ```

2. **Kaynak limitleri:**
   ```bash
   # Linux - systemd
   sudo nano /etc/systemd/system/blexis.service

   # Ekle:
   [Service]
   MemoryLimit=4G
   CPUQuota=200%
   ```

3. **Docker kaynakları:**
   ```yaml
   # docker-compose.yml
   services:
     blexis:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 4G
   ```

---

## 🔄 Güncelleme ve Bakım

### Git ile Güncelleme

```bash
# Projeye git
cd /opt/blexis/video-to-text  # Linux
cd C:\blexis\video-to-text     # Windows
cd /Applications/video-to-text # macOS

# Güncellemeleri çek
git pull

# Bağımlılıkları güncelle
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate   # Windows
pip install -r requirements.txt --upgrade

# Servisi yeniden başlat
# Linux
sudo systemctl restart blexis

# Windows
nssm restart BLEXIS

# macOS
launchctl stop com.blexis.streamlit
launchctl start com.blexis.streamlit

# Docker
docker-compose down
docker-compose up -d --build
```

### Log Yönetimi

**Linux:**
```bash
# Systemd logları
journalctl -u blexis -f

# Log rotation
sudo nano /etc/logrotate.d/blexis
```

**Docker:**
```bash
# Logları sınırla
docker-compose down
nano docker-compose.yml

# Ekle:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 📊 Performans İzleme

### Linux (htop, netdata)

```bash
# htop kur
sudo apt install htop

# Çalıştır
htop

# Netdata (gelişmiş monitoring)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### Docker Stats

```bash
# Container kaynak kullanımı
docker stats blexis

# Canlı monitoring
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## 📝 Özet Checklist

### Kurulum Tamamlandı mı?

- [ ] Python 3.8+ kurulu
- [ ] FFmpeg kurulu
- [ ] Proje klonlandı
- [ ] Virtual environment oluşturuldu
- [ ] Bağımlılıklar yüklendi
- [ ] Sunucu IP adresi belirlendi
- [ ] Firewall ayarlandı
- [ ] VPN kuruldu ve test edildi
- [ ] Tarayıcıdan erişim başarılı
- [ ] Otomatik başlatma ayarlandı
- [ ] Güvenlik kontrolleri yapıldı

---

## 🎯 Hızlı Başlangıç (Platform Seçimi)

| Kullanım Senaryosu | Önerilen Platform | Önerilen VPN |
|---------------------|-------------------|--------------|
| **Küçük ekip (1-5 kişi)** | Docker + Tailscale | Tailscale |
| **Orta ekip (5-20 kişi)** | Linux + WireGuard | WireGuard |
| **Kurumsal** | Linux/Windows + Kurumsal VPN | Mevcut VPN |
| **Test/Geliştirme** | Docker | Tailscale |
| **Yüksek güvenlik** | Linux + WireGuard + Auth | WireGuard |

---

**Önemli:** VPN olmadan erişim **asla** mümkün olmamalı. Port yönlendirme yapmayın!

---

## 📞 Destek

**Dokümantasyon:**
- README.md - Genel bilgiler
- KURULUM_MAC_TOKENSIZ.md - macOS kurulumu
- Bu dosya - Sunucu VPN kurulumu

**GitHub:**
- Issues: https://github.com/gp3lin/video-to-text/issues
- Discussions: https://github.com/gp3lin/video-to-text/discussions
