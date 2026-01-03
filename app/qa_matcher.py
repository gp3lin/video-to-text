"""
Question-Answer Matcher
=======================
Matches interview questions to answers using equal time segmentation.

This module provides simple, deterministic question-answer matching:
1. Read questions from text file (one per line)
2. Divide video duration into N equal segments
3. Map each question to its corresponding time segment
4. Extract transcript text from that segment
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime
import json
from loguru import logger


class QAMatcher:
    """
    Question-Answer Matcher

    Matches questions to answers using equal time segmentation.
    This is a simple, deterministic approach that divides the video
    timeline into equal segments based on the number of questions.
    """

    def load_questions(self, questions_path: Path) -> List[str]:
        """
        Load questions from text file (one question per line).

        Args:
            questions_path: Path to questions.txt

        Returns:
            List[str]: List of questions

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or has invalid format
        """
        if not questions_path.exists():
            raise FileNotFoundError(f"Questions file not found: {questions_path}")

        try:
            with open(questions_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            raise ValueError(f"Error reading questions file: {e}")

        # Strip whitespace and filter empty lines
        questions = [line.strip() for line in lines if line.strip()]

        if not questions:
            raise ValueError("Questions file is empty")

        logger.info(f"Loaded {len(questions)} questions from {questions_path}")
        return questions

    def create_qa_pairs(self, questions: List[str], transcript_data: Dict) -> Dict:
        """
        Create question-answer pairs using equal time segmentation.

        Algorithm:
        1. Get video duration D from metadata
        2. Get number of questions N
        3. Calculate segment_duration = D / N
        4. For each question i (0 to N-1):
           - start_time = i * segment_duration
           - end_time = (i + 1) * segment_duration (or video end for last question)
           - Extract all timeline segments in [start_time, end_time]
           - Concatenate their text to form the answer
           - Create QA pair

        Args:
            questions: List of questions from questions.txt
            transcript_data: Full transcript data from output_formatter

        Returns:
            Dict: QA pairs with metadata
        """
        # Get video duration
        duration = transcript_data['metadata']['duration_seconds']
        num_questions = len(questions)

        # Calculate segment duration
        segment_duration = duration / num_questions

        logger.info(f"Video duration: {duration}s, {num_questions} questions, {segment_duration:.2f}s per question")

        # Create QA pairs
        qa_pairs = []
        timeline = transcript_data['timeline']

        for i, question in enumerate(questions):
            # Calculate time range
            start_time = i * segment_duration
            # Last question goes to end of video
            end_time = duration if i == num_questions - 1 else (i + 1) * segment_duration

            # Extract segments in this time range
            segments_in_range = self._extract_segments_in_range(timeline, start_time, end_time)

            if not segments_in_range:
                logger.warning(f"No segments found for Q{i+1} in range [{start_time:.2f}s - {end_time:.2f}s]")

            # Concatenate segments into answer
            answer_data = self._concatenate_segments(segments_in_range)

            # Create QA pair
            qa_pair = {
                "question_number": i + 1,
                "question": question,
                "time_segment": {
                    "start": round(start_time, 2),
                    "end": round(end_time, 2),
                    "duration": round(end_time - start_time, 2)
                },
                "answer": answer_data
            }

            qa_pairs.append(qa_pair)
            logger.debug(f"Q{i+1}: {len(segments_in_range)} segments, {answer_data['word_count']} words")

        # Build result
        result = {
            "metadata": {
                "video_name": transcript_data['metadata']['video_name'],
                "duration_seconds": duration,
                "total_questions": num_questions,
                "avg_segment_duration": round(segment_duration, 2),
                "matched_at": datetime.now().isoformat(),
                "matching_method": "equal_time_segmentation",
                "questions_source": "questions.txt"
            },
            "qa_pairs": qa_pairs,
            "original_transcript_metadata": {
                "num_speakers": transcript_data['metadata']['num_speakers'],
                "num_segments": transcript_data['metadata']['num_segments'],
                "language": transcript_data['metadata'].get('language', 'unknown')
            }
        }

        logger.success(f"Created {num_questions} QA pairs")
        return result

    def _extract_segments_in_range(self, timeline: List[Dict], start: float, end: float) -> List[Dict]:
        """
        Extract all timeline segments that fall within [start, end].

        Inclusion criteria: Segment overlaps with [start, end]
        - segment.start < end AND segment.end > start

        Args:
            timeline: Timeline segments from transcript
            start: Range start (seconds)
            end: Range end (seconds)

        Returns:
            List[Dict]: Segments in range
        """
        segments_in_range = []

        for segment in timeline:
            seg_start = segment.get('start')
            seg_end = segment.get('end')

            # Skip segments with missing time information
            if seg_start is None or seg_end is None:
                logger.warning(f"Skipping segment with missing time info: {segment.get('text', '')[:50]}...")
                continue

            # Check if segment overlaps with range
            if seg_start < end and seg_end > start:
                segments_in_range.append(segment)

        return segments_in_range

    def _concatenate_segments(self, segments: List[Dict]) -> Dict:
        """
        Concatenate segment texts and group by speaker.

        Args:
            segments: List of timeline segments

        Returns:
            Dict: {
                "text": "Full concatenated text",
                "speakers": {
                    "SPEAKER_00": "Text from SPEAKER_00",
                    ...
                },
                "word_count": 150,
                "num_segments": 8
            }
        """
        if not segments:
            return {
                "text": "",
                "speakers": {},
                "word_count": 0,
                "num_segments": 0
            }

        # Concatenate all texts
        full_text = " ".join(seg['text'] for seg in segments)

        # Group by speaker
        speakers = {}
        for segment in segments:
            speaker = segment['speaker']
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(segment['text'])

        # Concatenate per speaker
        speakers_text = {speaker: " ".join(texts) for speaker, texts in speakers.items()}

        # Count words
        word_count = len(full_text.split())

        return {
            "text": full_text,
            "speakers": speakers_text,
            "word_count": word_count,
            "num_segments": len(segments)
        }

    def save_to_json(self, qa_data: Dict, output_path: Path) -> Path:
        """
        Save QA pairs to JSON file.

        Args:
            qa_data: QA pairs data from create_qa_pairs()
            output_path: Output file path

        Returns:
            Path: Path to saved file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, ensure_ascii=False, indent=2)

        logger.info(f"QA JSON saved: {output_path}")
        return output_path

    def save_to_markdown(self, qa_data: Dict, output_path: Path) -> Path:
        """
        Save QA pairs to Markdown file.

        Args:
            qa_data: QA pairs data from create_qa_pairs()
            output_path: Output file path

        Returns:
            Path: Path to saved file
        """
        metadata = qa_data['metadata']
        qa_pairs = qa_data['qa_pairs']

        # Helper function to format time
        def format_time(seconds: float) -> str:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            if minutes > 0:
                return f"{minutes}:{secs:02d}"
            else:
                return f"0:{secs:02d}"

        # Build markdown
        lines = []

        # Header
        lines.append("# Mülakat Soru-Cevap Raporu")
        lines.append("")
        lines.append(f"**Video:** {metadata['video_name']}")

        # Format duration
        duration = metadata['duration_seconds']
        duration_str = format_time(duration)
        lines.append(f"**Süre:** {int(duration)} saniye ({duration_str})")

        lines.append(f"**Soru Sayısı:** {metadata['total_questions']}")
        lines.append(f"**Eşleştirme Yöntemi:** Eşit Zaman Segmentasyonu")

        # Format timestamp
        matched_at = metadata['matched_at']
        try:
            dt = datetime.fromisoformat(matched_at)
            formatted_dt = dt.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_dt = matched_at
        lines.append(f"**Oluşturulma Tarihi:** {formatted_dt}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # QA Pairs
        for qa in qa_pairs:
            q_num = qa['question_number']
            question = qa['question']
            time_seg = qa['time_segment']
            answer = qa['answer']

            lines.append(f"## Soru {q_num}: {question}")
            lines.append("")

            start_str = format_time(time_seg['start'])
            end_str = format_time(time_seg['end'])
            duration_seg = int(time_seg['duration'])

            lines.append(f"**Zaman Aralığı:** {start_str} - {end_str} ({duration_seg} saniye)")

            if answer['speakers']:
                speakers_list = ", ".join(answer['speakers'].keys())
                lines.append(f"**Konuşmacılar:** {speakers_list}")

            lines.append(f"**Kelime Sayısı:** {answer['word_count']}")
            lines.append("")

            # Answer text
            lines.append("### Cevap:")
            lines.append("")
            if answer['text']:
                lines.append(answer['text'])
            else:
                lines.append("*(Bu zaman aralığında konuşma bulunamadı)*")
            lines.append("")

            # Speaker breakdown
            if answer['speakers']:
                lines.append("### Konuşmacı Bazlı Detay:")
                lines.append("")
                for speaker, text in answer['speakers'].items():
                    lines.append(f"**{speaker}:**")
                    lines.append(f"> {text}")
                    lines.append("")

            lines.append("---")
            lines.append("")

        # Statistics
        lines.append("## İstatistikler")
        lines.append("")
        lines.append(f"- **Toplam Soru Sayısı:** {metadata['total_questions']}")
        lines.append(f"- **Ortalama Cevap Süresi:** {metadata['avg_segment_duration']} saniye")

        # Calculate average word count
        if qa_pairs:
            avg_words = sum(qa['answer']['word_count'] for qa in qa_pairs) / len(qa_pairs)
            lines.append(f"- **Ortalama Kelime Sayısı:** {int(avg_words)} kelime/cevap")

        lines.append(f"- **Toplam Segment:** {qa_data['original_transcript_metadata']['num_segments']}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Bu rapor otomatik olarak oluşturulmuştur.*")

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        logger.info(f"QA Markdown saved: {output_path}")
        return output_path
