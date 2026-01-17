import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TimestampSegment:
    start_time: float
    end_time: float
    text: str
    start_str: str
    end_str: str

def parse_transcript_with_timestamps(transcript: str) -> List[TimestampSegment]:
    """Parse transcript and extract timestamp segments"""
    segments = []
    lines = transcript.strip().split('\n')
    
    for line in lines:
        # Pattern to match [start_time - end_time] text
        pattern = r'\[(\d{2}:\d{2}:\d{2}\.\d{2}) - (\d{2}:\d{2}:\d{2}\.\d{2})\] (.+)'
        match = re.match(pattern, line)
        
        if match:
            start_str, end_str, text = match.groups()
            start_time = time_to_seconds(start_str)
            end_time = time_to_seconds(end_str)
            
            segments.append(TimestampSegment(
                start_time=start_time,
                end_time=end_time,
                text=text,
                start_str=start_str,
                end_str=end_str
            ))
    
    return segments

def time_to_seconds(time_str: str) -> float:
    """Convert time string HH:MM:SS.ms to seconds"""
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_parts = parts[2].split('.')
    seconds = int(seconds_parts[0])
    milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
    
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 100

def seconds_to_time(seconds: float) -> str:
    """Convert seconds back to HH:MM:SS.ms format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    whole_seconds = int(secs)
    milliseconds = int((secs - whole_seconds) * 100)
    
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:02d}"

def find_relevant_segments(query: str, segments: List[TimestampSegment], max_segments: int = 5) -> List[TimestampSegment]:
    """Find segments most relevant to a query based on text similarity"""
    # Simple keyword matching for now - could be enhanced with semantic search
    query_words = set(query.lower().split())
    scored_segments = []
    
    for segment in segments:
        segment_words = set(segment.text.lower().split())
        # Calculate simple overlap score
        overlap = len(query_words.intersection(segment_words))
        if overlap > 0:
            scored_segments.append((segment, overlap))
    
    # Sort by relevance score and return top segments
    scored_segments.sort(key=lambda x: x[1], reverse=True)
    return [segment for segment, _ in scored_segments[:max_segments]]

def get_timestamp_context(segments: List[TimestampSegment], target_segment: TimestampSegment, context_window: int = 2) -> List[TimestampSegment]:
    """Get surrounding segments for context"""
    try:
        index = segments.index(target_segment)
        start_idx = max(0, index - context_window)
        end_idx = min(len(segments), index + context_window + 1)
        return segments[start_idx:end_idx]
    except ValueError:
        return [target_segment]

def format_timestamp_for_video(seconds: float) -> str:
    """Format seconds for video player (e.g., YouTube format)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h{minutes}m{secs}s"
    elif minutes > 0:
        return f"{minutes}m{secs}s"
    else:
        return f"{secs}s"
