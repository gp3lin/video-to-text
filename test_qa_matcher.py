"""
QA Matcher Mock Test
====================
Video olmadan QA matcher'ı test eder.
"""

from pathlib import Path
from app.qa_matcher import QAMatcher

# Mock transcript data (gerçek bir video transkripti gibi)
mock_transcript = {
    "metadata": {
        "video_name": "test_interview.mp4",
        "duration_seconds": 180.0,  # 3 dakika
        "language": "tr",
        "num_speakers": 2,
        "num_segments": 15,
        "processed_at": "2026-01-02T16:00:00"
    },
    "timeline": [
        # İlk 60 saniye - Soru 1: Kendinizden bahseder misiniz?
        {"start": 0.0, "end": 5.0, "speaker": "SPEAKER_00", "text": "Merhaba, kendinizden bahseder misiniz?", "confidence": 0.95},
        {"start": 5.5, "end": 15.0, "speaker": "SPEAKER_01", "text": "Merhaba, ben Ali Yılmaz. 5 yıldır yazılım geliştiriyorum.", "confidence": 0.92},
        {"start": 15.5, "end": 30.0, "speaker": "SPEAKER_01", "text": "Python ve JavaScript ile çalışıyorum. Özellikle backend sistemler konusunda deneyimliyim.", "confidence": 0.94},
        {"start": 30.5, "end": 45.0, "speaker": "SPEAKER_01", "text": "Son 2 yıldır bir fintech şirketinde senior developer olarak görev yapıyorum.", "confidence": 0.93},
        {"start": 45.5, "end": 60.0, "speaker": "SPEAKER_01", "text": "Aynı zamanda açık kaynak projelere katkıda bulunuyorum.", "confidence": 0.91},

        # İkinci 60 saniye - Soru 2: Neden bu pozisyonda çalışmak istiyorsunuz?
        {"start": 60.5, "end": 65.0, "speaker": "SPEAKER_00", "text": "Peki neden bu pozisyonda çalışmak istiyorsunuz?", "confidence": 0.96},
        {"start": 65.5, "end": 80.0, "speaker": "SPEAKER_01", "text": "Bu pozisyonda çalışmak istememin en önemli nedeni şirketinizin AI alanındaki çalışmaları.", "confidence": 0.94},
        {"start": 80.5, "end": 95.0, "speaker": "SPEAKER_01", "text": "Makine öğrenimi konusunda kendimi geliştirmek istiyorum ve burada bu fırsatı görebiliyorum.", "confidence": 0.93},
        {"start": 95.5, "end": 110.0, "speaker": "SPEAKER_01", "text": "Ayrıca ekibinizin yenilikçi projelere açık olması beni çok heyecanlandırıyor.", "confidence": 0.92},
        {"start": 110.5, "end": 120.0, "speaker": "SPEAKER_01", "text": "Daha önce benzer bir projede çalıştım ve bu deneyimimi burada kullanmak istiyorum.", "confidence": 0.91},

        # Üçüncü 60 saniye - Soru 3: En büyük başarınız nedir?
        {"start": 120.5, "end": 125.0, "speaker": "SPEAKER_00", "text": "Harika! En büyük başarınız nedir?", "confidence": 0.95},
        {"start": 125.5, "end": 140.0, "speaker": "SPEAKER_01", "text": "En büyük başarım geçen sene bir ödeme sistemini sıfırdan tasarlayıp hayata geçirmemdi.", "confidence": 0.94},
        {"start": 140.5, "end": 155.0, "speaker": "SPEAKER_01", "text": "Sistem günlük 1 milyon işlemi sorunsuz bir şekilde işleyebiliyor.", "confidence": 0.93},
        {"start": 155.5, "end": 170.0, "speaker": "SPEAKER_01", "text": "Bu proje sayesinde şirket yıllık 500 bin dolar tasarruf etti.", "confidence": 0.92},
        {"start": 170.5, "end": 180.0, "speaker": "SPEAKER_01", "text": "Ayrıca bu sistem için küçük bir ekip kurdum ve 3 junior developer'ı mentorluk ettim.", "confidence": 0.91},
    ],
    "speakers": {
        "SPEAKER_00": {
            "total_duration": 15.0,
            "total_words": 25,
            "num_segments": 3,
            "percentage": 8.3
        },
        "SPEAKER_01": {
            "total_duration": 165.0,
            "total_words": 180,
            "num_segments": 12,
            "percentage": 91.7
        }
    },
    "full_transcript": "Merhaba, kendinizden bahseder misiniz? Merhaba, ben Ali Yılmaz..."
}

def test_qa_matcher():
    """QA Matcher'ı test et."""
    print("="*70)
    print("QA MATCHER MOCK TEST")
    print("="*70)
    print()

    # QA Matcher oluştur
    matcher = QAMatcher()

    # Questions dosyasını yükle
    questions_path = Path("questions.txt")
    print(f"[1/4] Questions yükleniyor: {questions_path}")

    try:
        questions = matcher.load_questions(questions_path)
        print(f"[OK] {len(questions)} soru yuklendi:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
        print()
    except Exception as e:
        print(f"[ERROR] Hata: {e}")
        return

    # QA pairs oluştur
    print(f"[2/4] QA pairs olusturuluyor...")
    print(f"  - Video suresi: {mock_transcript['metadata']['duration_seconds']}s")
    print(f"  - Soru sayisi: {len(questions)}")
    print(f"  - Segment basina: {mock_transcript['metadata']['duration_seconds'] / len(questions):.1f}s")
    print()

    try:
        qa_data = matcher.create_qa_pairs(questions, mock_transcript)
        print(f"[OK] {len(qa_data['qa_pairs'])} QA pair olusturuldu")
        print()
    except Exception as e:
        print(f"[ERROR] Hata: {e}")
        return

    # JSON kaydet
    print(f"[3/4] JSON kaydediliyor...")
    json_path = Path("outputs/test_qa.json")
    json_path.parent.mkdir(exist_ok=True)

    try:
        matcher.save_to_json(qa_data, json_path)
        print(f"[OK] JSON kaydedildi: {json_path}")
        print()
    except Exception as e:
        print(f"[ERROR] Hata: {e}")
        return

    # Markdown kaydet
    print(f"[4/4] Markdown rapor olusturuluyor...")
    md_path = Path("outputs/test_qa.md")

    try:
        matcher.save_to_markdown(qa_data, md_path)
        print(f"[OK] Markdown kaydedildi: {md_path}")
        print()
    except Exception as e:
        print(f"[ERROR] Hata: {e}")
        return

    # Sonuçları göster
    print("="*70)
    print("SONUÇLAR")
    print("="*70)
    print()

    for qa in qa_data['qa_pairs']:
        print(f"SORU {qa['question_number']}: {qa['question']}")
        print(f"  Zaman: {qa['time_segment']['start']:.1f}s - {qa['time_segment']['end']:.1f}s ({qa['time_segment']['duration']:.1f}s)")
        print(f"  Kelime: {qa['answer']['word_count']}, Segment: {qa['answer']['num_segments']}")

        # İlk 100 karakter
        answer_preview = qa['answer']['text'][:100] + "..." if len(qa['answer']['text']) > 100 else qa['answer']['text']
        print(f"  Cevap: {answer_preview}")
        print()

    print("="*70)
    print("[SUCCESS] TEST BASARILI!")
    print("="*70)
    print()
    print("Olusturulan dosyalar:")
    print(f"  - {json_path}")
    print(f"  - {md_path}")
    print()
    print("Dosyalari incelemek icin:")
    print(f"  - cat {md_path}")
    print(f"  - cat {json_path}")
    print()

if __name__ == "__main__":
    test_qa_matcher()
