#!/usr/bin/env python3
"""
Model İndirme Script'i
======================
Tüm gerekli AI modellerini önceden indirir.
Offline kullanım için bu script'i çalıştırın.

Kullanım:
    python download_models.py
    python download_models.py --all  # Tüm model boyutlarını indir
"""

import argparse
from pathlib import Path
from loguru import logger
import sys

# Proje modüllerini import et
from app.transcriber import Transcriber
from app.diarizer import SpeakerDiarizer
import config.settings as settings


def setup_logging():
    """Logging kur."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True
    )


def print_banner():
    """Banner göster."""
    banner = """
================================================================
                    MODEL INDIRME ARACI

  Offline kullanim icin AI modellerini onceden indirir
================================================================
    """
    print(banner)


def check_disk_space():
    """Disk alanını kontrol et."""
    import shutil

    total, used, free = shutil.disk_usage(settings.BASE_DIR)
    free_gb = free / (1024**3)

    logger.info(f"Boş disk alanı: {free_gb:.2f} GB")

    if free_gb < 5:
        logger.warning("⚠️  Disk alanı az (5 GB'den az). Modeller indirilemeyebilir.")
        return False

    return True


def download_whisper_model(model_size: str) -> bool:
    """
    Whisper modelini indir.

    Args:
        model_size: Model boyutu (tiny, small, medium, large)

    Returns:
        bool: Başarılı ise True
    """
    model_sizes = {
        'tiny': 39,
        'base': 74,
        'small': 244,
        'medium': 769,
        'large': 1550
    }

    size_mb = model_sizes.get(model_size, 0)

    logger.info("─" * 70)
    logger.info(f"📥 Whisper {model_size} model indiriliyor (~{size_mb} MB)...")
    logger.info("─" * 70)

    try:
        transcriber = Transcriber(model_size=model_size)
        transcriber.load_model()

        # Model dosyasını kontrol et
        model_path = settings.MODEL_DIR / f"{model_size}.pt"
        if model_path.exists():
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            logger.success(f"✅ {model_size} model indirildi: {file_size_mb:.1f} MB")
            return True
        else:
            logger.warning(f"⚠️  Model dosyası bulunamadı: {model_path}")
            return False

    except Exception as e:
        logger.error(f"❌ Hata: {e}")
        return False


def download_pyannote_model() -> bool:
    """
    pyannote.audio modelini indir.

    Returns:
        bool: Başarılı ise True
    """
    logger.info("─" * 70)
    logger.info("📥 pyannote.audio model indiriliyor (~55 MB)...")
    logger.info("─" * 70)

    # Token kontrolü
    if not settings.HUGGINGFACE_TOKEN:
        logger.error("❌ HUGGINGFACE_TOKEN bulunamadı!")
        logger.error("   .env dosyasına token ekleyin:")
        logger.error("   HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx")
        logger.error("")
        logger.error("   Token almak için:")
        logger.error("   1. https://huggingface.co/settings/tokens")
        logger.error("   2. New token → Read yetkisiyle")
        logger.error("   3. Token'ı kopyala → .env'e yapıştır")
        return False

    try:
        diarizer = SpeakerDiarizer()
        diarizer.load_model()

        logger.success("✅ pyannote.audio model indirildi")
        return True

    except Exception as e:
        logger.error(f"❌ Hata: {e}")

        if "401" in str(e) or "authentication" in str(e).lower():
            logger.error("   Token hatası! Token'ınızı kontrol edin.")

        return False


def print_summary(downloaded_models: dict):
    """İndirme özetini göster."""
    print("\n" + "=" * 70)
    print("📊 İNDİRME ÖZETİ")
    print("=" * 70)

    # Whisper modelleri
    print("\n🎤 Whisper Modelleri:")
    for model, success in downloaded_models.items():
        if model.startswith('whisper_'):
            model_name = model.replace('whisper_', '')
            status = "✅ İndirildi" if success else "❌ Başarısız"
            print(f"  • {model_name}: {status}")

    # pyannote
    print("\n👥 Speaker Diarization:")
    pyannote_success = downloaded_models.get('pyannote', False)
    status = "✅ İndirildi" if pyannote_success else "❌ Başarısız"
    print(f"  • pyannote.audio: {status}")

    # Disk kullanımı
    print(f"\n💾 Model Klasörü: {settings.MODEL_DIR}")

    # Klasör boyutu
    total_size = 0
    for file_path in settings.MODEL_DIR.rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size

    total_size_mb = total_size / (1024 * 1024)
    print(f"📦 Toplam Boyut: {total_size_mb:.1f} MB")

    # Başarı oranı
    total = len(downloaded_models)
    successful = sum(downloaded_models.values())
    print(f"\n📈 Başarı Oranı: {successful}/{total} model")

    print("\n" + "=" * 70)

    # Offline kullanım bilgisi
    if successful == total:
        print("\n✅ TÜM MODELLER İNDİRİLDİ!")
        print("   Artık internet olmadan kullanabilirsiniz.")
        print("\n   Kullanım:")
        print("   python v_to_t.py video.mp4")
    else:
        print("\n⚠️  Bazı modeller indirilemedi.")
        print("   İnternet bağlantınızı kontrol edin ve tekrar deneyin.")

    print("")


def main():
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(
        description='AI modellerini önceden indir (offline kullanım için)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s                    # Önerilen modelleri indir (small)
  %(prog)s --all              # Tüm modelleri indir (tiny, small, medium, large)
  %(prog)s --models small medium  # Sadece belirtilen modelleri indir

Not:
  İlk indirmede internet gereklidir. Sonraki kullanımlarda offline çalışır.
        """
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Tüm Whisper modellerini indir (tiny, base, small, medium, large)'
    )

    parser.add_argument(
        '--models',
        nargs='+',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='İndirilecek Whisper model boyutları'
    )

    parser.add_argument(
        '--skip-pyannote',
        action='store_true',
        help='pyannote modelini indirme (sadece Whisper)'
    )

    args = parser.parse_args()

    # Setup
    setup_logging()
    print_banner()

    # Disk kontrolü
    if not check_disk_space():
        logger.warning("Devam etmek istiyor musunuz? (y/n)")
        response = input().lower()
        if response != 'y':
            logger.info("İptal edildi.")
            return

    # İndirilecek modelleri belirle
    if args.all:
        whisper_models = ['tiny', 'base', 'small', 'medium', 'large']
        logger.info("🎯 Mod: TÜM modeller indirilecek")
    elif args.models:
        whisper_models = args.models
        logger.info(f"🎯 Mod: Seçili modeller → {', '.join(whisper_models)}")
    else:
        whisper_models = ['small']  # Default
        logger.info("🎯 Mod: Önerilen model (small)")

    logger.info("")

    # İndirme
    downloaded_models = {}

    # 1. Whisper modelleri
    for model_size in whisper_models:
        success = download_whisper_model(model_size)
        downloaded_models[f'whisper_{model_size}'] = success

    # 2. pyannote modeli
    if not args.skip_pyannote:
        success = download_pyannote_model()
        downloaded_models['pyannote'] = success
    else:
        logger.info("⏭️  pyannote modeli atlanıyor (--skip-pyannote)")

    # Özet
    print_summary(downloaded_models)


if __name__ == "__main__":
    main()
