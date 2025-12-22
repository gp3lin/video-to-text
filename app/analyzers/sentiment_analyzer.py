"""
Sentiment Analyzer Module
===========================
Duygu ve ton analizi.
"""

from typing import Dict
from app.prompts.sentiment_prompts import create_sentiment_prompt


def analyze_sentiment(transcript_data: Dict) -> tuple[str, str]:
    """
    Sentiment analizi için prompt'ları hazırlar.

    Args:
        transcript_data: Transkript verisi

    Returns:
        tuple: (system_prompt, user_prompt)
    """
    return create_sentiment_prompt(transcript_data)
