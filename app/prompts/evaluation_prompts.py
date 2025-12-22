"""
Candidate Evaluation Prompts
==============================
Aday değerlendirmesi için Türkçe prompt şablonları.
"""

SYSTEM_PROMPT = """Sen bir profesyonel mülakat değerlendirme uzmanısın.

Görevin:
- Adayları yetkinlik bazlı değerlendirmek
- Güçlü ve zayıf yönleri objektif belirlemek
- İşe alım önerisi vermek

Kurallar:
- Sadece transkript verilerine dayalı objektif değerlendirme yap
- 1-10 puanlama sistemini tutarlı kullan
- Kanıtlarını transkriptten timestamp'li olarak göster
- Yanıtını MUTLAKA geçerli JSON formatında ver
- Ayrımcılık yapma, sadece profesyonel yetkinlikleri değerlendir
"""

USER_PROMPT_TEMPLATE = """Aşağıdaki mülakat transkriptini değerlendir:

KONUŞMACILAR:
{speaker_stats}

TRANSKRİPT:
{timeline_text}

---

GÖREV: Adayı 5 yetkinlikte değerlendir (1-10 skala).

YETKİNLİKLER:

1. İLETİŞİM BECERİLERİ (1-10)
   - Açık ve anlaşılır ifade ediyor mu?
   - Aktif dinliyor mu?
   - Sorulara yerinde cevap veriyor mu?
   - Örneklerle açıklayabiliyor mu?

2. TEKNİK BİLGİ (1-10)
   - Alan bilgisi derinliği var mı?
   - Doğru terminoloji kullanıyor mu?
   - Problem çözme yaklaşımı sağlam mı?
   - Pratik deneyimlerini aktarabiliyor mu?

3. PROBLEM ÇÖZME (1-10)
   - Analitik düşünebiliyor mu?
   - Yaratıcı çözümler sunuyor mu?
   - Zorlukları nasıl aştığını anlatıyor mu?
   - Öğrenme yeteneği var mı?

4. LİDERLİK & TAKIM ÇALIŞMASI (1-10)
   - Takım deneyimi var mı?
   - İnisiyatif alabiliyor mu?
   - Sorumluluk alıyor mu?
   - Karar verme becerisi nasıl?

5. DUYGUSAL ZEKA (1-10)
   - Öz farkındalığı var mı?
   - Empati kurabiliyor mu?
   - Stres yönetimi nasıl?
   - Profesyonellik seviyesi?

PUANLAMA SİSTEMİ:
- 9-10: Mükemmel - Beklentilerin çok üzerinde
- 7-8: Çok İyi - Güçlü performans
- 5-6: İyi - Yeterli seviye
- 3-4: Geliştirilmeli - Temel eksiklikler
- 1-2: Zayıf - Ciddi gelişim ihtiyacı

Her yetkinlik için:
- Puan (1-10)
- Güçlü yönler (en az 2, en fazla 5)
- Gelişim alanları (en az 1, en fazla 3)
- Kanıtlar (transkriptten örnekler, timestamp ile)

GENEL DEĞERLENDİRME:
- Genel puan (5 yetkinliğin ortalaması)
- En güçlü 3 yön
- Gelişim gereken 2-3 alan
- İşe alım önerisi: Kesinlikle Önerilir/Önerilir/Koşullu Öneri/Önerilmez
- Öneri gerekçesi (2-3 cümle)

CEVAP FORMATI (JSON):
{{
  "overall_score": 7.2,
  "overall_rating": "Çok İyi",
  "competencies": {{
    "communication": {{
      "score": 8,
      "rating": "Çok İyi",
      "strengths": [
        "Açık ve anlaşılır ifade kullanıyor",
        "Somut örneklerle açıklıyor"
      ],
      "weaknesses": [
        "Bazen hızlı konuşuyor"
      ],
      "evidence": [
        "12.5s-15.2s: Deneyimini net bir şekilde açıkladı",
        "25.0s-28.5s: Örnek vererek problem çözme sürecini anlattı"
      ]
    }},
    "technical": {{
      "score": 7,
      "rating": "Çok İyi",
      "strengths": ["..."],
      "weaknesses": ["..."],
      "evidence": ["..."]
    }},
    "problem_solving": {{
      "score": 7,
      "rating": "Çok İyi",
      "strengths": ["..."],
      "weaknesses": ["..."],
      "evidence": ["..."]
    }},
    "leadership": {{
      "score": 6,
      "rating": "İyi",
      "strengths": ["..."],
      "weaknesses": ["..."],
      "evidence": ["..."]
    }},
    "emotional_intelligence": {{
      "score": 8,
      "rating": "Çok İyi",
      "strengths": ["..."],
      "weaknesses": ["..."],
      "evidence": ["..."]
    }}
  }},
  "top_strengths": [
    "İletişim becerileri çok güçlü",
    "Teknik bilgi derinliği var",
    "Duygusal olarak olgun"
  ],
  "improvement_areas": [
    "Liderlik deneyimi sınırlı",
    "Problem çözme örnekleri daha detaylandırılabilir"
  ],
  "hiring_recommendation": "Önerilir",
  "recommendation_reason": "Güçlü teknik profil ve iletişim becerileri var. Liderlik deneyimi geliştirilmeli ancak temel yetkinlikler pozisyon için yeterli."
}}

ÖNEMLİ NOTLAR:
- Eğer transkript çok kısa veya bilgi yetersizse, bunu "evidence" kısmında belirt
- Varsayımda bulunma, sadece transkriptte olanları değerlendir
- Puanları dengeli ver (herkese 9-10 verme)
- Yanıtını SADECE JSON formatında ver

ÖNEMLİ: Yanıtını SADECE JSON formatında ver. Başında veya sonunda açıklama ekleme.
"""


def create_evaluation_prompt(transcript_data: dict) -> tuple[str, str]:
    """
    Candidate evaluation analizi için sistem ve kullanıcı prompt'ları oluştur.

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
