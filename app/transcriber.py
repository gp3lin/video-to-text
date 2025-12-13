"""
Konuşma Tanıma Modülü (Speech-to-Text)
========================================
Bu modül faster-whisper kullanarak ses dosyalarını metne çevirir.

faster-whisper Nedir?
---------------------
- OpenAI Whisper'ın CTranslate2 ile optimize edilmiş versiyonu
- 4-5x DAHA HIZLI, aynı doğruluk
- %40-50 daha az bellek kullanımı
- 99 dili destekler (Türkçe dahil)
- Offline çalışır (internet gerekmez)

Model Boyutları:
- tiny: 39MB, en hızlı ama düşük doğruluk
- base: 74MB
- small: 244MB
- medium: 769MB
- large-v3: 1550MB (en iyi doğruluk)
- large-v3-turbo: 809MB (ÖNERİLEN - hızlı ve çok iyi doğruluk)

Compute Types (Hız/Bellek Optimizasyonu):
- float32: En yüksek hassasiyet, en yavaş
- float16: GPU için optimal (CUDA)
- int8: CPU için optimal, 2x hız artışı
- int8_float16: GPU için en hızlı
"""

from pathlib import Path
from typing import Union, Dict, List
from loguru import logger
from faster_whisper import WhisperModel
from tqdm import tqdm
import config.settings as settings


class Transcriber:
    """
    Whisper tabanlı konuşma tanıma sınıfı.

    Bu sınıf Whisper modelini yönetir ve transcription işlemlerini yapar.
    Sınıf kullanma nedeni: Model bir kez yüklenir, tekrar tekrar kullanılır.
    """

    def __init__(self, model_size: str = None, language: str = None, device: str = "cpu", compute_type: str = "int8"):
        """
        Transcriber başlatıcı.

        Args:
            model_size: Whisper model boyutu (tiny, small, medium, large-v3, large-v3-turbo)
                Verilmezse settings'ten alınır
            language: Dil kodu (tr, en vb.)
                None verilirse Whisper otomatik dil algılar (önerilen)
            device: "cpu", "cuda", veya "auto"
                Varsayılan: "cpu"
            compute_type: "float32", "float16", "int8", "int8_float16"
                CPU için: "int8" (önerilen - 2x hızlı)
                GPU için: "float16" veya "int8_float16" (önerilen)
                Varsayılan: "int8"
        """
        # Model boyutu belirtilmemişse settings'ten al
        self.model_size = model_size or settings.WHISPER_MODEL_SIZE

        # Device ve compute type
        self.device = device
        self.compute_type = compute_type

        # Dil: None ise otomatik algılama yapılacak
        # Sadece language parametresi açıkça verilmediyse settings'ten al
        if language is not None:
            self.language = language
        else:
            # Otomatik dil algılama için None kullan
            self.language = None

        lang_info = self.language if self.language else "otomatik algılama"
        logger.info(f"Transcriber başlatılıyor: {self.model_size} model ({self.compute_type} on {self.device}), {lang_info} dili")

        # Model henüz yüklenmedi
        self.model = None

    def load_model(self):
        """
        faster-whisper modelini yükler.

        İlk çalıştırmada:
        - Model internet üzerinden indirilir (Hugging Face cache)
        - 2-10 dakika sürebilir (model boyutuna göre)

        Sonraki çalıştırmalarda:
        - Model cache'den yüklenir (hızlı)

        faster-whisper avantajları:
        - 4-5x daha hızlı işlem
        - %40-50 daha az bellek kullanımı
        - CTranslate2 optimizasyonu
        """
        if self.model is not None:
            # Model zaten yüklüyse tekrar yükleme
            logger.debug("Model zaten yüklü, tekrar yükleme yapılmıyor")
            return

        logger.info(f"faster-whisper {self.model_size} model yükleniyor ({self.compute_type} on {self.device})...")
        logger.info("İlk kullanımda model indirilecek, bu 2-10 dakika sürebilir.")

        try:
            # WhisperModel():
            # - Model boyutunu al (tiny, small, medium, large-v3, large-v3-turbo)
            # - CTranslate2 formatında yükle
            # - Quantization uygula (int8, float16 vb.)
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                # download_root: Modelin kaydedileceği yer
                download_root=str(settings.MODEL_DIR)
            )

            logger.success(f"{self.model_size} model başarıyla yüklendi ({self.compute_type} on {self.device})")

        except Exception as e:
            logger.error(f"Model yükleme hatası: {str(e)}")
            raise

    def transcribe(
        self,
        audio_path: Union[str, Path],
        beam_size: int = 5,
        temperature: float = 0.0,
        vad_filter: bool = True,
        **kwargs
    ) -> Dict:
        """
        Ses dosyasını metne çevirir (faster-whisper ile).

        Args:
            audio_path: Ses dosyasının yolu (.wav, .mp3 vb.)
            beam_size: Arama algoritması beam sayısı (varsayılan: 5)
                Daha yüksek = daha iyi doğruluk ama yavaş
                Önerilen: 5 (openai/whisper varsayılanı: 1)
            temperature: 0.0-1.0 (varsayılan: 0.0)
                0.0 = deterministic (tutarlı, önerilen)
                1.0 = yaratıcı (stokastik)
            vad_filter: Voice Activity Detection (varsayılan: True)
                True = Sessizlikleri filtrele, halüsinasyonu azalt
                False = Tüm sesi işle
            **kwargs: faster-whisper'a geçirilecek ekstra parametreler
                - word_timestamps: Kelime bazlı zaman damgası
                - condition_on_previous_text: Önceki metne göre koşullandır

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
        logger.debug(f"Parametreler: beam_size={beam_size}, temperature={temperature}, vad_filter={vad_filter}")

        try:
            # faster-whisper transcribe():
            # Ses dosyasını alıp (segments generator, info) tuple'ı döndürür
            segments_generator, info = self.model.transcribe(
                str(audio_path),

                # language: Dil belirtmek doğruluğu artırır
                # None verilirse Whisper dili otomatik algılar
                language=self.language,

                # beam_size: Arama algoritması beam sayısı
                # 5 önerilir (openai/whisper varsayılanı 1)
                beam_size=beam_size,

                # temperature: 0.0 = deterministic (tutarlı sonuçlar)
                temperature=temperature,

                # vad_filter: Voice Activity Detection
                # Sessizlikleri filtreler, halüsinasyonu azaltır
                vad_filter=vad_filter,

                # **kwargs: Kullanıcının verdiği ekstra parametreler
                **kwargs
            )

            # Segments generator'u listeye çevir
            # faster-whisper generator döndürür, hepsini listeye almamız gerekiyor
            segments_list = list(segments_generator)

            # Algılanan dil bilgisi
            detected_language = info.language if hasattr(info, 'language') else self.language

            # Sonuçları işle ve zenginleştir
            processed_result = self._process_faster_whisper_result(segments_list, detected_language)

            # İstatistikler
            total_duration = processed_result["segments"][-1]["end"] if processed_result["segments"] else 0
            word_count = len(processed_result["text"].split())

            logger.success(
                f"Transcription tamamlandı: {word_count} kelime, "
                f"{total_duration:.2f} saniye, "
                f"dil: {detected_language}"
            )

            return processed_result

        except Exception as e:
            logger.error(f"Transcription hatası: {str(e)}")
            raise

    def _process_faster_whisper_result(self, segments_list: List, detected_language: str) -> Dict:
        """
        faster-whisper'ın ham sonucunu işler ve düzenler.

        Args:
            segments_list: faster-whisper'dan gelen segment listesi
            detected_language: Algılanan dil kodu

        Returns:
            Dict: İşlenmiş ve zenginleştirilmiş sonuç
        """
        # Segment'leri işle
        # faster-whisper her cümleyi/parçayı ayrı segment olarak döndürür
        processed_segments = []
        full_text = []

        for i, segment in enumerate(segments_list):
            # faster-whisper segment yapısı:
            # segment.start, segment.end, segment.text, segment.avg_logprob, segment.no_speech_prob
            processed_segments.append({
                "id": i,  # Segment numarası
                "start": round(segment.start, 2),  # Başlangıç (saniye)
                "end": round(segment.end, 2),  # Bitiş
                "text": segment.text.strip(),  # Metin (baştaki/sondaki boşlukları kaldır)

                # Güven skoru hesapla
                # faster-whisper avg_logprob ve no_speech_prob sağlar
                "confidence": self._calculate_confidence_from_logprob(
                    getattr(segment, 'avg_logprob', -1.0),
                    getattr(segment, 'no_speech_prob', 0.0)
                ),
            })

            # Tam metin için birleştir
            full_text.append(segment.text.strip())

        return {
            "text": " ".join(full_text),  # Tam metin
            "segments": processed_segments,  # Zaman damgalı parçalar
            "language": detected_language,  # Algılanan dil
        }

    def _process_result(self, raw_result: Dict) -> Dict:
        """
        Eski openai-whisper formatındaki sonucu işler (geriye dönük uyumluluk için).

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
                "confidence": self._calculate_confidence_from_logprob(
                    segment.get("avg_logprob", -1.0),
                    segment.get("no_speech_prob", 0.0)
                ),
            })

        return {
            "text": raw_result.get("text", "").strip(),  # Tam metin
            "segments": processed_segments,  # Zaman damgalı parçalar
            "language": raw_result.get("language", self.language),  # Algılanan dil
        }

    def _calculate_confidence(self, segment: Dict) -> float:
        """
        Eski API için: Segment dict'inden güven skorunu hesaplar (geriye dönük uyumluluk).

        Args:
            segment: Whisper segment dict'i

        Returns:
            float: 0.0-1.0 arası güven skoru
        """
        return self._calculate_confidence_from_logprob(
            segment.get("avg_logprob", -1.0),
            segment.get("no_speech_prob", 0.0)
        )

    def _calculate_confidence_from_logprob(self, avg_logprob: float, no_speech_prob: float) -> float:
        """
        avg_logprob ve no_speech_prob'dan güven skoru hesaplar.

        Whisper doğrudan confidence vermez, ama avg_logprob'dan
        yaklaşık bir güven skoru hesaplayabiliriz.

        Args:
            avg_logprob: Ortalama log probability
                Negatif değerler (-0.1 ile -3.0 arası)
                -0.1 -> yüksek güven
                -3.0 -> düşük güven
            no_speech_prob: Sessizlik olasılığı (0.0-1.0)
                0.0 -> kesinlikle konuşma var
                1.0 -> kesinlikle sessiz

        Returns:
            float: 0.0-1.0 arası güven skoru
        """
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

        Not: faster-whisper kendi içinde ilerleme göstermiyor, bu sadece
        başlangıç/bitiş bildirimi için basit bir wrapper.
        """
        with tqdm(total=100, desc="Transcribing (faster-whisper)") as pbar:
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
