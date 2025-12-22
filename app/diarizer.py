"""
Konuşmacı Ayırma Modülü (Speaker Diarization)
===============================================
Bu modül ses dosyasındaki konuşmacıları ayırır ve kim ne zaman konuştuğunu belirler.

Speaker Diarization Nedir?
---------------------------
"Who spoke when?" sorusuna cevap verir:
- Video/seste kaç kişi konuşuyor?
- Her konuşmacı hangi zaman aralıklarında konuşuyor?
- Konuşmacıları birbirinden ayırt et

Önemli: İsimleri bilmez, sadece "SPEAKER_00", "SPEAKER_01" gibi etiketler verir.

pyannote.audio Nedir?
---------------------
- En iyi açık kaynak speaker diarization modeli
- Hugging Face üzerinde yayınlanmış
- Dil-bağımsız çalışır (Türkçe dahil)
- Hugging Face token gerektirir (ücretsiz)
"""

from pathlib import Path
from typing import Union, List, Dict, Optional
from loguru import logger
import torch
from pyannote.audio import Pipeline
import config.settings as settings


class SpeakerDiarizer:
    """
    pyannote.audio tabanlı konuşmacı ayırma sınıfı.

    Bu sınıf ses dosyalarındaki konuşmacıları ayırır ve
    zaman damgalı konuşmacı bilgilerini döndürür.
    """

    def __init__(self, hf_token: Optional[str] = None, device: str = "auto"):
        """
        Diarizer başlatıcı.

        Args:
            hf_token: Hugging Face token
                Verilmezse settings'ten veya .env'den alınır
                Token almak için: https://huggingface.co/settings/tokens

            device: İşlem cihazı
                "auto": Otomatik seç (GPU varsa kullan, yoksa CPU)
                "cuda": NVIDIA GPU
                "cpu": CPU (yavaş ama herkes kullanabilir)
        """
        # Token kontrolü
        self.hf_token = hf_token or settings.HUGGINGFACE_TOKEN

        if not self.hf_token:
            error_msg = (
                "Hugging Face token bulunamadı!\n"
                "1. https://huggingface.co/settings/tokens adresinden token alın\n"
                "2. .env dosyasına ekleyin: HUGGINGFACE_TOKEN=your_token_here"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Device seçimi
        if device == "auto":
            # GPU varsa kullan, yoksa CPU
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Diarizer başlatılıyor: {self.device} cihazı kullanılacak")

        if self.device == "cpu":
            logger.warning(
                "CPU kullanılıyor. GPU'lu sistemlerde daha hızlı olabilir.\n"
                "GPU desteği için: pip install torch --index-url "
                "https://download.pytorch.org/whl/cu118"
            )

        # Pipeline henüz yüklenmedi
        self.pipeline = None

    def load_model(self):
        """
        pyannote.audio 
          pipeline'ını yükler.

        İlk çalıştırmada:
        - Model Hugging Face'den indirilir (~300MB)
        - Token ile kimlik doğrulama yapılır
        - settings.MODEL_DIR klasörüne kaydedilir

        Sonraki çalıştırmalarda:
        - Model cache'den yüklenir (hızlı)
        """
        if self.pipeline is not None:
            logger.debug("Pipeline zaten yüklü")
            return

        logger.info("pyannote.audio pipeline yükleniyor...")
        logger.info(
            "İlk kullanımda model indirilecek (~300MB), 2-5 dakika sürebilir."
        )

        try:
            # Pipeline.from_pretrained():
            # Hugging Face'den önceden eğitilmiş modeli yükler
            #
            # "pyannote/speaker-diarization-3.1":
            # pyannote.audio'nun en son ve en iyi modeli
            #
            # NOT: Offline mod environment variable'lar ile kontrol edilir
            # (HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1)
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",

                # use_auth_token: Hugging Face kimlik doğrulama
                # Token olmadan model indirilemez
                use_auth_token=self.hf_token,

                # cache_dir: İndirilen modelin saklanacağı yer
                cache_dir=str(settings.MODEL_DIR)
            )

            # Pipeline'ı GPU/CPU'ya taşı
            # .to(device): PyTorch'un device yönetimi
            # GPU varsa hesaplamalar GPU'da yapılır (çok daha hızlı)
            self.pipeline = self.pipeline.to(torch.device(self.device))

            logger.success("Pipeline başarıyla yüklendi")

        except Exception as e:
            logger.error(f"Pipeline yükleme hatası: {str(e)}")

            # Token hatası mı kontrol et
            if "401" in str(e) or "authentication" in str(e).lower():
                logger.error(
                    "Token hatası! Token'ınızı kontrol edin:\n"
                    "1. https://huggingface.co/settings/tokens\n"
                    "2. Token'ın 'Read' yetkisi olmalı\n"
                    "3. .env dosyasına doğru kopyalandığından emin olun"
                )

            raise

    def diarize(
        self,
        audio_path: Union[str, Path],
        num_speakers: Optional[int] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        # Yeni parametreler: Speaker diarization iyileştirmeleri
        min_duration: float = 0.5,  # Minimum segment süresi (saniye)
        segmentation_onset: float = 0.5,  # Konuşma başlangıç hassasiyeti (0-1)
        segmentation_offset: float = 0.5,  # Konuşma bitiş hassasiyeti (0-1)
        clustering_threshold: Optional[float] = None,  # Clustering eşik değeri
        embedding_batch_size: int = 32,  # GPU batch size (performans)
        embedding_exclude_overlap: bool = True  # Üst üste konuşmaları hariç tut
    ) -> List[Dict]:
        """
        Ses dosyasındaki konuşmacıları ayırır (gelişmiş parametrelerle).

        Args:
            audio_path: Ses dosyasının yolu (.wav, .mp3 vb.)

            num_speakers: Konuşmacı sayısı (biliyorsanız)
                Örnek: 2 (röportaj, podcast)
                None: Otomatik tespit et

            min_speakers: Minimum konuşmacı sayısı
                Örnek: 1 (en az 1 kişi konuşuyor)

            max_speakers: Maksimum konuşmacı sayısı
                Örnek: 10 (panel tartışması)

            min_duration: Minimum segment süresi (varsayılan: 0.5 saniye)
                Daha kısa segment'ler filtrelenir (gürültü azaltma)
                Önerilen: 0.3-1.0 arası

            segmentation_onset: (KULLANILMIYOR - gelecek için rezerve)
                Konuşma başlangıç hassasiyeti
                NOT: pyannote 3.1 bu parametreyi apply() metodunda desteklemiyor

            segmentation_offset: (KULLANILMIYOR - gelecek için rezerve)
                Konuşma bitiş hassasiyeti
                NOT: pyannote 3.1 bu parametreyi apply() metodunda desteklemiyor

            clustering_threshold: (KULLANILMIYOR - gelecek için rezerve)
                Clustering eşik değeri
                NOT: pyannote 3.1 bu parametreyi apply() metodunda desteklemiyor

            embedding_batch_size: (KULLANILMIYOR - gelecek için rezerve)
                GPU batch boyutu
                NOT: pyannote 3.1 bu parametreyi apply() metodunda desteklemiyor

            embedding_exclude_overlap: (KULLANILMIYOR - gelecek için rezerve)
                Üst üste konuşmaları hariç tut
                NOT: pyannote 3.1 bu parametreyi apply() metodunda desteklemiyor

            ** ÖNEMLİ: Yukarıdaki parametreler şu anda kullanılmıyor **
            ** Sadece min_duration ile post-processing yapılıyor **
            ** İyileştirme: min_duration filtreleme + segment birleştirme **

        Returns:
            List[Dict]: Konuşmacı zaman damgaları
                [
                    {
                        "speaker": "SPEAKER_00",
                        "start": 0.0,
                        "end": 15.5
                    },
                    {
                        "speaker": "SPEAKER_01",
                        "start": 15.5,
                        "end": 32.1
                    },
                    ...
                ]

        Raises:
            FileNotFoundError: Ses dosyası bulunamazsa
            Exception: Diarization hatası

        Örnek Kullanım:
            >>> diarizer = SpeakerDiarizer()
            >>> segments = diarizer.diarize("audio.wav", num_speakers=2)
            >>> for seg in segments[:3]:
            ...     print(f"{seg['speaker']}: {seg['start']:.2f}s - {seg['end']:.2f}s")
            SPEAKER_00: 0.00s - 15.50s
            SPEAKER_01: 15.50s - 32.10s
            SPEAKER_00: 32.10s - 45.00s
        """
        audio_path = Path(audio_path)

        # Dosya var mı?
        if not audio_path.exists():
            error_msg = f"Ses dosyası bulunamadı: {audio_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Pipeline yüklü mü?
        if self.pipeline is None:
            self.load_model()

        logger.info(f"Diarization başlıyor: {audio_path.name}")

        # Konuşmacı sayısı parametreleri
        # Bu parametreler pyannote'a ipucu verir
        params = {}
        if num_speakers is not None:
            # Kesin sayı biliyorsak
            params["num_speakers"] = num_speakers
            logger.info(f"Konuşmacı sayısı belirtildi: {num_speakers}")
        else:
            # Aralık biliyorsak
            if min_speakers is not None:
                params["min_speakers"] = min_speakers
            if max_speakers is not None:
                params["max_speakers"] = max_speakers
            logger.info("Konuşmacı sayısı otomatik tespit edilecek")

        # NOT: pyannote 3.1 pipeline.apply() sadece num_speakers, min_speakers, max_speakers kabul eder
        # Diğer parametreler (onset, offset, clustering vb.) pipeline instantiation sırasında ayarlanmalı
        # Şimdilik sadece desteklenen parametreleri kullanıyoruz
        # İyileştirmeler post-processing ile yapılıyor (min_duration, segment merging)

        logger.debug(f"Diarization parametreleri: {params}")
        logger.debug(
            f"Post-processing parametreleri: min_duration={min_duration}, "
            f"segmentation_onset={segmentation_onset}, segmentation_offset={segmentation_offset}, "
            f"clustering_threshold={clustering_threshold}, embedding_batch_size={embedding_batch_size}, "
            f"embedding_exclude_overlap={embedding_exclude_overlap}"
        )

        try:
            # pipeline(audio_path):
            # Ana diarization fonksiyonu
            # Audio'yu yükler, işler ve konuşmacıları ayırır
            logger.debug("pyannote pipeline çalıştırılıyor...")
            diarization = self.pipeline(str(audio_path), **params)

            # Sonuçları işle (min_duration filtresi ile)
            segments = self._process_diarization(diarization, min_duration=min_duration)

            # Post-processing: Yakın segment'leri birleştir
            segments = self._merge_close_segments(segments, max_gap=0.5)

            # İstatistikler
            speakers = set(seg["speaker"] for seg in segments)
            total_duration = segments[-1]["end"] if segments else 0

            logger.success(
                f"Diarization tamamlandı: {len(speakers)} konuşmacı, "
                f"{len(segments)} segment, {total_duration:.2f} saniye"
            )

            return segments

        except Exception as e:
            logger.error(f"Diarization hatası: {str(e)}")
            raise

    def _process_diarization(self, diarization, min_duration: float = 0.5) -> List[Dict]:
        """
        pyannote'un ham diarization sonucunu işler ve filtreler.

        Args:
            diarization: pyannote.audio diarization objesi
            min_duration: Minimum segment süresi (saniye)
                Daha kısa segment'ler filtrelenir (gürültü/hata azaltma)

        Returns:
            List[Dict]: İşlenmiş ve filtrelenmiş konuşmacı segmentleri
        """
        segments = []
        filtered_count = 0

        # diarization.itertracks():
        # Her konuşma parçasını (track) döner
        # yield_label=True: Konuşmacı etiketini de ver
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            # turn: pyannote Segment objesi
            # turn.start: Başlangıç zamanı (saniye)
            # turn.end: Bitiş zamanı (saniye)
            # speaker: Konuşmacı etiketi (SPEAKER_00, SPEAKER_01, ...)

            duration = turn.end - turn.start

            # Minimum süre kontrolü
            # Çok kısa segment'ler genellikle gürültü veya hatalı tespit
            if duration < min_duration:
                filtered_count += 1
                logger.debug(
                    f"Segment filtrelendi (çok kısa): {speaker} "
                    f"{turn.start:.2f}s-{turn.end:.2f}s ({duration:.2f}s)"
                )
                continue

            segments.append({
                "speaker": speaker,
                "start": round(turn.start, 2),  # 2 ondalık
                "end": round(turn.end, 2),
                "duration": round(duration, 2)
            })

        if filtered_count > 0:
            logger.info(f"{filtered_count} kısa segment filtrelendi (min_duration: {min_duration}s)")

        # Zaman sırasına göre sırala
        # Bazen pyannote sırasız dönebilir
        segments.sort(key=lambda x: x["start"])

        return segments

    def _merge_close_segments(self, segments: List[Dict], max_gap: float = 0.5) -> List[Dict]:
        """
        Aynı konuşmacının yakın segment'lerini birleştirir.

        Sorun: Pyannote bazen aynı kişinin konuşmasını küçük parçalara bölebiliyor.
        Örnek: SPEAKER_00 [0-5s], SPEAKER_00 [5.2-10s] → Birleştirilmeli

        Args:
            segments: İşlenmiş segment listesi
            max_gap: Maksimum boşluk (saniye)
                İki segment arası boşluk bundan azsa birleştir

        Returns:
            List[Dict]: Birleştirilmiş segment listesi
        """
        if not segments:
            return segments

        merged = []
        current = segments[0].copy()

        for next_seg in segments[1:]:
            # Aynı konuşmacı mı?
            same_speaker = current["speaker"] == next_seg["speaker"]

            # Aralarındaki boşluk
            gap = next_seg["start"] - current["end"]

            # Birleştirme koşulları:
            # 1. Aynı konuşmacı
            # 2. Boşluk max_gap'ten küçük (veya negatif = üst üste)
            if same_speaker and gap <= max_gap:
                # Birleştir: current segment'i genişlet
                current["end"] = next_seg["end"]
                current["duration"] = round(current["end"] - current["start"], 2)
                logger.debug(
                    f"Segment birleştirildi: {current['speaker']} "
                    f"{current['start']:.2f}s-{current['end']:.2f}s "
                    f"(gap: {gap:.2f}s)"
                )
            else:
                # Birleştirme yok: current'i kaydet, next'i current yap
                merged.append(current)
                current = next_seg.copy()

        # Son segment'i ekle
        merged.append(current)

        initial_count = len(segments)
        merged_count = len(merged)
        if merged_count < initial_count:
            logger.info(
                f"{initial_count - merged_count} segment birleştirildi "
                f"({initial_count} → {merged_count})"
            )

        return merged

    def get_speaker_statistics(self, segments: List[Dict]) -> Dict:
        """
        Konuşmacı istatistiklerini hesaplar.

        Args:
            segments: diarize() fonksiyonundan dönen segmentler

        Returns:
            Dict: Her konuşmacı için istatistikler
                {
                    "SPEAKER_00": {
                        "total_duration": 125.5,  # Toplam konuşma süresi
                        "num_segments": 10,       # Kaç kez konuştu
                        "avg_segment_duration": 12.55,  # Ortalama süre
                        "percentage": 45.2       # Toplam içinde yüzdesi
                    },
                    ...
                }
        """
        if not segments:
            return {}

        # Konuşmacıları grupla
        speaker_data = {}

        for seg in segments:
            speaker = seg["speaker"]

            if speaker not in speaker_data:
                speaker_data[speaker] = {
                    "segments": [],
                    "total_duration": 0
                }

            speaker_data[speaker]["segments"].append(seg)
            speaker_data[speaker]["total_duration"] += seg["duration"]

        # Toplam süre
        total_duration = sum(data["total_duration"] for data in speaker_data.values())

        # İstatistikleri hesapla
        statistics = {}

        for speaker, data in speaker_data.items():
            num_segs = len(data["segments"])
            total_dur = data["total_duration"]

            statistics[speaker] = {
                "total_duration": round(total_dur, 2),
                "num_segments": num_segs,
                "avg_segment_duration": round(total_dur / num_segs, 2),
                "percentage": round((total_dur / total_duration) * 100, 1) if total_duration > 0 else 0
            }

        return statistics


# Yardımcı fonksiyon
def diarize_audio(
    audio_path: Union[str, Path],
    hf_token: Optional[str] = None,
    **kwargs
) -> List[Dict]:
    """
    Hızlı diarization fonksiyonu.

    SpeakerDiarizer sınıfını kullanmadan direkt diarization yapar.

    Args:
        audio_path: Ses dosyası
        hf_token: Hugging Face token (opsiyonel)
        **kwargs: diarize() metoduna geçilecek parametreler

    Returns:
        List[Dict]: Konuşmacı segmentleri

    Örnek:
        >>> segments = diarize_audio("audio.wav", num_speakers=2)
    """
    diarizer = SpeakerDiarizer(hf_token=hf_token)
    return diarizer.diarize(audio_path, **kwargs)


# Test için
if __name__ == "__main__":
    logger.add(
        "logs/diarizer_{time}.log",
        rotation="1 day",
        level="DEBUG"
    )

    print("pyannote.audio Speaker Diarizer Test")
    print("\nHugging Face Token:")
    print("https://huggingface.co/settings/tokens adresinden alabilirsiniz")

    token = input("HF Token (Enter=.env'den al): ").strip() or None

    audio_file = input("\nSes dosyası yolu: ").strip()

    num_speakers_input = input(
        "\nKonuşmacı sayısı (biliyorsanız, Enter=otomatik): "
    ).strip()

    num_speakers = int(num_speakers_input) if num_speakers_input else None

    if audio_file:
        try:
            diarizer = SpeakerDiarizer(hf_token=token)
            segments = diarizer.diarize(audio_file, num_speakers=num_speakers)

            # İstatistikler
            stats = diarizer.get_speaker_statistics(segments)

            print("\n" + "="*60)
            print("DIARIZATION SONUCU")
            print("="*60)

            print(f"\nToplam {len(segments)} segment")
            print(f"Konuşmacı sayısı: {len(stats)}")

            print("\nKonuşmacı İstatistikleri:")
            for speaker, data in stats.items():
                print(f"\n{speaker}:")
                print(f"  Toplam süre: {data['total_duration']:.2f}s")
                print(f"  Segment sayısı: {data['num_segments']}")
                print(f"  Ortalama segment: {data['avg_segment_duration']:.2f}s")
                print(f"  Yüzde: %{data['percentage']:.1f}")

            print("\nİlk 10 segment:")
            for seg in segments[:10]:
                print(
                    f"  {seg['speaker']}: "
                    f"{seg['start']:.2f}s - {seg['end']:.2f}s "
                    f"({seg['duration']:.2f}s)"
                )

        except Exception as e:
            print(f"\n❌ Hata: {e}")
            import traceback
            traceback.print_exc()
