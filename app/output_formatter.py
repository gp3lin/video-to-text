"""
Çıktı Formatlama Modülü
========================
Bu modül transcription ve diarization sonuçlarını birleştirir
ve kullanılabilir JSON formatına dönüştürür.

Ana Görevler:
1. Transcription + Diarization birleştirme
2. Zaman aralıklarını eşleştirme
3. JSON formatında yapılandırma
4. İstatistik hesaplama
"""

from pathlib import Path
from typing import Dict, List, Union
from datetime import datetime
from loguru import logger
import json


class OutputFormatter:
    """
    Transcription ve diarization sonuçlarını işler ve formatlar.
    """

    @staticmethod
    def merge_results(
        transcription: Dict,
        diarization: List[Dict],
        video_name: str = None,
        additional_metadata: Dict = None
    ) -> Dict:
        """
        Transcription ve diarization sonuçlarını birleştirir.

        Bu fonksiyon iki farklı kaynaktan gelen bilgiyi birleştirir:
        - Transcription: "Ne söylendi?" (metin + zaman)
        - Diarization: "Kim söyledi?" (konuşmacı + zaman)

        Zorluk: İki sonucun zaman aralıkları tam örtüşmeyebilir.
        Çözüm: Overlap (örtüşme) mantığı ile eşleştirme.

        Args:
            transcription: transcriber.py'dan gelen sonuç
                {
                    "text": "Tam metin",
                    "segments": [
                        {"start": 0.0, "end": 3.5, "text": "..."},
                        ...
                    ]
                }

            diarization: diarizer.py'dan gelen sonuç
                [
                    {"speaker": "SPEAKER_00", "start": 0.0, "end": 15.5},
                    ...
                ]

            video_name: Video dosyası adı (metadata için)

            additional_metadata: Ekstra metadatalar

        Returns:
            Dict: Birleştirilmiş ve yapılandırılmış sonuç
        """
        logger.info("Transcription ve diarization sonuçları birleştiriliyor...")

        # Transcription segmentlerini al
        trans_segments = transcription.get("segments", [])

        # Her transcription segmentine konuşmacı ata
        merged_segments = []

        for trans_seg in trans_segments:
            # Bu segment'in başlangıç ve bitiş zamanları
            trans_start = trans_seg["start"]
            trans_end = trans_seg["end"]

            # Bu zaman aralığında hangi konuşmacı(lar) konuşuyor?
            # find_speaker_at_time() ile en uygun konuşmacıyı bul
            speaker = OutputFormatter._find_speaker_for_segment(
                trans_start,
                trans_end,
                diarization
            )

            # Birleştirilmiş segment oluştur
            merged_segments.append({
                "start": trans_start,
                "end": trans_end,
                "duration": round(trans_end - trans_start, 2),
                "speaker": speaker,
                "text": trans_seg["text"].strip(),
                "confidence": trans_seg.get("confidence", 0.0)
            })

        # Konuşmacılara göre grupla
        speakers_data = OutputFormatter._group_by_speaker(merged_segments, diarization)

        # Toplam süre
        total_duration = merged_segments[-1]["end"] if merged_segments else 0

        # Metadata oluştur
        metadata = {
            "video_name": video_name or "unknown",
            "duration_seconds": round(total_duration, 2),
            "language": transcription.get("language", "unknown"),
            "num_speakers": len(speakers_data),
            "num_segments": len(merged_segments),
            "processed_at": datetime.now().isoformat(),
            "model_info": {
                "transcription": "OpenAI Whisper",
                "diarization": "pyannote.audio 3.1"
            }
        }

        # Ekstra metadata ekle
        if additional_metadata:
            metadata.update(additional_metadata)

        # Final JSON yapısı
        result = {
            "metadata": metadata,
            "speakers": speakers_data,
            "timeline": merged_segments,
            "full_transcript": transcription.get("text", "").strip()
        }

        logger.success(
            f"Birleştirme tamamlandı: {len(speakers_data)} konuşmacı, "
            f"{len(merged_segments)} segment"
        )

        return result

    @staticmethod
    def _find_speaker_for_segment(
        start: float,
        end: float,
        diarization: List[Dict]
    ) -> str:
        """
        Belirli bir zaman aralığında konuşan kişiyi bulur.

        Mantık:
        1. Transcription segment'i ile diarization segment'lerini karşılaştır
        2. En çok örtüşen (overlap) konuşmacıyı bul
        3. Örtüşme yoksa en yakın konuşmacıyı al

        Args:
            start: Segment başlangıcı (saniye)
            end: Segment bitişi (saniye)
            diarization: Diarization sonuçları

        Returns:
            str: Konuşmacı etiketi (SPEAKER_00, SPEAKER_01, ...)
        """
        max_overlap = 0
        best_speaker = "SPEAKER_UNKNOWN"

        for dia_seg in diarization:
            dia_start = dia_seg["start"]
            dia_end = dia_seg["end"]

            # Örtüşme hesapla (overlap)
            # İki zaman aralığının kesişimi
            overlap_start = max(start, dia_start)
            overlap_end = min(end, dia_end)
            overlap = max(0, overlap_end - overlap_start)

            # En çok örtüşeni bul
            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = dia_seg["speaker"]

        # Hiç örtüşme yoksa yaklaşık eşleştirme
        if max_overlap == 0:
            logger.warning(
                f"Segment [{start:.2f}s - {end:.2f}s] için "
                f"tam örtüşme bulunamadı, yaklaşık eşleştirme yapılıyor"
            )

            # En yakın zaman aralığını bul
            min_distance = float('inf')

            for dia_seg in diarization:
                # Zaman farkını hesapla
                distance = min(
                    abs(start - dia_seg["start"]),
                    abs(end - dia_seg["end"])
                )

                if distance < min_distance:
                    min_distance = distance
                    best_speaker = dia_seg["speaker"]

        return best_speaker

    @staticmethod
    def _group_by_speaker(
        merged_segments: List[Dict],
        diarization: List[Dict]
    ) -> Dict:
        """
        Segmentleri konuşmacılara göre gruplar ve istatistik hesaplar.

        Args:
            merged_segments: Birleştirilmiş segmentler
            diarization: Ham diarization sonuçları

        Returns:
            Dict: Konuşmacı bazlı veri ve istatistikler
                {
                    "SPEAKER_00": {
                        "total_duration": 65.2,
                        "total_words": 450,
                        "num_segments": 5,
                        "percentage": 45.2,
                        "segments": [...]
                    },
                    ...
                }
        """
        speakers = {}
        total_duration = merged_segments[-1]["end"] if merged_segments else 0

        # Her konuşmacıyı initialize et
        for dia_seg in diarization:
            speaker = dia_seg["speaker"]
            if speaker not in speakers:
                speakers[speaker] = {
                    "total_duration": 0,
                    "total_words": 0,
                    "num_segments": 0,
                    "segments": []
                }

        # Segmentleri grupla
        for seg in merged_segments:
            speaker = seg["speaker"]

            if speaker not in speakers:
                # SPEAKER_UNKNOWN gibi durumlar için
                speakers[speaker] = {
                    "total_duration": 0,
                    "total_words": 0,
                    "num_segments": 0,
                    "segments": []
                }

            speakers[speaker]["segments"].append(seg)
            speakers[speaker]["total_duration"] += seg["duration"]
            speakers[speaker]["num_segments"] += 1

            # Kelime sayısı
            word_count = len(seg["text"].split())
            speakers[speaker]["total_words"] += word_count

        # İstatistikleri hesapla
        for speaker, data in speakers.items():
            # Yüzde hesapla
            if total_duration > 0:
                data["percentage"] = round(
                    (data["total_duration"] / total_duration) * 100,
                    1
                )
            else:
                data["percentage"] = 0

            # Yuvarla
            data["total_duration"] = round(data["total_duration"], 2)

        return speakers

    @staticmethod
    def save_to_json(
        result: Dict,
        output_path: Union[str, Path],
        pretty: bool = True
    ) -> Path:
        """
        Sonucu JSON dosyasına kaydeder.

        Args:
            result: merge_results()'dan dönen sonuç
            output_path: JSON dosyası yolu
            pretty: Güzel formatlanmış mı? (indent, sort_keys)

        Returns:
            Path: Oluşturulan dosya yolu
        """
        output_path = Path(output_path)

        # Klasör var mı?
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"JSON dosyası kaydediliyor: {output_path}")

        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                # Güzel formatlı JSON
                # indent=2: Her seviye 2 boşluk girintili
                # ensure_ascii=False: Türkçe karakterleri koru
                # sort_keys=True: Anahtarları alfabetik sırala
                json.dump(
                    result,
                    f,
                    indent=2,
                    ensure_ascii=False,
                    sort_keys=False  # Metadata üstte kalsın
                )
            else:
                # Kompakt JSON (küçük dosya boyutu)
                json.dump(result, f, ensure_ascii=False)

        # Dosya boyutu
        file_size_kb = output_path.stat().st_size / 1024

        logger.success(
            f"JSON başarıyla kaydedildi: {output_path.name} ({file_size_kb:.2f} KB)"
        )

        return output_path

    @staticmethod
    def load_from_json(json_path: Union[str, Path]) -> Dict:
        """
        JSON dosyasından sonuç yükler.

        Args:
            json_path: JSON dosyası yolu

        Returns:
            Dict: Yüklenmiş sonuç

        Raises:
            FileNotFoundError: Dosya bulunamazsa
            json.JSONDecodeError: Geçersiz JSON formatıysa
        """
        json_path = Path(json_path)

        if not json_path.exists():
            raise FileNotFoundError(f"JSON dosyası bulunamadı: {json_path}")

        logger.info(f"JSON dosyası yükleniyor: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            result = json.load(f)

        logger.success(f"JSON başarıyla yüklendi")
        return result

    @staticmethod
    def export_to_text(result: Dict, output_path: Union[str, Path]) -> Path:
        """
        Sonucu okunabilir metin dosyasına dönüştürür.

        Args:
            result: merge_results()'dan dönen sonuç
            output_path: Text dosyası yolu

        Returns:
            Path: Oluşturulan dosya yolu
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Text dosyası oluşturuluyor: {output_path}")

        with open(output_path, 'w', encoding='utf-8') as f:
            # Başlık
            metadata = result["metadata"]
            f.write(f"Video: {metadata['video_name']}\n")
            f.write(f"Süre: {metadata['duration_seconds']}s\n")
            f.write(f"Dil: {metadata['language']}\n")
            f.write(f"Konuşmacı Sayısı: {metadata['num_speakers']}\n")
            f.write(f"İşlenme Zamanı: {metadata['processed_at']}\n")
            f.write("\n" + "="*60 + "\n\n")

            # Timeline
            f.write("ZAMAN ÇİZELGESİ\n")
            f.write("="*60 + "\n\n")

            for seg in result["timeline"]:
                f.write(
                    f"[{seg['start']:.2f}s - {seg['end']:.2f}s] "
                    f"{seg['speaker']}:\n"
                    f"  {seg['text']}\n\n"
                )

            # Konuşmacı istatistikleri
            f.write("\n" + "="*60 + "\n")
            f.write("KONUŞMACI İSTATİSTİKLERİ\n")
            f.write("="*60 + "\n\n")

            for speaker, data in result["speakers"].items():
                f.write(f"{speaker}:\n")
                f.write(f"  Toplam Süre: {data['total_duration']}s\n")
                f.write(f"  Kelime Sayısı: {data['total_words']}\n")
                f.write(f"  Segment Sayısı: {data['num_segments']}\n")
                f.write(f"  Yüzde: %{data['percentage']}\n\n")

            # Tam metin
            f.write("\n" + "="*60 + "\n")
            f.write("TAM METİN\n")
            f.write("="*60 + "\n\n")
            f.write(result["full_transcript"])

        logger.success(f"Text dosyası oluşturuldu: {output_path}")
        return output_path


# Test için
if __name__ == "__main__":
    logger.add("logs/output_formatter_{time}.log", rotation="1 day")

    print("Output Formatter Test")

    # Örnek transcription
    sample_transcription = {
        "text": "Merhaba, bugün sizlere yeni projemizi anlatacağım. Çok güzel.",
        "language": "tr",
        "segments": [
            {"start": 0.0, "end": 3.5, "text": "Merhaba, bugün sizlere yeni projemizi anlatacağım.", "confidence": 0.95},
            {"start": 3.5, "end": 5.0, "text": "Çok güzel.", "confidence": 0.92}
        ]
    }

    # Örnek diarization
    sample_diarization = [
        {"speaker": "SPEAKER_00", "start": 0.0, "end": 5.0, "duration": 5.0}
    ]

    # Birleştir
    result = OutputFormatter.merge_results(
        sample_transcription,
        sample_diarization,
        video_name="test.mp4"
    )

    # JSON kaydet
    json_path = OutputFormatter.save_to_json(result, "test_output.json")
    print(f"\nJSON kaydedildi: {json_path}")

    # Text export
    txt_path = OutputFormatter.export_to_text(result, "test_output.txt")
    print(f"Text kaydedildi: {txt_path}")

    # JSON göster
    print("\nJSON İçeriği:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
