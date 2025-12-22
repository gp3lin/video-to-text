#!/usr/bin/env python3
"""
Video-to-Text Dönüştürücü - CLI Arayüzü
==========================================
Video dosyalarından konuşmaları metne çevirir ve konuşmacılara göre ayırır.

Kullanım:
    python v_to_t.py video.mp4
    python v_to_t.py video.mp4 --model medium --language tr --num-speakers 2
    python v_to_t.py video.mp4 --output sonuc.json
"""

import argparse
import sys
from pathlib import Path
from loguru import logger
import time

# Proje modüllerini import et
from app.video_processor import (
    extract_audio_from_video,
    validate_video_file,
    get_audio_duration
)
from app.transcriber import Transcriber
from app.diarizer import SpeakerDiarizer
from app.output_formatter import OutputFormatter
import config.settings as settings


def setup_logging(verbose: bool = False):
    """
    Logging sistemini kur.

    Args:
        verbose: Detaylı log çıktısı (DEBUG seviyesi)
    """
    # Mevcut handler'ları kaldır
    logger.remove()

    # Konsol handler
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # Dosya handler (her zaman DEBUG)
    logger.add(
        settings.LOG_DIR / "v_to_t_{time}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        encoding="utf-8"
    )


def print_banner():
    """Hoş geldin banner'ı göster."""
    banner = """
================================================================
                  VIDEO-TO-TEXT DONUSTURUCU

  Video -> Ses -> Metin -> Konusmaci Analizi
================================================================
    """
    print(banner)


def print_progress(step: int, total: int, message: str):
    """
    İlerleme göstergesi yazdır.

    Args:
        step: Mevcut adım (1-4)
        total: Toplam adım sayısı
        message: İlerleme mesajı
    """
    bar_length = 40
    filled = int(bar_length * step / total)
    bar = "#" * filled + "-" * (bar_length - filled)
    percentage = int(100 * step / total)

    print(f"\r[{bar}] {percentage}% - {message}", end="", flush=True)
    if step == total:
        print()  # Yeni satır


def format_duration(seconds: float) -> str:
    """
    Saniyeyi okunabilir formata çevir.

    Args:
        seconds: Saniye cinsinden süre

    Returns:
        str: "2m 30s" formatında
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)

    if minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def process_video(
    video_path: Path,
    model_size: str,
    language: str,
    num_speakers: int = None,
    output_path: Path = None,
    export_text: bool = True,
    analyze: bool = False,
    ai_model: str = 'qwen3:4b',
    analyses: list = None
) -> dict:
    """
    Video dosyasını işle (ana pipeline).

    Args:
        video_path: Video dosyası yolu
        model_size: Whisper model boyutu
        language: Dil kodu (tr, en)
        num_speakers: Konuşmacı sayısı (opsiyonel)
        output_path: Çıktı JSON dosyası yolu
        export_text: Text dosyası da oluştur mu?
        analyze: AI analizi yap mı? (Faz 3)
        ai_model: Ollama model adı (Faz 3)
        analyses: Hangi analizler yapılacak (Faz 3)

    Returns:
        dict: İşlem sonucu

    Raises:
        Exception: İşlem hatası
    """
    total_steps = 5 if analyze else 4
    start_time = time.time()

    # ADIM 1: Video Validasyonu ve Ses Çıkarma
    print_progress(0, total_steps, "Video validasyonu yapılıyor...")
    logger.info(f"Video işleniyor: {video_path.name}")

    validate_video_file(video_path)

    print_progress(1, total_steps, "Ses çıkarılıyor...")
    audio_path = extract_audio_from_video(video_path)
    audio_duration = get_audio_duration(audio_path)
    logger.info(f"Ses süresi: {format_duration(audio_duration)}")

    # ADIM 2: Konuşma Tanıma (Speech-to-Text)
    print_progress(2, total_steps, f"Konuşma metne çevriliyor ({model_size} model - faster-whisper)...")
    logger.info(f"faster-whisper {model_size} model yükleniyor...")

    # faster-whisper ile optimized transcription
    # Dil parametresi: None ise otomatik algılama, "tr" ise Türkçe
    # Müzikli videolar için dil belirtmek daha iyi sonuç verir
    transcriber = Transcriber(
        model_size=model_size,
        language=language if language else "tr",  # Varsayılan: Türkçe
        device=settings.WHISPER_DEVICE,
        compute_type=settings.WHISPER_COMPUTE_TYPE
    )
    transcriber.load_model()

    logger.info("Transcription başlıyor (optimized parameters)...")
    # Optimize edilmiş parametreler:
    # - beam_size=5: Daha iyi doğruluk (varsayılan 1'den yüksek)
    # - temperature=0.0: Deterministic, tutarlı sonuçlar
    # - vad_filter=False: MÜZİKLİ videolar için VAD kapalı (yoksa şarkı sözlerini filtreler)
    #   NOT: Sadece konuşma olan videolar için vad_filter=True kullanın
    transcription = transcriber.transcribe(
        audio_path,
        beam_size=5,
        temperature=0.0,
        vad_filter=False  # Müzikli videolar için KAPALI
    )

    word_count = len(transcription['text'].split())
    logger.success(f"Transcription tamamlandı: {word_count} kelime")

    # ADIM 3: Konuşmacı Ayırma (Speaker Diarization)
    print_progress(3, total_steps, "Konuşmacılar ayırılıyor (gelişmiş parametrelerle)...")
    logger.info("Speaker diarization başlıyor (optimized parameters)...")

    diarizer = SpeakerDiarizer()
    diarizer.load_model()

    # Gelişmiş diarization parametreleri:
    # - min_duration=0.5: Çok kısa segment'leri filtrele (gürültü azaltma) ✅ ÇALIŞIYOR
    # - Segment birleştirme: Yakın segment'leri birleştir (max_gap=0.5s) ✅ ÇALIŞIYOR
    #
    # NOT: Diğer parametreler (onset, offset, clustering vb.) pyannote 3.1 tarafından
    # apply() metodunda desteklenmiyor. Bu parametreler pipeline instantiation
    # sırasında ayarlanmalı (gelecek güncellemede eklenecek).
    diarization = diarizer.diarize(
        audio_path,
        num_speakers=num_speakers if num_speakers > 0 else None,
        min_duration=0.5  # Minimum segment süresi (gürültü filtreleme)
        # Diğer parametreler şimdilik kullanılmıyor (pyannote 3.1 limitasyonu)
    )

    # İstatistik
    speakers = set(seg['speaker'] for seg in diarization)
    logger.success(f"Diarization tamamlandı: {len(speakers)} konuşmacı tespit edildi")

    # ADIM 4: Sonuçları Birleştir ve Kaydet
    print_progress(4, total_steps, "Sonuçlar birleştiriliyor ve kaydediliyor...")
    logger.info("Sonuçlar birleştiriliyor...")

    result = OutputFormatter.merge_results(
        transcription,
        diarization,
        video_name=video_path.name,
        additional_metadata={
            "model_size": model_size,
            "language": language,
            "audio_duration": round(audio_duration, 2)
        }
    )

    # ADIM 5: AI Analizi (Opsiyonel - Faz 3)
    if analyze:
        print_progress(5, total_steps, "AI analizi yapiliyor (Ollama)...")
        logger.info("AI analizi basliyor...")

        try:
            from app.analyzer import InterviewAnalyzer

            # Analyzer oluştur
            analyzer = InterviewAnalyzer(
                model_name=ai_model,
                temperature=0.3,
                enabled_analyses=analyses if analyses else ['evaluation', 'summary', 'sentiment', 'qa']
            )

            # Hangi analizler çalışacak?
            if 'all' in analyses:
                analyses_to_run = ['evaluation', 'summary', 'sentiment', 'qa']
            else:
                analyses_to_run = analyses

            logger.info(f"Analizler: {', '.join(analyses_to_run)}")

            # Analizi çalıştır
            analysis_result = analyzer.analyze(result, analysis_types=analyses_to_run)

            # Sonucu result'a ekle
            result['analysis'] = analysis_result

            logger.success(f"AI analizi tamamlandi: {analysis_result['metadata']['status']}")

            # Markdown rapor oluştur
            try:
                from app.report_generator import ReportGenerator

                report_path = output_path.with_suffix('.md') if output_path else settings.OUTPUT_DIR / f"{video_path.stem}_report.md"
                ReportGenerator.create_report(result, report_path)
                logger.success(f"Markdown rapor olusturuldu: {report_path}")

            except Exception as rep_error:
                logger.error(f"Rapor olusturulamadi: {rep_error}")

        except Exception as e:
            logger.error(f"AI analizi basarisiz: {e}")
            logger.warning("Analiz olmadan devam ediliyor...")
            # Analiz başarısız olsa bile devam et

    # JSON kaydet
    if output_path is None:
        output_path = settings.OUTPUT_DIR / f"{video_path.stem}_output.json"

    json_path = OutputFormatter.save_to_json(result, output_path, pretty=True)

    # Text export
    text_path = None
    if export_text:
        text_path = output_path.with_suffix('.txt')
        OutputFormatter.export_to_text(result, text_path)

    # Geçici ses dosyasını temizle
    if settings.TEMP_FILE_CLEANUP and audio_path.exists():
        audio_path.unlink()
        logger.debug(f"Geçici dosya silindi: {audio_path}")

    # Süre hesapla
    elapsed_time = time.time() - start_time

    return {
        "success": True,
        "json_path": json_path,
        "text_path": text_path,
        "num_speakers": len(result['speakers']),
        "num_segments": len(result['timeline']),
        "elapsed_time": elapsed_time,
        "result": result
    }


def print_summary(process_result: dict):
    """
    İşlem özetini ekrana yazdır.

    Args:
        process_result: process_video() fonksiyonundan dönen sonuç
    """
    result = process_result['result']

    print("\n" + "="*70)
    print("[BASARILI] ISLEM TAMAMLANDI")
    print("="*70)

    # Genel bilgiler
    print(f"\nGENEL BILGILER")
    print(f"  • Video: {result['metadata']['video_name']}")
    print(f"  • Süre: {format_duration(result['metadata']['duration_seconds'])}")
    print(f"  • Dil: {result['metadata']['language']}")
    print(f"  • Konuşmacı sayısı: {process_result['num_speakers']}")
    print(f"  • Segment sayısı: {process_result['num_segments']}")
    print(f"  • İşlem süresi: {format_duration(process_result['elapsed_time'])}")

    # Konuşmacı istatistikleri
    print(f"\nKONUSMACI ISTATISTIKLERI")
    for speaker, stats in result['speakers'].items():
        print(f"  • {speaker}:")
        print(f"    - Toplam konuşma: {format_duration(stats['total_duration'])} (%{stats['percentage']})")
        print(f"    - Kelime sayısı: {stats['total_words']}")
        print(f"    - Segment sayısı: {stats['num_segments']}")

    # İlk 3 segment
    print(f"\nILK 3 SEGMENT (Onizleme)")
    for seg in result['timeline'][:3]:
        duration = seg['end'] - seg['start']
        print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['speaker']} ({duration:.1f}s):")
        # Metni kısalt (max 80 karakter)
        text = seg['text'][:77] + "..." if len(seg['text']) > 80 else seg['text']
        print(f"    \"{text}\"")
        print(f"    Güven: {seg['confidence']:.0%}")

    # Çıktı dosyaları
    print(f"\nCIKTI DOSYALARI")
    print(f"  • JSON: {process_result['json_path']}")
    if process_result['text_path']:
        print(f"  • Text: {process_result['text_path']}")

    print("\n" + "="*70)


def main():
    """Ana CLI fonksiyonu."""
    # Argument parser
    parser = argparse.ArgumentParser(
        description='Video-to-Text Dönüştürücü - Video dosyalarından konuşmaları metne çevirir',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s video.mp4
  %(prog)s video.mp4 --model medium --language tr
  %(prog)s video.mp4 --num-speakers 2 --output sonuc.json
  %(prog)s video.mp4 --model large --verbose

Desteklenen formatlar:
  Video: .mp4, .avi, .mov, .mkv, .webm

Model boyutları (faster-whisper):
  tiny          - 39 MB   (en hızlı, düşük doğruluk)
  base          - 74 MB   (hızlı, orta doğruluk)
  small         - 244 MB  (orta hız, iyi doğruluk)
  medium        - 769 MB  (iyi doğruluk)
  large-v3      - 1550 MB (en iyi doğruluk, yavaş)
  large-v3-turbo- 809 MB  (en iyi doğruluk/hız dengesi) [ÖNERİLEN]
        """
    )

    # Pozisyonel argüman
    parser.add_argument(
        'video',
        type=str,
        help='Video dosyası yolu'
    )

    # Opsiyonel argümanlar
    parser.add_argument(
        '--model',
        type=str,
        default='large-v3-turbo',
        choices=['tiny', 'base', 'small', 'medium', 'large-v3', 'large-v3-turbo'],
        help='faster-whisper model boyutu (default: large-v3-turbo)'
    )

    parser.add_argument(
        '--language',
        type=str,
        default=None,
        help='Dil kodu (tr, en, vb.) - Belirtilmezse otomatik algılanır (default: otomatik)'
    )

    parser.add_argument(
        '--num-speakers',
        type=int,
        default=0,
        help='Konuşmacı sayısı (0=otomatik tespit) (default: 0)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Çıktı JSON dosyası yolu (default: outputs/<video>_output.json)'
    )

    parser.add_argument(
        '--no-text',
        action='store_true',
        help='Text dosyası oluşturma (sadece JSON)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Detaylı log çıktısı (DEBUG seviyesi)'
    )

    # AI Analizi argümanları (Faz 3)
    analysis_group = parser.add_argument_group('AI Analizi (Ollama - Opsiyonel)')

    analysis_group.add_argument(
        '--analyze',
        action='store_true',
        help='AI analizi yap (Ollama qwen3:4b gerektirir)'
    )

    analysis_group.add_argument(
        '--ai-model',
        type=str,
        default='qwen3:4b',
        help='Ollama model adı (default: qwen3:4b)'
    )

    analysis_group.add_argument(
        '--analyses',
        nargs='+',
        choices=['all', 'summary', 'sentiment', 'qa', 'evaluation'],
        default=['all'],
        help='Yapılacak analiz tipleri (default: all)'
    )

    analysis_group.add_argument(
        '--skip-analysis',
        nargs='+',
        choices=['summary', 'sentiment', 'qa', 'evaluation'],
        help='Atlanacak analiz tipleri'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0 (Faz 3 - AI Analysis)'
    )

    # Argümanları parse et
    args = parser.parse_args()

    # Logging kur
    setup_logging(verbose=args.verbose)

    # Banner göster
    print_banner()

    # Video yolu kontrolü
    video_path = Path(args.video)
    if not video_path.exists():
        logger.error(f"Video dosyası bulunamadı: {video_path}")
        print(f"[HATA] Video dosyasi bulunamadi: {video_path}")
        sys.exit(1)

    # Output yolu
    output_path = Path(args.output) if args.output else None

    try:
        # Analiz tiplerini belirle
        analyses_to_run = args.analyses
        if args.skip_analysis:
            analyses_to_run = [a for a in analyses_to_run if a not in args.skip_analysis]

        # Video işle
        result = process_video(
            video_path=video_path,
            model_size=args.model,
            language=args.language,
            num_speakers=args.num_speakers,
            output_path=output_path,
            export_text=not args.no_text,
            analyze=args.analyze,
            ai_model=args.ai_model,
            analyses=analyses_to_run
        )

        # Özet göster
        print_summary(result)

        logger.success("İşlem başarıyla tamamlandı!")
        sys.exit(0)

    except FileNotFoundError as e:
        logger.error(f"Dosya bulunamadı: {e}")
        print(f"\n[HATA] Dosya bulunamadi")
        print(f"   {e}")
        sys.exit(1)

    except ValueError as e:
        logger.error(f"Geçersiz değer: {e}")
        print(f"\n[HATA] Gecersiz deger")
        print(f"   {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("İşlem kullanıcı tarafından iptal edildi")
        print(f"\n\n[UYARI] Islem iptal edildi")
        sys.exit(130)

    except Exception as e:
        logger.exception(f"Beklenmeyen hata: {e}")
        print(f"\n[HATA] Beklenmeyen Hata:")
        print(f"   {e}")
        print(f"\n   Detayli log: {settings.LOG_DIR / 'v_to_t_*.log'}")
        sys.exit(1)


if __name__ == "__main__":
    main()
