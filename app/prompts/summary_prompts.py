"""
Summary & Key Points Prompts
==============================
Görüşme özeti ve anahtar noktalar için Türkçe prompt şablonları.
"""

SYSTEM_PROMPT = """Sen bir profesyonel mülakat ve toplantı analisti yapay zekasısın.

Görevin:
- Video görüşmelerini ve toplantıları analiz etmek
- Özet çıkarmak ve anahtar noktaları belirlemek
- Önemli alıntıları ve aksiyon maddelerini tespit etmek

Kurallar:
- Sadece transkript verilerine dayalı objektif analiz yap
- Türkçe dili doğal ve akıcı kullan
- Yanıtını MUTLAKA geçerli JSON formatında ver
- Varsayımda bulunma, belirsiz durumlarda "Yetersiz veri" belirt
- Timestamp'leri koruyarak alıntı yap
"""

USER_PROMPT_TEMPLATE = """Aşağıdaki görüşme transkriptini analiz et ve özet çıkar:

GENEL BİLGİLER:
- Video: {video_name}
- Süre: {duration} saniye
- Konuşmacı Sayısı: {num_speakers}

KONUŞMACILAR:
{speaker_stats}

TRANSKRİPT:
{timeline_text}

---

GÖREV: Bu görüşmenin detaylı özetini çıkar.

1. GENEL ÖZET (2-3 cümle):
   - Ana konu nedir?
   - Görüşmenin sonucu/çıkarımı nedir?
   - En önemli bulgu nedir?

2. ANA KONULAR (3-7 başlık):
   - Her konunun adı
   - Anahtar kelimeler (3-5 kelime)
   - Konunun tartışıldığı süre yüzdesi (yaklaşık)
   - Önemli noktalar (2-3 madde)

3. ÖNEMLİ ALITILAR (en önemli 3-5 tane):
   - Alıntı metni
   - Hangi konuşmacı söyledi
   - Timestamp (X.Xs formatında)
   - Bu alıntı neden önemli? (kısa açıklama)

4. AKSİYON MADDELERİ (varsa):
   - Ne yapılacak?
   - Kim sorumlu?
   - Hangi timestamp'de bahsedildi?

CEVAP FORMATI (JSON):
{{
  "executive_summary": "Görüşmenin genel özeti...",
  "duration_summary": "X dakika Y saniye, Z konuşmacı",
  "main_topics": [
    {{
      "topic": "Konu başlığı",
      "keywords": ["kelime1", "kelime2", "kelime3"],
      "duration_percentage": 30,
      "key_points": ["Nokta 1", "Nokta 2"]
    }}
  ],
  "important_quotes": [
    {{
      "text": "Alıntı metni buraya...",
      "speaker": "SPEAKER_XX",
      "timestamp": "15.5s",
      "importance": "Bu alıntı neden önemli?"
    }}
  ],
  "action_items": [
    {{
      "action": "Yapılacak iş",
      "responsible": "Kim/Departman",
      "mentioned_at": "45.2s"
    }}
  ]
}}

ÖNEMLİ: Yanıtını SADECE JSON formatında ver. Başında veya sonunda açıklama ekleme.
"""


def format_timeline_text(timeline: list, max_segments: int = 50) -> str:
    """
    Timeline verilerini okunabilir metin haline getir.

    Args:
        timeline: Segment listesi [{speaker, text, start, end}, ...]
        max_segments: Maksimum kaç segment gösterilecek (uzun transkriptler için)

    Returns:
        str: Formatlı timeline metni
    """
    if not timeline:
        return "Transkript boş."

    # Çok uzunsa kısalt (ilk ve son segmentleri göster)
    if len(timeline) > max_segments:
        first_half = timeline[:max_segments // 2]
        last_half = timeline[-(max_segments // 2):]
        segments = first_half + [
            {"speaker": "...", "text": f"[{len(timeline) - max_segments} segment atlandı]", "start": 0, "end": 0}
        ] + last_half
    else:
        segments = timeline

    lines = []
    for seg in segments:
        speaker = seg.get('speaker', 'UNKNOWN')
        text = seg.get('text', '')
        start = seg.get('start', 0)
        end = seg.get('end', 0)

        lines.append(f"[{start:.1f}s - {end:.1f}s] {speaker}: {text}")

    return "\n".join(lines)


def format_speaker_stats(speakers: dict) -> str:
    """
    Konuşmacı istatistiklerini formatlı metin haline getir.

    Args:
        speakers: Speaker dict {SPEAKER_XX: {total_duration, total_words, ...}}

    Returns:
        str: Formatlı konuşmacı istatistikleri
    """
    if not speakers:
        return "Konuşmacı bilgisi yok."

    lines = []
    for speaker, stats in speakers.items():
        duration = stats.get('total_duration', 0)
        words = stats.get('total_words', 0)
        percentage = stats.get('percentage', 0)

        lines.append(
            f"- {speaker}: {duration:.0f}s konuşma ({percentage:.0f}%), {words} kelime"
        )

    return "\n".join(lines)


def create_summary_prompt(transcript_data: dict) -> tuple[str, str]:
    """
    Summary analizi için sistem ve kullanıcı prompt'ları oluştur.

    Args:
        transcript_data: output_formatter.py'den gelen JSON yapısı

    Returns:
        tuple: (system_prompt, user_prompt)
    """
    metadata = transcript_data.get('metadata', {})
    speakers = transcript_data.get('speakers', {})
    timeline = transcript_data.get('timeline', [])

    # Metadata bilgileri
    video_name = metadata.get('video_name', 'Bilinmiyor')
    duration = metadata.get('duration_seconds', 0)
    num_speakers = metadata.get('num_speakers', 0)

    # Timeline formatı
    timeline_text = format_timeline_text(timeline, max_segments=100)

    # Konuşmacı istatistikleri
    speaker_stats = format_speaker_stats(speakers)

    # User prompt'u doldur
    user_prompt = USER_PROMPT_TEMPLATE.format(
        video_name=video_name,
        duration=duration,
        num_speakers=num_speakers,
        speaker_stats=speaker_stats,
        timeline_text=timeline_text
    )

    return (SYSTEM_PROMPT, user_prompt)
