#!/usr/bin/env python3
"""
Receipt Sense - Local AI Receipt Scanner & Spending Tracker
Uses OCR + Llama 3.2 via Ollama for offline receipt processing.
"""

from src.config import Config
from src.pipeline import ReceiptPipeline
import json


def main():
    # Setup directories
    Config.setup()
    
    # Initialize pipeline
    pipeline = ReceiptPipeline()
    
    # Process all receipts
    results = pipeline.process_all()
    
    if results:
        # Save to CSV
        pipeline.save_to_csv()
        
        # Analyze spending
        print("\n" + "="*50)
        print("📊 GENERATING ANALYSIS")
        print("="*50)
        
        analysis = pipeline.get_analysis()
        if analysis:
            print(json.dumps(analysis, indent=2))
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()