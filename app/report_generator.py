"""
Markdown Report Generator
===========================
AI analiz sonuçlarından profesyonel Markdown rapor oluşturur.
"""

from pathlib import Path
from typing import Dict
from datetime import datetime


class ReportGenerator:
    """Markdown rapor oluşturucu."""

    @staticmethod
    def create_report(result_data: Dict, output_path: Path) -> Path:
        """
        AI analiz sonuçlarından Markdown raporu oluştur.

        Args:
            result_data: process_video() sonucu (analysis içeren)
            output_path: Rapor dosyası yolu (.md)

        Returns:
            Path: Oluşturulan rapor dosyası yolu
        """
        # Analysis var mı kontrol et
        if 'analysis' not in result_data:
            raise ValueError("result_data'da 'analysis' anahtarı bulunamadı")

        analysis = result_data['analysis']
        metadata = result_data['metadata']
        speakers = result_data['speakers']

        # Markdown içeriği
        markdown = []

        # Başlık
        markdown.append(f"# Mulakat Analiz Raporu\n")
        markdown.append(f"**Video:** {metadata.get('video_name', 'Bilinmiyor')}  ")
        markdown.append(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
        markdown.append(f"**Sure:** {metadata.get('duration_seconds', 0):.0f} saniye  ")
        markdown.append(f"**Konusmaci Sayisi:** {metadata.get('num_speakers', 0)}  ")
        markdown.append(f"**AI Model:** {analysis['metadata'].get('model_used', 'Bilinmiyor')}\n")
        markdown.append("---\n")

        # Özet (varsa)
        if 'summary' in analysis:
            markdown.append("## Ozet\n")
            summary = analysis['summary']
            markdown.append(f"{summary.get('executive_summary', 'Ozet bulunamadi')}\n")
            markdown.append("")

        # Aday Değerlendirmesi (varsa)
        if 'candidate_evaluation' in analysis:
            markdown.append("## Aday Degerlendirmesi\n")
            eval_data = analysis['candidate_evaluation']

            overall = eval_data.get('overall_score', 0)
            markdown.append(f"**Genel Puan:** {overall}/10\n")
            markdown.append(f"**Oneri:** {eval_data.get('hiring_recommendation', 'Belirtilmedi')}\n")
            markdown.append("")

            # Yetkinlikler
            if 'competencies' in eval_data:
                markdown.append("### Yetkinlikler\n")
                for comp_name, comp_data in eval_data['competencies'].items():
                    score = comp_data.get('score', 0)
                    markdown.append(f"**{comp_name.title()}: {score}/10**\n")

                    # Güçlü yönler
                    strengths = comp_data.get('strengths', [])
                    if strengths:
                        markdown.append("- Guclu: " + ", ".join(strengths))

                    # Zayıf yönler
                    weaknesses = comp_data.get('weaknesses', [])
                    if weaknesses:
                        markdown.append("- Gelisim: " + ", ".join(weaknesses))

                    markdown.append("")

        # Sentiment Analizi (varsa)
        if 'sentiment_analysis' in analysis:
            markdown.append("## Duygusal Ton Analizi\n")
            sentiment = analysis['sentiment_analysis']

            overall_sent = sentiment.get('overall', {})
            markdown.append(f"**Genel Duygu:** {overall_sent.get('sentiment', 'Bilinmiyor')}  ")
            markdown.append(f"**Durum:** {overall_sent.get('emotional_state', 'Bilinmiyor')}  ")
            markdown.append(f"**Stres:** {overall_sent.get('stress_level', 'Bilinmiyor')}\n")

        # Soru-Cevap Analizi (varsa)
        if 'qa_analysis' in analysis:
            markdown.append("## Soru-Cevap Analizi\n")
            qa = analysis['qa_analysis']

            stats = qa.get('statistics', {})
            markdown.append(f"**Toplam Soru:** {stats.get('total_questions', 0)}  ")
            markdown.append(f"**Ortalama Cevap Kalitesi:** {stats.get('avg_answer_quality', 0):.1f}/10\n")

        # İstatistikler
        markdown.append("---\n")
        markdown.append("## Istatistikler\n")
        markdown.append(f"- Analiz Suresi: {analysis['metadata'].get('analysis_duration', 0):.1f}s\n")
        markdown.append(f"- Durum: {analysis['metadata'].get('status', 'Bilinmiyor')}\n")

        # Dosyaya yaz
        markdown_content = "\n".join(markdown)

        output_path = Path(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return output_path


# Test
if __name__ == "__main__":
    print("Report Generator Test")

    # Test verisi
    test_data = {
        "metadata": {
            "video_name": "test.mp4",
            "duration_seconds": 120,
            "num_speakers": 2
        },
        "speakers": {},
        "analysis": {
            "metadata": {
                "model_used": "qwen3:4b",
                "analysis_duration": 10.5,
                "status": "complete"
            },
            "summary": {
                "executive_summary": "Test ozeti buraya gelecek."
            },
            "candidate_evaluation": {
                "overall_score": 7.5,
                "hiring_recommendation": "Onerilir",
                "competencies": {
                    "communication": {
                        "score": 8,
                        "strengths": ["Acik ifade"],
                        "weaknesses": ["Hizli konusma"]
                    }
                }
            }
        }
    }

    # Rapor oluştur
    report_path = Path("test_report.md")
    ReportGenerator.create_report(test_data, report_path)
    print(f"Test rapor olusturuldu: {report_path}")
