"""
Sentiment & Tone Analysis Prompts
===================================
Duygu ve ton analizi için Türkçe prompt şablonları.
"""

SYSTEM_PROMPT = """Sen bir duygusal zeka ve ton analizi uzmanısısın.

Görevin:
- Konuşmacıların duygusal durumlarını analiz etmek
- Ton değişimlerini tespit etmek
- Stres göstergelerini belirlemek
- Özgüven seviyesini değerlendirmek

Kurallar:
- Sadece transkript verilerine dayalı objektif analiz yap
- Duygu analizinde nötr ve profesyonel ol
- Yanıtını MUTLAKA geçerli JSON formatında ver
- Aşırı yorum yapma, gözlemleri bildir
"""

USER_PROMPT_TEMPLATE = """Aşağıdaki görüşme transkriptinin duygusal tonunu analiz et:

KONUŞMACILAR:
{speaker_stats}

TRANSKRİPT:
{timeline_text}

---

GÖREV: Duygusal ton ve stres analizi yap.

1. GENEL DUYGU DURUMU:
   - Sentiment: Pozitif/Nötr/Negatif
   - Güven skoru: 0.0-1.0 (ne kadar emin olduğun)
   - Duygusal durum: Sakin/Heyecanlı/Gergin/Stresli
   - Stres seviyesi: Düşük/Orta/Yüksek

2. KONUŞMACI BAZLI ANALİZ (her konuşmacı için):
   - Rol tahmini: Görüşmeci/Aday/Diğer
   - Sentiment: Pozitif/Nötr/Negatif
   - Ton: (örn: Profesyonel, Samimi, Resmi, Rahat, Gergin)
   - Özgüven: Yüksek/Orta/Düşük
   - Stres göstergeleri (varsa):
     * Tereddütler ("ııı", "şey", "yani")
     * Tekrarlar
     * Hızlı konuşma
     * Cümle yarıda kesme
   - Pozitif anlar: [timestamp + açıklama]
   - Negatif anlar: [timestamp + açıklama] (varsa)

3. TON GELİŞİMİ (zaman içinde ton nasıl değişti):
   - Başlangıç (ilk 1/3): Ton nasıldı?
   - Orta (orta 1/3): Ton nasıl değişti?
   - Son (son 1/3): Kapanış tonu nasıl?

STRES GÖSTERGELERİ İÇİN İPUÇLARI:
- Tereddüt kelimeleri: "ııı", "şey", "yani", "işte", "hani"
- Tekrarlar: Aynı cümleyi/kelimeyi tekrar etme
- Eksik cümleler: Cümleyi tamamlamadan geçme
- Hızlı konuşma: Çok fazla kelime kısa sürede

CEVAP FORMATI (JSON):
{{
  "overall": {{
    "sentiment": "Pozitif/Nötr/Negatif",
    "confidence_score": 0.85,
    "emotional_state": "Sakin ve Profesyonel",
    "stress_level": "Düşük/Orta/Yüksek"
  }},
  "per_speaker": {{
    "SPEAKER_00": {{
      "role": "Görüşmeci",
      "sentiment": "Nötr-Pozitif",
      "tone": "Profesyonel, Teşvik Edici",
      "confidence": "Yüksek",
      "stress_indicators": [],
      "positive_moments": ["15.5s: Deneyimi överken pozitif ton"],
      "negative_moments": []
    }},
    "SPEAKER_01": {{
      "role": "Aday",
      "sentiment": "Pozitif",
      "tone": "Hevesli, Kendinden Emin",
      "confidence": "Orta-Yüksek",
      "stress_indicators": [
        "21.0s: Hızlı konuşma (stres göstergesi olabilir)",
        "35.2s: 'ııı' tereddütü"
      ],
      "positive_moments": ["15-20s: Deneyimini anlatırken kendinden emin"],
      "negative_moments": []
    }}
  }},
  "tone_progression": [
    {{"time_range": "0-30s", "tone": "Resmi, Çekingen", "description": "Görüşme başlangıcı"}},
    {{"time_range": "30-60s", "tone": "Rahat, Konuşkan", "description": "Isınma süreci"}},
    {{"time_range": "60-83s", "tone": "Kendinden Emin, Kapanış", "description": "Güvenle sonlandırma"}}
  ]
}}

ÖNEMLİ: Yanıtını SADECE JSON formatında ver. Başında veya sonunda açıklama ekleme.
"""


def create_sentiment_prompt(transcript_data: dict) -> tuple[str, str]:
    """
    Sentiment analizi için sistem ve kullanıcı prompt'ları oluştur.

    Args:
        transcript_data: output_formatter.py'den gelen JSON yapısı

    Returns:
        tuple: (system_prompt, user_prompt)
    """
    from app.prompts.summary_prompts import format_timeline_text, format_speaker_stats

    speakers = transcript_data.get('speakers', {})
    timeline = transcript_data.get('timeline', [])

    # Timeline formatı
    timeline_text = format_timeline_text(timeline, max_segments=100)

    # Konuşmacı istatistikleri
    speaker_stats = format_speaker_stats(speakers)

    # User prompt'u doldur
    user_prompt = USER_PROMPT_TEMPLATE.format(
        speaker_stats=speaker_stats,
        timeline_text=timeline_text
    )

    return (SYSTEM_PROMPT, user_prompt)
