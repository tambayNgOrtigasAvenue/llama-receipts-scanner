import easyocr
from pathlib import Path

class OCRReader:
    def __init__(self, languages: list = None):
        self.languages = languages or ['en']
        print("🔄 Loading OCR engine (one-time)...")
        self.reader = easyocr.Reader(self.languages, gpu=False)
        print("✅ OCR engine ready")

    def extract_text(self, img_path: Path) -> str:
        """Convert a receipt image to raw text."""
        print(f"  📷 Scanning: {image_path.name}")
        results = self.reader.readtext(str(image_path))
        text = " ".join([item[1] for item in results])
        return text.strip()
    
    @staticmethod
    def clean_text(raw_text: str) -> str:
        """Basic cleaning of OCR output."""
        text = " ".join(raw_text.split())  # Remove extra whitespace
        text = text.replace("|", "I")       # Common OCR fix
        return text
