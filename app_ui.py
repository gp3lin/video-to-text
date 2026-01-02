"""
Video Mülakat Transkripsiyon - Web UI
======================================
Streamlit tabanlı basit arayüz
"""

import streamlit as st
from pathlib import Path
import time
from v_to_t import process_video
import json

# Sayfa yapılandırması
st.set_page_config(
    page_title="Video Mülakat Transkripsiyon",
    page_icon="🎥",
    layout="wide"
)

# CSS ile özel stil
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<h1 class="main-header">🎥 Video Mülakat Transkripsiyon</h1>', unsafe_allow_html=True)

# Sidebar - Ayarlar
st.sidebar.header("⚙️ Ayarlar")

# Model seçimi
model_size = st.sidebar.selectbox(
    "Whisper Model Boyutu",
    ["large-v3-turbo", "medium", "small", "base", "tiny"],
    index=0,
    help="large-v3-turbo: En iyi doğruluk/hız dengesi (önerilen)"
)

# Dil seçimi
language = st.sidebar.selectbox(
    "Dil",
    [("Otomatik", None), ("Türkçe", "tr"), ("İngilizce", "en")],
    format_func=lambda x: x[0],
    index=1
)[1]

# Konuşmacı sayısı
num_speakers = st.sidebar.number_input(
    "Konuşmacı Sayısı",
    min_value=0,
    max_value=10,
    value=0,
    help="0 = otomatik tespit"
)

# Text export
export_text = st.sidebar.checkbox("Text dosyası oluştur", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Desteklenen Formatlar:**
- Video: MP4, AVI, MOV, MKV, WEBM
- Questions: TXT (her satırda bir soru)
""")

# Ana içerik
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📹 Video Yükle")
    video_file = st.file_uploader(
        "Video dosyanızı seçin",
        type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
        help="Mülakat veya toplantı videosu"
    )

with col2:
    st.header("📝 Sorular (Opsiyonel)")
    questions_option = st.radio(
        "Soru girişi",
        ["Yok", "Dosya Yükle", "Manuel Gir"]
    )

questions_text = None
questions_file = None

if questions_option == "Dosya Yükle":
    questions_file = st.file_uploader(
        "questions.txt dosyası",
        type=['txt'],
        help="Her satırda bir soru"
    )
    if questions_file:
        questions_text = questions_file.read().decode('utf-8')
        st.text_area("Sorular (Önizleme)", questions_text, height=150, disabled=True)

elif questions_option == "Manuel Gir":
    questions_text = st.text_area(
        "Soruları girin (her satırda bir soru)",
        height=150,
        placeholder="Kendinizden bahseder misiniz?\nNeden bu pozisyonda çalışmak istiyorsunuz?\nEn büyük başarınız nedir?"
    )

# İşlem butonu
st.markdown("---")

if st.button("🚀 İşleme Başla", type="primary", use_container_width=True):
    if not video_file:
        st.error("❌ Lütfen bir video dosyası yükleyin!")
    else:
        # Video'yu geçici olarak kaydet
        video_path = Path("uploads") / video_file.name
        video_path.parent.mkdir(exist_ok=True)

        with open(video_path, "wb") as f:
            f.write(video_file.read())

        # Questions dosyası varsa kaydet
        questions_path = None
        if questions_text and questions_text.strip():
            questions_path = Path("uploads/questions_temp.txt")
            with open(questions_path, "w", encoding="utf-8") as f:
                f.write(questions_text.strip())

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # İşlemi başlat
            status_text.text("⏳ Video işleniyor...")
            progress_bar.progress(10)

            output_path = Path("outputs") / f"{video_path.stem}_output.json"

            result = process_video(
                video_path=video_path,
                model_size=model_size,
                language=language,
                num_speakers=num_speakers if num_speakers > 0 else None,
                output_path=output_path,
                export_text=export_text,
                questions_path=questions_path
            )

            progress_bar.progress(100)
            status_text.empty()

            # Başarı mesajı
            st.success("✅ İşlem başarıyla tamamlandı!")

            # Sonuçlar
            st.markdown("---")
            st.header("📊 Sonuçlar")

            # İstatistikler
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Konuşmacı", result['num_speakers'])
            with col2:
                st.metric("Segment", result['num_segments'])
            with col3:
                duration = result['result']['metadata']['duration_seconds']
                st.metric("Süre", f"{int(duration)}s")
            with col4:
                st.metric("İşlem Süresi", f"{int(result['elapsed_time'])}s")

            # Dosya indirmeleri
            st.markdown("### 📥 İndirmeler")

            download_col1, download_col2, download_col3, download_col4 = st.columns(4)

            # JSON dosyası
            with download_col1:
                with open(result['json_path'], 'r', encoding='utf-8') as f:
                    json_data = f.read()
                st.download_button(
                    label="📄 JSON İndir",
                    data=json_data,
                    file_name=f"{video_path.stem}_output.json",
                    mime="application/json"
                )

            # Text dosyası
            if result.get('text_path'):
                with download_col2:
                    with open(result['text_path'], 'r', encoding='utf-8') as f:
                        text_data = f.read()
                    st.download_button(
                        label="📝 Text İndir",
                        data=text_data,
                        file_name=f"{video_path.stem}_output.txt",
                        mime="text/plain"
                    )

            # QA JSON dosyası
            if result.get('qa_json_path'):
                with download_col3:
                    with open(result['qa_json_path'], 'r', encoding='utf-8') as f:
                        qa_json_data = f.read()
                    st.download_button(
                        label="🔍 QA JSON İndir",
                        data=qa_json_data,
                        file_name=f"{video_path.stem}_qa.json",
                        mime="application/json"
                    )

            # QA Markdown dosyası
            if result.get('qa_md_path'):
                with download_col4:
                    with open(result['qa_md_path'], 'r', encoding='utf-8') as f:
                        qa_md_data = f.read()
                    st.download_button(
                        label="📋 QA Rapor İndir",
                        data=qa_md_data,
                        file_name=f"{video_path.stem}_qa.md",
                        mime="text/markdown"
                    )

            # Transkript önizlemesi
            st.markdown("### 📜 Transkript Önizleme")

            preview_tab1, preview_tab2 = st.tabs(["Timeline", "Konuşmacı Bazlı"])

            with preview_tab1:
                # İlk 10 segment
                timeline = result['result']['timeline'][:10]
                for seg in timeline:
                    with st.expander(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['speaker']} (Güven: {seg['confidence']:.0%})"):
                        st.write(seg['text'])

                if len(result['result']['timeline']) > 10:
                    st.info(f"ℹ️ Toplam {len(result['result']['timeline'])} segment. Tümünü görmek için JSON dosyasını indirin.")

            with preview_tab2:
                speakers = result['result']['speakers']
                for speaker, data in speakers.items():
                    st.subheader(f"{speaker}")
                    st.write(f"**Konuşma Süresi:** {data['total_duration']:.1f}s ({data['percentage']:.1f}%)")
                    st.write(f"**Kelime Sayısı:** {data['total_words']}")
                    st.write(f"**Segment Sayısı:** {data['num_segments']}")

            # QA Rapor önizlemesi
            if result.get('qa_md_path'):
                st.markdown("### 🔍 Soru-Cevap Raporu")
                with open(result['qa_md_path'], 'r', encoding='utf-8') as f:
                    qa_md = f.read()
                st.markdown(qa_md)

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Hata oluştu: {str(e)}")
            st.exception(e)

        finally:
            # Geçici dosyaları temizle
            if video_path.exists():
                video_path.unlink()
            if questions_path and questions_path.exists():
                questions_path.unlink()

# Alt bilgi
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Video-to-Text v2.1.0 | Powered by faster-whisper + pyannote.audio</p>
    <p>🚀 <a href="https://github.com/gp3lin/video-to-text" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
