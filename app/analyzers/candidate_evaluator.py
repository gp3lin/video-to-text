"""
Candidate Evaluator Module
============================
Aday değerlendirmesi ve yetkinlik analizi.
"""

from typing import Dict
from app.prompts.evaluation_prompts import create_evaluation_prompt


def analyze_evaluation(transcript_data: Dict) -> tuple[str, str]:
    """
    Candidate evaluation analizi için prompt'ları hazırlar.

    Args:
        transcript_data: Transkript verisi

    Returns:
        tuple: (system_prompt, user_prompt)
    """
    return create_evaluation_prompt(transcript_data)
