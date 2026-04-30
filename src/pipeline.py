import csv
import json
from pathlib import Path
from datetime import datetime
from src.ocr_reader import OCRReader
from src.llm_extractor import LlamaExtractor
from src.config import Config


class ReceiptPipeline:
    """Orchestrates the full receipt processing workflow."""
    
    def __init__(self):
        self.ocr = OCRReader()
        self.extractor = LlamaExtractor(
            model_name=Config.MODEL_NAME,
            temperature=Config.EXTRACTION_TEMPERATURE,
            top_p=Config.EXTRACTION_TOP_P
        )
        self.results = []
    
    def process_single(self, image_path: Path) -> dict:
        """Process one receipt through all stages."""
        print(f"\n{'='*50}")
        print(f"📋 Processing: {image_path.name}")
        print(f"{'='*50}")
        
        # Stage 1: OCR
        raw_text = self.ocr.extract_text(image_path)
        if not raw_text:
            print("  ⚠️ No text found")
            return {"error": "No text extracted", "file": image_path.name}
        
        # Stage 2: Clean
        clean_text = OCRReader.clean_text(raw_text)
        print(f"  📝 Text: {clean_text[:80]}...")
        
        # Stage 3: LLM Extraction
        result = self.extractor.extract_receipt(clean_text, Config.RECEIPT_SCHEMA)
        result["source_file"] = image_path.name
        result["processed_at"] = datetime.now().isoformat()
        
        # Stage 4: Store
        self.results.append(result)
        
        # Summary
        print(f"  🏪 Vendor: {result.get('vendor', 'N/A')}")
        print(f"  💰 Total: {result.get('total_amount', 'N/A')}")
        
        return result
    
    def process_all(self) -> list:
        """Process all receipts in the configured directory."""
        image_files = list(Config.RECEIPTS_DIR.glob("*.[pj][np][g]"))
        
        if not image_files:
            print(f"⚠️ No images found in {Config.RECEIPTS_DIR}")
            return []
        
        print(f"\n📁 Found {len(image_files)} receipt(s)")
        
        for i, path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}]")
            try:
                self.process_single(path)
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.results.append({
                    "error": str(e),
                    "source_file": path.name
                })
        
        return self.results
    
    def save_to_csv(self, filepath: Path = None):
        """Export all results to CSV."""
        if not filepath:
            filepath = Config.OUTPUT_CSV
        
        if not self.results:
            print("⚠️ No data to save")
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "vendor", "category", "date", "total_amount",
                "currency", "payment_method", "items", "source_file"
            ])
            writer.writeheader()
            for r in self.results:
                # Flatten items for CSV
                row = {k: r.get(k, "") for k in writer.fieldnames}
                row["items"] = json.dumps(r.get("items", []))
                writer.writerow(row)
        
        print(f"✅ Saved {len(self.results)} entries to {filepath}")
    
    def get_analysis(self) -> dict:
        """Generate spending analysis from collected data."""
        if not self.results:
            print("⚠️ No data to analyze")
            return {}
        
        return self.extractor.analyze_spending(self.results)