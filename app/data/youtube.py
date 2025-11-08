# Commented out YouTube transcript API import
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

import fitz  # PyMuPDF


def fetch_youtube_transcript_from_pdf(pdf_path: str) -> str:
    """Extract text from a pre-saved transcript PDF instead of fetching online."""
    try:
        with fitz.open(pdf_path) as doc:
            return "\n".join(page.get_text("text") for page in doc)
    except Exception as e:
        return ""
