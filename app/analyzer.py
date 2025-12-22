"""
AI-Powered Interview/Meeting Analyzer
=======================================
Bu modül Ollama kullanarak video mülakat ve toplantılarını analiz eder.

Özellikler:
- Aday değerlendirmesi (yetkinlik bazlı puanlama)
- Görüşme özeti ve anahtar noktalar
- Sentiment & ton analizi
- Soru-cevap ayırma ve kalite değerlendirme

Kullanım:
    from app.analyzer import InterviewAnalyzer

    analyzer = InterviewAnalyzer(model_name="qwen3:4b")
    analysis = analyzer.analyze(transcript_data)
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from loguru import logger
import json
import time

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama kütüphanesi bulunamadı. 'pip install ollama' çalıştırın.")


class OllamaConnectionError(Exception):
    """Ollama servisi bağlantı hatası."""
    pass


class InterviewAnalyzer:
    """
    AI-powered mülakat ve toplantı analizi sınıfı.

    Ollama ile local AI modelleri kullanarak derin analiz yapar:
    - Offline çalışır (internet gerektirmez)
    - Ücretsiz (API key gerekmez)
    - Türkçe optimizasyonları

    Attributes:
        model_name (str): Kullanılacak Ollama modeli (varsayılan: qwen3:4b)
        temperature (float): AI model temperature (0.0-1.0, varsayılan: 0.3)
        timeout (int): AI yanıt timeout süresi (saniye)
        enabled_analyses (list): Aktif analiz tipleri
    """

    def __init__(
        self,
        model_name: str = "qwen3:4b",
        temperature: float = 0.3,
        timeout: int = 120,
        enabled_analyses: Optional[List[str]] = None
    ):
        """
        Analyzer'ı başlat.

        Args:
            model_name: Ollama model adı (qwen3:4b, qwen3:14b, vs.)
            temperature: Model temperature (düşük = daha tutarlı)
                0.0-0.3: Deterministik, tutarlı (önerilir)
                0.7-1.0: Yaratıcı, çeşitli
            timeout: Maksimum bekleme süresi (saniye)
            enabled_analyses: Hangi analizler çalışacak
                None = hepsi
                ['evaluation', 'summary', 'sentiment', 'qa']
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError(
                "Ollama kütüphanesi bulunamadı. Kurulum:\n"
                "pip install ollama"
            )

        self.model_name = model_name
        self.temperature = temperature
        self.timeout = timeout

        # Varsayılan: Tüm analizler aktif
        if enabled_analyses is None:
            self.enabled_analyses = ['evaluation', 'summary', 'sentiment', 'qa']
        else:
            self.enabled_analyses = enabled_analyses

        logger.info(f"InterviewAnalyzer başlatıldı: model={model_name}, temp={temperature}")

    def check_ollama_connection(self) -> bool:
        """
        Ollama servisi çalışıyor mu kontrol et.

        Returns:
            bool: True if available, False otherwise

        Raises:
            OllamaConnectionError: Servis bulunamazsa
        """
        try:
            # Ollama list komutu ile test
            models = ollama.list()
            logger.debug(f"Ollama connection OK. Modeller: {len(models.get('models', []))}")
            return True

        except Exception as e:
            error_msg = f"""
❌ Ollama servisi bulunamadı!

Çözüm adımları:
1. Ollama kurulu mu kontrol edin: ollama --version
2. Kurulu değilse: https://ollama.com/download
3. Servis çalışıyor mu: ollama list
4. Model indirilmiş mi: ollama pull {self.model_name}

Detaylı hata: {str(e)}
            """
            logger.error(error_msg)
            raise OllamaConnectionError(error_msg)

    def check_model_available(self) -> bool:
        """
        Belirtilen model indirilmiş mi kontrol et.

        Returns:
            bool: True if model exists
        """
        try:
            models_response = ollama.list()
            models = models_response.get('models', [])

            available_models = [m['name'] for m in models]

            # Model adı kontrolü (qwen3:4b veya sadece qwen3 olabilir)
            model_found = any(
                self.model_name in model_name or model_name in self.model_name
                for model_name in available_models
            )

            if not model_found:
                logger.warning(f"Model '{self.model_name}' bulunamadı!")
                logger.info(f"Mevcut modeller: {', '.join(available_models)}")
                logger.info(f"İndirmek için: ollama pull {self.model_name}")
                return False

            logger.debug(f"Model '{self.model_name}' mevcut")
            return True

        except Exception as e:
            logger.error(f"Model kontrolü başarısız: {e}")
            return False

    def analyze(
        self,
        transcript_data: Dict,
        analysis_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Ana analiz fonksiyonu - transcript verisi üzerinde AI analizi yapar.

        Args:
            transcript_data: output_formatter.py'den gelen JSON yapısı
                {
                    "metadata": {...},
                    "speakers": {...},
                    "timeline": [...],
                    "full_transcript": "..."
                }

            analysis_types: Çalıştırılacak analizler (None = tümü)
                ['evaluation'] - Aday değerlendirmesi
                ['summary'] - Özet ve anahtar noktalar
                ['sentiment'] - Duygu ve ton analizi
                ['qa'] - Soru-cevap ayırma

        Returns:
            Dict: Analiz sonuçları
                {
                    "metadata": {
                        "analyzed_at": "...",
                        "model_used": "qwen3:4b",
                        "analysis_duration": 12.5,
                        "status": "complete" / "partial" / "failed"
                    },
                    "candidate_evaluation": {...},
                    "summary": {...},
                    "sentiment_analysis": {...},
                    "qa_analysis": {...},
                    "errors": [...]
                }

        Raises:
            OllamaConnectionError: Ollama servisi bulunamazsa
        """
        start_time = time.time()

        # Ollama connection kontrolü
        try:
            self.check_ollama_connection()
            self.check_model_available()
        except OllamaConnectionError:
            raise

        # Hangi analizler çalışacak?
        analyses_to_run = analysis_types or self.enabled_analyses

        logger.info(f"Analiz başlıyor: {', '.join(analyses_to_run)}")

        # Sonuçlar dict
        results = {
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "model_used": self.model_name,
                "temperature": self.temperature,
                "status": "partial",  # Başlangıçta partial
                "enabled_analyses": analyses_to_run
            },
            "errors": []
        }

        # Her analizi sırayla çalıştır (error handling ile)
        for analysis_type in analyses_to_run:
            try:
                logger.info(f"'{analysis_type}' analizi çalıştırılıyor...")

                if analysis_type == "evaluation":
                    results["candidate_evaluation"] = self._run_evaluation(transcript_data)

                elif analysis_type == "summary":
                    results["summary"] = self._run_summary(transcript_data)

                elif analysis_type == "sentiment":
                    results["sentiment_analysis"] = self._run_sentiment(transcript_data)

                elif analysis_type == "qa":
                    results["qa_analysis"] = self._run_qa_separation(transcript_data)

                else:
                    logger.warning(f"Bilinmeyen analiz tipi: {analysis_type}")
                    continue

                logger.success(f"'{analysis_type}' analizi tamamlandı")

            except Exception as e:
                error_msg = f"{analysis_type} analizi başarısız: {str(e)}"
                logger.error(error_msg)

                results["errors"].append({
                    "analysis": analysis_type,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

                # Hata olsa bile diğer analizlere devam et
                continue

        # Analiz süresi
        elapsed_time = time.time() - start_time
        results["metadata"]["analysis_duration"] = round(elapsed_time, 2)

        # Status güncelle
        if not results["errors"]:
            results["metadata"]["status"] = "complete"
        elif len(results["errors"]) == len(analyses_to_run):
            results["metadata"]["status"] = "failed"
        else:
            results["metadata"]["status"] = "partial"

        logger.info(
            f"Analiz tamamlandı: {results['metadata']['status']} "
            f"({elapsed_time:.1f}s)"
        )

        return results

    def _call_ollama(self, system_prompt: str, user_prompt: str) -> Dict:
        """
        Ollama API'yi çağır ve JSON yanıtını parse et.

        Args:
            system_prompt: AI'nin rolü ve görevleri
            user_prompt: Spesifik task ve veri

        Returns:
            Dict: Parse edilmiş JSON yanıtı

        Raises:
            Exception: API hatası veya JSON parse hatası
        """
        try:
            logger.debug(f"Ollama çağrılıyor: model={self.model_name}")

            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_prompt
                    }
                ],
                options={
                    'temperature': self.temperature,
                    'num_predict': 2048  # Max token output
                }
            )

            # Yanıtı al (Pydantic model)
            response_text = response.message.content

            # Debug: response_text None mi kontrol et
            if response_text is None:
                response_text = ""
                logger.error("Response content is None!")

            logger.debug(f"Ollama yanıtı alındı ({len(response_text)} karakter)")

            # JSON parse et
            # AI bazen ```json ... ``` formatında dönebilir, temizle
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # ```json kaldır
            if response_text.startswith('```'):
                response_text = response_text[3:]  # ``` kaldır
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # ``` kaldır
            response_text = response_text.strip()

            # JSON parse
            result = json.loads(response_text)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse hatası: {e}")
            logger.error(f"Yanıt: {response_text[:500]}...")
            raise Exception(f"AI yanıtı geçerli JSON değil: {str(e)}")

        except Exception as e:
            logger.error(f"Ollama API hatası: {e}")
            raise

    # Gerçek analiz metodları - Faz 2 implemented

    def _run_evaluation(self, transcript_data: Dict) -> Dict:
        """Aday değerlendirmesi analizi."""
        from app.analyzers.candidate_evaluator import analyze_evaluation

        logger.debug("Evaluation prompt'u hazırlanıyor...")
        system_prompt, user_prompt = analyze_evaluation(transcript_data)

        logger.debug("Ollama'ya evaluation prompt'u gönderiliyor...")
        result = self._call_ollama(system_prompt, user_prompt)

        return result

    def _run_summary(self, transcript_data: Dict) -> Dict:
        """Özet analizi."""
        from app.analyzers.summarizer import analyze_summary

        logger.debug("Summary prompt'u hazırlanıyor...")
        system_prompt, user_prompt = analyze_summary(transcript_data)

        logger.debug("Ollama'ya summary prompt'u gönderiliyor...")
        result = self._call_ollama(system_prompt, user_prompt)

        return result

    def _run_sentiment(self, transcript_data: Dict) -> Dict:
        """Sentiment analizi."""
        from app.analyzers.sentiment_analyzer import analyze_sentiment

        logger.debug("Sentiment prompt'u hazırlanıyor...")
        system_prompt, user_prompt = analyze_sentiment(transcript_data)

        logger.debug("Ollama'ya sentiment prompt'u gönderiliyor...")
        result = self._call_ollama(system_prompt, user_prompt)

        return result

    def _run_qa_separation(self, transcript_data: Dict) -> Dict:
        """Soru-cevap ayırma analizi."""
        from app.analyzers.qa_separator import analyze_qa

        logger.debug("Q&A prompt'u hazırlanıyor...")
        system_prompt, user_prompt = analyze_qa(transcript_data)

        logger.debug("Ollama'ya Q&A prompt'u gönderiliyor...")
        result = self._call_ollama(system_prompt, user_prompt)

        return result


# Test için
if __name__ == "__main__":
    print("InterviewAnalyzer Test")
    print("="*60)

    try:
        # Analyzer oluştur
        analyzer = InterviewAnalyzer(model_name="qwen3:4b")

        # Connection test
        print("\n1. Ollama connection testi...")
        analyzer.check_ollama_connection()
        print("   [OK] Ollama baglantisi OK")

        # Model kontrolü
        print(f"\n2. Model ({analyzer.model_name}) kontrolu...")
        if analyzer.check_model_available():
            print(f"   [OK] Model mevcut")
        else:
            print(f"   [WARN] Model bulunamadi. Indirin: ollama pull {analyzer.model_name}")

        # Basit test verisi
        print("\n3. Basit analiz testi...")
        test_data = {
            "metadata": {"video_name": "test.mp4", "duration_seconds": 60},
            "speakers": {
                "SPEAKER_00": {"total_duration": 30, "total_words": 50},
                "SPEAKER_01": {"total_duration": 30, "total_words": 50}
            },
            "timeline": [
                {"speaker": "SPEAKER_00", "text": "Merhaba, bugün görüşme yapacağız.", "start": 0, "end": 3},
                {"speaker": "SPEAKER_01", "text": "Merhaba, hazırım.", "start": 3, "end": 5}
            ],
            "full_transcript": "Merhaba, bugün görüşme yapacağız. Merhaba, hazırım."
        }

        results = analyzer.analyze(test_data, analysis_types=['summary'])

        print(f"\n   Analiz sonucu:")
        print(f"   - Status: {results['metadata']['status']}")
        print(f"   - Süre: {results['metadata']['analysis_duration']}s")
        if 'summary' in results:
            print(f"   - Özet: {results['summary']['executive_summary'][:100]}...")

        print("\n[SUCCESS] Tum testler basarili!")

    except Exception as e:
        print(f"\n[ERROR] Hata: {e}")
        import traceback
        traceback.print_exc()
