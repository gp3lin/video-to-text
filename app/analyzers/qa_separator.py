"""
Q&A Separator Module
=====================
Soru-cevap ayırma ve kalite değerlendirmesi.
"""

from typing import Dict
from app.prompts.qa_prompts import create_qa_prompt


def analyze_qa(transcript_data: Dict) -> tuple[str, str]:
    """
    Q&A separation analizi için prompt'ları hazırlar.

    Args:
        transcript_data: Transkript verisi

    Returns:
        tuple: (system_prompt, user_prompt)
    """
    return create_qa_prompt(transcript_data)
