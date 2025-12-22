"""
Summarizer Module
==================
Görüşme özeti ve anahtar noktalar analizi.
"""

from typing import Dict
from app.prompts.summary_prompts import create_summary_prompt


def analyze_summary(transcript_data: Dict) -> tuple[str, str]:
    """
    Özet analizi için prompt'ları hazırlar.

    Args:
        transcript_data: Transkript verisi

    Returns:
        tuple: (system_prompt, user_prompt)
    """
    return create_summary_prompt(transcript_data)
