import os
import re
from datetime import datetime
from fpdf import FPDF
from typing import Optional
from app.config import DATA_DIR

PDF_DIR = f"{DATA_DIR}/pdfs"

class LecturePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Lecture Transcript', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(5)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, body)
        self.ln()

def parse_timestamp_line(line: str) -> Optional[tuple]:
    """Parse a timestamp line like '[00:00:00.00 - 00:00:05.00] text'"""
    pattern = r'\[(\d{2}:\d{2}:\d{2}\.\d{2}) - (\d{2}:\d{2}:\d{2}\.\d{2})\] (.+)'
    match = re.match(pattern, line)
    if match:
        start_time, end_time, text = match.groups()
        return start_time, end_time, text
    return None

def generate_transcript_pdf(transcript: str, lecture_id: str, filename: str = None) -> str:
    """Generate a PDF from lecture transcript with timestamps"""
    os.makedirs(PDF_DIR, exist_ok=True)
    
    if not filename:
        filename = f"lecture_{lecture_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    pdf_path = os.path.join(PDF_DIR, filename)
    pdf = LecturePDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Lecture Transcript - {lecture_id}', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 8, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
    pdf.ln(10)
    
    # Process transcript lines
    lines = transcript.strip().split('\n')
    current_segment = []
    segment_count = 0
    
    for line in lines:
        parsed = parse_timestamp_line(line)
        if parsed:
            start_time, end_time, text = parsed
            
            # Add previous segment if exists
            if current_segment:
                pdf.chapter_body('\n'.join(current_segment))
                current_segment = []
            
            # Add timestamp header
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, f'Timestamp: {start_time} - {end_time}', 0, 1, 'L', 1)
            
            # Add text
            pdf.set_font('Arial', '', 11)
            current_segment.append(text)
            segment_count += 1
            
            # Add page break every 10 segments for better readability
            if segment_count % 10 == 0:
                pdf.add_page()
        else:
            # Handle lines without timestamps (continuation text)
            current_segment.append(line)
    
    # Add final segment
    if current_segment:
        pdf.chapter_body('\n'.join(current_segment))
    
    pdf.output(pdf_path)
    return pdf_path

def generate_summary_pdf(summary: str, lecture_id: str, filename: str = None) -> str:
    """Generate a PDF with lecture summary"""
    os.makedirs(PDF_DIR, exist_ok=True)
    
    if not filename:
        filename = f"summary_{lecture_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    pdf_path = os.path.join(PDF_DIR, filename)
    pdf = LecturePDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Lecture Summary - {lecture_id}', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 8, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
    pdf.ln(15)
    
    # Add summary content
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, summary)
    
    pdf.output(pdf_path)
    return pdf_path
