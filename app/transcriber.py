"""
Konuşma Tanıma Modülü (Speech-to-Text)
========================================
Bu modül OpenAI Whisper modelini kullanarak ses dosyalarını metne çevirir.

Whisper Nedir?
--------------
- OpenAI'ın ücretsiz, açık kaynak konuşma tanıma modeli
- 99 dili destekler (Türkçe dahil)
- Offline çalışır (internet gerekmez)
- İlk kullanımda model otomatik indirilir (~500MB)

Model Boyutları:
- tiny: 39MB, en hızlı ama düşük doğruluk
- base: 74MB
- small: 244MB (ÖNERİLEN - iyi denge)
- medium: 769MB (daha iyi doğruluk)
- large: 1550MB (en iyi doğruluk, yavaş)
"""

from pathlib import Path
from typing import Union, Dict, List
from loguru import logger
import whisper
from tqdm import tqdm
import config.settings as settings


class Transcriber:
    """
    Whisper tabanlı konuşma tanıma sınıfı.

    Bu sınıf Whisper modelini yönetir ve transcription işlemlerini yapar.
    Sınıf kullanma nedeni: Model bir kez yüklenir, tekrar tekrar kullanılır.
    """

    def __init__(self, model_size: str = None, language: str = None):
        """
        Transcriber başlatıcı.

        Args:
            model_size: Whisper model boyutu (tiny, small, medium, large)
                Verilmezse settings'ten alınır
            language: Dil kodu (tr, en vb.)
                Verilmezse settings'ten alınır
        """
        # Model boyutu belirtilmemişse settings'ten al
        self.model_size = model_size or settings.WHISPER_MODEL_SIZE
        self.language = language or settings.WHISPER_LANGUAGE

        logger.info(f"Transcriber başlatılıyor: {self.model_size} model, {self.language} dili")

        # Model henüz yüklenmedi
        self.model = None

    def load_model(self):
        """
        Whisper modelini yükler.

        İlk çalıştırmada:
        - Model internet üzerinden indirilir (~/.cache/whisper/)
        - 2-10 dakika sürebilir (model boyutuna göre)

        Sonraki çalıştırmalarda:
        - Model cache'den yüklenir (hızlı)
        """
        if self.model is not None:
            # Model zaten yüklüyse tekrar yükleme
            logger.debug("Model zaten yüklü, tekrar yükleme yapılmıyor")
            return

        logger.info(f"Whisper {self.model_size} model yükleniyor...")
        logger.info("İlk kullanımda model indirilecek, bu 2-10 dakika sürebilir.")

        try:
            # whisper.load_model():
            # - Model boyutunu al (tiny, small, medium, large)
            # - Eğer yoksa indir
            # - Bellege yükle ve model nesnesini döndür
            self.model = whisper.load_model(
                self.model_size,
                # download_root: Modelin kaydedileceği yer
                # Verilmezse ~/.cache/whisper/ kullanılır
                download_root=str(settings.MODEL_DIR)
            )

            logger.success(f"{self.model_size} model başarıyla yüklendi")

        except Exception as e:
            logger.error(f"Model yükleme hatası: {str(e)}")
            raise

    def transcribe(
        self,
        audio_path: Union[str, Path],
        **kwargs
    ) -> Dict:
        """
        Ses dosyasını metne çevirir.

        Args:
            audio_path: Ses dosyasının yolu (.wav, .mp3 vb.)
            **kwargs: Whisper'a geçirilecek ekstra parametreler
                - temperature: 0.0-1.0 (0=deterministic, 1=yaratıcı)
                - beam_size: Arama algoritması beam sayısı
                - best_of: En iyi N sonuçtan seç

        Returns:
            Dict: Transcription sonucu
                {
                    "text": "Tam metin",
                    "segments": [
                        {
                            "start": 0.0,  # Başlangıç (saniye)
                            "end": 3.5,    # Bitiş (saniye)
                            "text": "Merhaba",
                            "confidence": 0.95  # Güven skoru (0-1)
                        },
                        ...
                    ],
                    "language": "tr"  # Algılanan dil
                }

        Raises:
            FileNotFoundError: Ses dosyası bulunamazsa
            Exception: Transcription hatası
        """
        audio_path = Path(audio_path)

        # Dosya var mı?
        if not audio_path.exists():
            error_msg = f"Ses dosyası bulunamadı: {audio_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Model yüklü mü?
        if self.model is None:
            self.load_model()

        logger.info(f"Transcription başlıyor: {audio_path.name}")

        try:
            # model.transcribe() Whisper'ın ana fonksiyonu
            # Ses dosyasını alıp metin döndürür
            result = self.model.transcribe(
                str(audio_path),

                # language: Dil belirtmek doğruluğu artırır
                # None verilirse Whisper dili otomatik algılar
                language=self.language,

                # verbose: İlerleme bilgisi göster
                # False: Sessiz mod
                # True: Her segment'i konsola yaz
                verbose=False,

                # **kwargs: Kullanıcının verdiği ekstra parametreler
                **kwargs
            )

            # Sonuçları işle ve zenginleştir
            processed_result = self._process_result(result)

            # İstatistikler
            total_duration = processed_result["segments"][-1]["end"] if processed_result["segments"] else 0
            word_count = len(processed_result["text"].split())

            logger.success(
                f"Transcription tamamlandı: {word_count} kelime, "
                f"{total_duration:.2f} saniye"
            )

            return processed_result

        except Exception as e:
            logger.error(f"Transcription hatası: {str(e)}")
            raise

    def _process_result(self, raw_result: Dict) -> Dict:
        """
        Whisper'ın ham sonucunu işler ve düzenler.

        Args:
            raw_result: Whisper'dan gelen ham sonuç

        Returns:
            Dict: İşlenmiş ve zenginleştirilmiş sonuç
        """
        # Segment'leri işle
        # Whisper her cümleyi/parçayı ayrı segment olarak döndürür
        processed_segments = []

        for segment in raw_result.get("segments", []):
            processed_segments.append({
                "id": segment.get("id"),  # Segment numarası
                "start": round(segment.get("start", 0), 2),  # Başlangıç (saniye)
                "end": round(segment.get("end", 0), 2),  # Bitiş
                "text": segment.get("text", "").strip(),  # Metin (baştaki/sondaki boşlukları kaldır)

                # Whisper bazı segmentler için güven skoru vermeyebilir
                # avg_logprob: Ortalama log probability (güven göstergesi)
                # no_speech_prob: Sessizlik olasılığı
                "confidence": self._calculate_confidence(segment),
            })

        return {
            "text": raw_result.get("text", "").strip(),  # Tam metin
            "segments": processed_segments,  # Zaman damgalı parçalar
            "language": raw_result.get("language", self.language),  # Algılanan dil
        }

    def _calculate_confidence(self, segment: Dict) -> float:
        """
        Segment için güven skorunu hesaplar.

        Whisper doğrudan confidence vermez, ama avg_logprob'dan
        yaklaşık bir güven skoru hesaplayabiliriz.

        Args:
            segment: Whisper segment'i

        Returns:
            float: 0.0-1.0 arası güven skoru
        """
        # avg_logprob: Log probability ortalaması
        # Negatif değerler (-0.1 ile -3.0 arası)
        # -0.1 -> yüksek güven
        # -3.0 -> düşük güven
        avg_logprob = segment.get("avg_logprob", -1.0)

        # no_speech_prob: Sessizlik olasılığı
        # 0.0 -> kesinlikle konuşma var
        # 1.0 -> kesinlikle sessiz
        no_speech_prob = segment.get("no_speech_prob", 0.0)

        # Basit bir güven skoru hesapla
        # Bu tamamen heuristic (deneysel) bir formül
        if avg_logprob > -0.5:
            base_confidence = 0.95
        elif avg_logprob > -1.0:
            base_confidence = 0.85
        elif avg_logprob > -1.5:
            base_confidence = 0.75
        else:
            base_confidence = 0.65

        # Sessizlik olasılığı yüksekse güveni düşür
        confidence = base_confidence * (1 - no_speech_prob)

        # 0.0-1.0 arasına sınırla
        return max(0.0, min(1.0, round(confidence, 2)))

    def transcribe_with_progress(
        self,
        audio_path: Union[str, Path],
        **kwargs
    ) -> Dict:
        """
        İlerleme çubuğu ile transcription.

        Not: Whisper kendi içinde ilerleme göstermiyor, bu sadece
        başlangıç/bitiş bildirimi için basit bir wrapper.
        """
        with tqdm(total=100, desc="Transcribing") as pbar:
            pbar.update(10)  # Başladı
            result = self.transcribe(audio_path, **kwargs)
            pbar.update(90)  # Bitti
            return result


# Yardımcı fonksiyon: Hızlı kullanım için
def transcribe_audio(
    audio_path: Union[str, Path],
    model_size: str = None,
    language: str = None
) -> Dict:
    """
    Hızlı transcription fonksiyonu.

    Transcriber sınıfını kullanmadan direkt transcription yapar.
    Tek kullanım için uygundur.

    Args:
        audio_path: Ses dosyası
        model_size: Model boyutu (opsiyonel)
        language: Dil (opsiyonel)

    Returns:
        Dict: Transcription sonucu

    Örnek:
        >>> result = transcribe_audio("audio.wav", model_size="small", language="tr")
        >>> print(result["text"])
        "Merhaba, bugün sizlere..."
    """
    transcriber = Transcriber(model_size=model_size, language=language)
    return transcriber.transcribe(audio_path)


# Test için
if __name__ == "__main__":
    logger.add(
        "logs/transcriber_{time}.log",
        rotation="1 day",
        level="DEBUG"
    )

    print("Whisper Transcriber Test")
    print("\nModel boyutları: tiny, small, medium, large")
    model = input("Model boyutu (Enter=small): ").strip() or "small"

    print("\nDil kodları: tr (Türkçe), en (İngilizce)")
    lang = input("Dil (Enter=tr): ").strip() or "tr"

    audio_file = input("\nSes dosyası yolu: ").strip()

    if audio_file:
        try:
            transcriber = Transcriber(model_size=model, language=lang)
            result = transcriber.transcribe_with_progress(audio_file)

            print("\n" + "="*50)
            print("SONUÇ")
            print("="*50)
            print(f"\nTam Metin:\n{result['text']}\n")
            print(f"Segment sayısı: {len(result['segments'])}")
            print(f"Algılanan dil: {result['language']}")

            print("\nİlk 3 segment:")
            for seg in result['segments'][:3]:
                print(f"  [{seg['start']:.2f}s - {seg['end']:.2f}s] "
                      f"({seg['confidence']:.0%}): {seg['text']}")

        except Exception as e:
            print(f"\n❌ Hata: {e}")
