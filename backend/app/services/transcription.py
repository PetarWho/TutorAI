import os
from faster_whisper import WhisperModel
from app.config import LECTURE_DIR

model = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16"
)

def transcribe(audio_path: str, lecture_id: str = None) -> str:
    segments, info = model.transcribe(audio_path)
    transcript = []
    total_duration = info.duration

    for seg in segments:
        transcript.append(
            f"[{seg.start:.2f} - {seg.end:.2f}] {seg.text}"
        )

    full_transcript = "\n".join(transcript)
    
    # Save transcript to file for PDF generation
    if lecture_id:
        transcript_path = os.path.join(LECTURE_DIR, f"{lecture_id}_transcript.txt")
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(full_transcript)
        
        # Save duration to file for later retrieval
        duration_path = os.path.join(LECTURE_DIR, f"{lecture_id}_duration.txt")
        with open(duration_path, 'w', encoding='utf-8') as f:
            f.write(str(total_duration))
    
    return full_transcript

def load_transcript(lecture_id: str) -> str:
    """Load saved transcript for a lecture"""
    transcript_path = os.path.join(LECTURE_DIR, f"{lecture_id}_transcript.txt")
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def load_duration(lecture_id: str) -> float:
    """Load saved duration for a lecture"""
    duration_path = os.path.join(LECTURE_DIR, f"{lecture_id}_duration.txt")
    if os.path.exists(duration_path):
        with open(duration_path, 'r', encoding='utf-8') as f:
            return float(f.read().strip())
    return None
