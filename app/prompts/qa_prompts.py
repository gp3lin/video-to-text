"""
Q&A Separation Prompts
=======================
Soru-cevap ayırma ve kalite değerlendirme için Türkçe prompt şablonları.
"""

SYSTEM_PROMPT = """Sen bir mülakat soru-cevap analisti yapay zekasısın.

Görevin:
- Görüşmeci ve aday rollerini tespit etmek
- Soruları ve cevapları eşleştirmek
- Cevap kalitesini değerlendirmek

Kurallar:
- Sadece transkript verilerine dayalı objektif analiz yap
- Soru işaretleri ("mı", "mi", "nasıl", "neden") ve konuşma süreleriyle rol belirle
- Yanıtını MUTLAKA geçerli JSON formatında ver
- Cevap kalitesi için somut kriterler kullan
"""

USER_PROMPT_TEMPLATE = """Aşağıdaki görüşme transkriptindeki soruları ve cevapları ayır:

KONUŞMACILAR:
{speaker_stats}

TRANSKRİPT:
{timeline_text}

---

GÖREV: Soru-cevap eşleştirme ve analiz.

1. ROL TESPİTİ:
   - Hangi konuşmacı görüşmeci, hangisi aday?
   - Nasıl anladın? (konuşma süreleri, soru kalıpları, vs.)
   - Güven skoru: 0.0-1.0

2. SORU-CEVAP EŞLEŞTİRMESİ:
   Her soru için:
   - Soru metni
   - Hangi konuşmacı sordu
   - Timestamp
   - Soru tipi: (Açık Uçlu/Teknik/Davranışsal/Genel/Kapanış)

   Cevap:
   - Cevap metni
   - Hangi konuşmacı cevapladı
   - Timestamp ve süre
   - Cevap kalite puanı (1-10)

   Kalite kriterleri:
   - Tamlık (soruyu tam cevapladı mı?): 1-10
   - Netlik (anlaşılır mı?): 1-10
   - Kanıt var mı? (örnek, deneyim anlattı mı?): true/false
   - Uzunluk: Çok Kısa/Optimal/Çok Uzun
   - Güçlü yönler: [liste]
   - Zayıf yönler: [liste]

3. İSTATİSTİKLER:
   - Toplam soru sayısı
   - Ortalama cevap kalitesi
   - Cevaplanmayan sorular (varsa)
   - Ortalama cevap süresi

SORU TESPİT İPUÇLARI:
- Soru işaretçileri: "mı/mi/mu/mü", "nasıl", "neden", "ne", "kim", "nerede", "ne zaman"
- Tipik mülakat soruları:
  * "Kendinizden bahseder misiniz?"
  * "Güçlü yönleriniz nelerdir?"
  * "En zorlandığınız proje?"
  * "Neden bu pozisyonu istiyorsunuz?"

CEVAP FORMATI (JSON):
{{
  "role_identification": {{
    "SPEAKER_00": "Görüşmeci",
    "SPEAKER_01": "Aday",
    "confidence": 0.95,
    "reasoning": "SPEAKER_00 sorular soruyor, SPEAKER_01 uzun cevaplar veriyor"
  }},
  "question_answer_pairs": [
    {{
      "question": {{
        "text": "Kendinizden bahseder misiniz?",
        "speaker": "SPEAKER_00",
        "timestamp": "5.0-7.0s",
        "type": "Genel"
      }},
      "answer": {{
        "text": "Ben 5 yıldır yazılım geliştirici olarak...",
        "speaker": "SPEAKER_01",
        "timestamp": "7.5-25.0s",
        "duration": 17.5,
        "quality": {{
          "completeness": 9,
          "clarity": 8,
          "evidence_provided": true,
          "length_rating": "Optimal",
          "strengths": ["Yapılandırılmış cevap", "Somut örnekler"],
          "weaknesses": ["Biraz uzun olabilir"]
        }}
      }}
    }}
  ],
  "statistics": {{
    "total_questions": 8,
    "avg_answer_quality": 7.5,
    "unanswered_questions": 0,
    "avg_answer_duration": 15.2
  }}
}}

ÖNEMLİ: Yanıtını SADECE JSON formatında ver. Başında veya sonunda açıklama ekleme.
"""


def create_qa_prompt(transcript_data: dict) -> tuple[str, str]:
    """
    Q&A separation analizi için sistem ve kullanıcı prompt'ları oluştur.

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
