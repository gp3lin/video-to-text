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
    page_title="B-LΞXIS - Lexical Intelligence System",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile özel stil - B-LΞXIS Lexical Theme (Pink/Purple Cyberpunk)
st.markdown("""
<style>
    /* B-LΞXIS Header - Purple/Pink Gradient */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #9D4EDD 0%, #FF006E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 3px;
        text-shadow: 0 0 30px rgba(157, 78, 221, 0.3);
    }

    .subtitle {
        text-align: center;
        color: #C77DFF;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-style: italic;
        font-weight: 300;
    }

    /* Custom boxes - Purple/Pink Theme */
    .success-box {
        padding: 1rem;
        background: linear-gradient(135deg, #9D4EDD15 0%, #C77DFF15 100%);
        border-left: 4px solid #9D4EDD;
        border-radius: 8px;
        color: #E6EDF3;
    }

    .info-box {
        padding: 1rem;
        background: linear-gradient(135deg, #FF006E15 0%, #FF66B215 100%);
        border-left: 4px solid #FF006E;
        border-radius: 8px;
        color: #E6EDF3;
    }

    .warning-box {
        padding: 1rem;
        background: linear-gradient(135deg, #FB560715 0%, #FF8C0015 100%);
        border-left: 4px solid #FB5607;
        border-radius: 8px;
        color: #E6EDF3;
    }

    /* Glow effect for buttons - Purple/Pink glow */
    .stButton>button {
        box-shadow: 0 0 20px rgba(157, 78, 221, 0.4);
        transition: all 0.3s ease;
        border: 1px solid rgba(157, 78, 221, 0.3);
    }

    .stButton>button:hover {
        box-shadow: 0 0 30px rgba(255, 0, 110, 0.6);
        transform: translateY(-2px);
        border: 1px solid rgba(255, 0, 110, 0.5);
    }

    /* Sidebar styling - Purple accent */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(157, 78, 221, 0.2);
    }

    /* File uploader - Purple border */
    .stFileUploader {
        border: 2px dashed rgba(157, 78, 221, 0.3);
        border-radius: 8px;
        padding: 1rem;
    }

    /* Metric cards - Purple values */
    [data-testid="stMetricValue"] {
        color: #C77DFF;
        font-weight: 600;
    }

    /* Expanders - Purple accent */
    .streamlit-expanderHeader {
        border-left: 3px solid #9D4EDD;
    }
</style>
""", unsafe_allow_html=True)

# Başlık - B-LΞXIS Theme
st.markdown('<h1 class="main-header">🗣️ B-LΞXIS</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">"Lexical Intelligence - Transforming speech into structured knowledge"</p>', unsafe_allow_html=True)

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
            # Eski sonuçları temizle
            if 'result' in st.session_state:
                del st.session_state['result']
            if 'video_path' in st.session_state:
                del st.session_state['video_path']
            if 'questions_path' in st.session_state:
                del st.session_state['questions_path']

            # İşlemi başlat
            status_text.text("⏳ Video işleniyor...")
            progress_bar.progress(10)

            output_path = Path("outputs") / f"{video_path.stem}_output.json"

            result = process_video(
                video_path=video_path,
                model_size=model_size,
                language=language,
                num_speakers=None,  # Otomatik tespit
                output_path=output_path,
                export_text=export_text,
                questions_path=questions_path
            )

            progress_bar.progress(100)
            status_text.empty()

            # Sonuçları session state'e kaydet
            st.session_state['result'] = result
            st.session_state['video_path'] = video_path
            st.session_state['questions_path'] = questions_path

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

# Sonuçları Göster (session_state'ten - download sonrası da kalıcı)
if 'result' in st.session_state:
    result = st.session_state['result']
    saved_video_path = st.session_state.get('video_path')
    saved_questions_path = st.session_state.get('questions_path')

    st.success("✅ Sonuçlar hazır!")

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
            file_name=f"{saved_video_path.stem}_output.json" if saved_video_path else "output.json",
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
                file_name=f"{saved_video_path.stem}_output.txt" if saved_video_path else "output.txt",
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
                file_name=f"{saved_video_path.stem}_qa.json" if saved_video_path else "qa.json",
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
                file_name=f"{saved_video_path.stem}_qa.md" if saved_video_path else "qa.md",
                mime="text/markdown"
            )

    # Önizleme - Her zaman paragraf formatı
    st.markdown("### 📜 Transkript")

    if result.get('qa_md_path'):
        # QA Paragrafları (Soru-Cevap Formatı)
        with open(result['qa_md_path'], 'r', encoding='utf-8') as f:
            qa_md = f.read()
        st.markdown(qa_md)
    else:
        # Konuşmacı Paragrafları
        speakers = result['result']['speakers']

        for speaker, data in speakers.items():
            st.markdown(f"## {speaker}")
            st.markdown(f"**Konuşma Süresi:** {data['total_duration']:.1f}s ({data['percentage']:.1f}%) | **Kelime Sayısı:** {data['total_words']}")
            st.markdown("")

            # Konuşmacının tüm metni paragraf olarak
            speaker_segments = data.get('segments', [])
            if speaker_segments:
                full_text = " ".join(seg['text'] for seg in speaker_segments)
                st.markdown(full_text)
            else:
                st.info("*(Bu konuşmacı için metin bulunamadı)*")

            st.markdown("---")

# Alt bilgi - B-LΞXIS Lexical Theme
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8B949E; padding: 2rem 0;'>
    <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'>
        <strong style='background: linear-gradient(135deg, #9D4EDD 0%, #FF006E 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;'>
            🗣️ B-LΞXIS
        </strong> v2.1.0
    </p>
    <p style='font-size: 0.9rem; margin-bottom: 1rem;'>
        Powered by <span style='color: #9D4EDD;'>faster-whisper</span> +
        <span style='color: #C77DFF;'>pyannote.audio</span> +
        <span style='color: #FF006E;'>Streamlit</span>
    </p>
    <p style='font-size: 0.8rem; color: #C77DFF; margin-top: 1rem;'>
        "Lexical Intelligence - Transforming speech into structured knowledge"
    </p>
</div>
""", unsafe_allow_html=True)
