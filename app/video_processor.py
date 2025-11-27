"""
Video İşleme Modülü
===================
Bu modül video dosyalarından ses çıkarır ve işler.
- Video'dan ses extraction (çıkarma)
- Ses formatını WAV'a çevirme
- Sample rate ve kanal ayarlama (16kHz, mono)
"""

from pathlib import Path
from typing import Union
from loguru import logger
from moviepy.editor import VideoFileClip
import config.settings as settings


def extract_audio_from_video(
    video_path: Union[str, Path],
    output_path: Union[str, Path] = None
) -> Path:
    """
    Video dosyasından ses çıkarır ve WAV formatında kaydeder.

    Args:
        video_path: Video dosyasının yolu (str veya Path)
            Örnek: "video.mp4" veya Path("videos/sample.mp4")

        output_path: Çıktı ses dosyasının yolu (opsiyonel)
            Verilmezse otomatik oluşturulur
            Örnek: "audio.wav"

    Returns:
        Path: Oluşturulan ses dosyasının yolu

    Raises:
        FileNotFoundError: Video dosyası bulunamazsa
        Exception: Video işleme hatası

    Örnek Kullanım:
        >>> audio_path = extract_audio_from_video("video.mp4")
        >>> print(audio_path)
        Path('uploads/video_audio.wav')
    """

    # Path nesnesine çevir (str veya Path olabilir)
    video_path = Path(video_path)

    # Video dosyası var mı kontrol et
    if not video_path.exists():
        error_msg = f"Video dosyası bulunamadı: {video_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    # Çıktı yolu belirtilmemişse otomatik oluştur
    if output_path is None:
        # video_path.stem = dosya adı (uzantısız)
        # Örnek: "video.mp4" -> stem = "video"
        output_filename = f"{video_path.stem}_audio.wav"
        output_path = settings.UPLOAD_DIR / output_filename
    else:
        output_path = Path(output_path)

    logger.info(f"Video işleniyor: {video_path.name}")
    logger.debug(f"Çıktı dosyası: {output_path}")

    try:
        # VideoFileClip: moviepy'ın video yükleme sınıfı
        # Video dosyasını bellege yükler
        logger.debug("Video yükleniyor...")
        video = VideoFileClip(str(video_path))

        # Video'nun ses kanalını al
        audio = video.audio

        if audio is None:
            # Video'da ses yoksa hata ver
            error_msg = f"Video'da ses bulunamadı: {video_path.name}"
            logger.error(error_msg)
            video.close()  # Kaynakları serbest bırak
            raise ValueError(error_msg)

        # Ses dosyasını kaydet
        logger.info("Ses çıkarılıyor ve WAV formatına dönüştürülüyor...")
        audio.write_audiofile(
            str(output_path),
            # fps = frames per second = sample rate
            # 16000 Hz = 16 kHz (konuşma tanıma için optimal)
            fps=settings.AUDIO_SAMPLE_RATE,

            # nbytes = bytes per sample
            # 2 bytes = 16 bit (standart kalite)
            nbytes=2,

            # codec = ses codec'i
            # pcm_s16le = WAV için standart codec
            codec='pcm_s16le',

            # Kanal sayısı: 1=mono, 2=stereo
            # Mono konuşma tanıma için yeterli
            # Not: moviepy'da bu bitwise işlemle yapılıyor
            # 1 = mono, 2 = stereo
            ffmpeg_params=["-ac", str(settings.AUDIO_CHANNELS)],

            # logger=None: moviepy'nin kendi loglarını kapat
            # (çok verbose/detaylı)
            logger=None,

            # verbose=False: İlerleme çubuğunu gösterme
            verbose=False
        )

        # Kaynakları temizle
        # Video ve audio nesneleri bellekte yer kaplar
        audio.close()
        video.close()

        # Dosya boyutunu logla
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        logger.success(
            f"Ses başarıyla çıkarıldı: {output_path.name} "
            f"({file_size_mb:.2f} MB)"
        )

        return output_path

    except Exception as e:
        # Hata durumunda detaylı log
        logger.error(f"Video işleme hatası: {str(e)}")

        # Yarım kalmış dosyayı sil
        if output_path.exists():
            output_path.unlink()  # Dosyayı sil
            logger.debug(f"Yarım kalmış dosya silindi: {output_path}")

        # Hatayı yukarı fırlat (caller'a bildir)
        raise


def get_audio_duration(audio_path: Union[str, Path]) -> float:
    """
    Ses dosyasının süresini saniye cinsinden döndürür.

    Args:
        audio_path: Ses dosyasının yolu

    Returns:
        float: Süre (saniye)

    Örnek:
        >>> duration = get_audio_duration("audio.wav")
        >>> print(f"{duration:.2f} saniye")
        125.50 saniye
    """
    from moviepy.editor import AudioFileClip

    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Ses dosyası bulunamadı: {audio_path}")

    # AudioFileClip: sadece ses dosyaları için
    audio = AudioFileClip(str(audio_path))
    duration = audio.duration  # Saniye cinsinden
    audio.close()

    logger.debug(f"Ses dosyası süresi: {duration:.2f} saniye")
    return duration


def validate_video_file(video_path: Union[str, Path]) -> bool:
    """
    Video dosyasını doğrular.
    - Dosya var mı?
    - Desteklenen format mı?
    - Boyut limiti içinde mi?

    Args:
        video_path: Kontrol edilecek video dosyası

    Returns:
        bool: Geçerli ise True

    Raises:
        FileNotFoundError: Dosya yoksa
        ValueError: Format veya boyut uygun değilse
    """
    video_path = Path(video_path)

    # Dosya var mı?
    if not video_path.exists():
        raise FileNotFoundError(f"Video dosyası bulunamadı: {video_path}")

    # Format destekleniyor mu?
    # .suffix = dosya uzantısı (.mp4, .avi vb.)
    if video_path.suffix.lower() not in settings.SUPPORTED_VIDEO_FORMATS:
        raise ValueError(
            f"Desteklenmeyen format: {video_path.suffix}\n"
            f"Desteklenen formatlar: {settings.SUPPORTED_VIDEO_FORMATS}"
        )

    # Dosya boyutu kontrol et
    file_size_mb = video_path.stat().st_size / (1024 * 1024)

    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise ValueError(
            f"Dosya çok büyük: {file_size_mb:.2f} MB\n"
            f"Maksimum boyut: {settings.MAX_FILE_SIZE_MB} MB"
        )

    logger.info(
        f"Video doğrulandı: {video_path.name} "
        f"({file_size_mb:.2f} MB, {video_path.suffix})"
    )

    return True


# Test için (dosya direkt çalıştırılırsa)
if __name__ == "__main__":
    # Loguru konfigürasyonu
    logger.add(
        "logs/video_processor_{time}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG"
    )

    # Test
    print("Video Processor Modülü")
    print("Test için bir video dosyası yolu girin:")
    test_video = input("Video path: ")

    if test_video:
        try:
            validate_video_file(test_video)
            audio_path = extract_audio_from_video(test_video)
            duration = get_audio_duration(audio_path)
            print(f"\n✅ Başarılı!")
            print(f"Ses dosyası: {audio_path}")
            print(f"Süre: {duration:.2f} saniye")
        except Exception as e:
            print(f"\n❌ Hata: {e}")
