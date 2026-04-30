import os
import json
import csv
from pathlib import Path
from dotenv import load_dotenv
import easyocr  # pip install easyocr
from llama_cpp import Llama

load_dotenv()
# ============================
# 1. SETUP & CONFIGURATION
# ============================

MODEL_PATH = os.getenv("MODEL_PATH")
RECEIPTS_DIR = "./receipts/"                    # Folder for your receipt images
OUTPUT_CSV = "./spending_data.csv"

# Initialize OCR (do this once - it downloads language models on first run)
print("🔄 Loading OCR engine...")
reader = easyocr.Reader(['en'], gpu=False)  # CPU-only for your setup

# Initialize LLM
print("🔄 Loading LLM model...")
llm = Llama(
    model_path=MODEL_PATH,
    temperature = 0.9,
    n_ctx=2048,       # Context window
    n_threads=6,      # Match your CPU cores (Ryzen 5 5625U has 6)
    verbose=False
)

# ============================
# 2. RECEIPT EXTRACTION PROMPT
# ============================

EXTRACTION_PROMPT = """You are a precise receipt data extractor. 
Extract the following information from this receipt text.
Return ONLY a valid JSON object. If something is missing, use null.

Receipt text:
{receipt_text}

JSON format:
{{
    "vendor": "Store name",
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "total_amount": 0.00,
    "currency": "PHP",
    "items": [
        {{"name": "Item name", "quantity": 1, "price": 0.00}}
    ],
    "tax": 0.00,
    "payment_method": "cash/card/etc or null",
    "category": "food/groceries/transport/etc or null"
}}

JSON:"""

# ============================
# 3. CORE FUNCTIONS
# ============================

def extract_text_from_image(image_path):
    """Use OCR to get text from a receipt image."""
    try:
        print(f"  📷 Scanning: {image_path}")
        results = reader.readtext(str(image_path))
        text = " ".join([item[1] for item in results])
        return text.strip()
    except Exception as e:
        print(f"  ❌ OCR failed: {e}")
        return ""

def extract_receipt_data(raw_text):
    """Send OCR text to Llama for structured extraction."""
    prompt = EXTRACTION_PROMPT.format(receipt_text=raw_text)
    
    try:
        response = llm(
            prompt,
            max_tokens=512,
            temperature=0.1,    # Low temperature = more consistent output
            stop=["\n\n"],
            echo=False
        )
        result_text = response['choices'][0]['text'].strip()
        
        # Try to parse as JSON
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            # Sometimes the model adds extra text; try to extract JSON
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(result_text[start:end])
            return {"error": "Could not parse JSON", "raw": result_text}
            
    except Exception as e:
        return {"error": str(e)}

def save_to_csv(data, filepath):
    """Append extracted data to a CSV for spending analysis."""
    file_exists = os.path.exists(filepath)
    
    with open(filepath, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow([
                "Vendor", "Date", "Total", "Currency", 
                "Category", "Payment Method", "Items Count"
            ])
        
        # Write data row
        if "error" not in data:
            writer.writerow([
                data.get("vendor", "Unknown"),
                data.get("date", "Unknown"),
                data.get("total_amount", 0),
                data.get("currency", "PHP"),
                data.get("category", "Unknown"),
                data.get("payment_method", "Unknown"),
                len(data.get("items", []))
            ])

# ============================
# 4. MAIN PROCESS
# ============================

def process_all_receipts():
    """Process all images in the receipts directory."""
    receipt_files = list(Path(RECEIPTS_DIR).glob("*.[pj][np][g]"))  # .jpg, .jpeg, .png
    receipt_files += list(Path(RECEIPTS_DIR).glob("*.pdf"))  # Add PDFs if needed
    
    if not receipt_files:
        print(f"⚠️  No images found in {RECEIPTS_DIR}")
        print("   Add your receipt images there and run again.")
        return
    
    print(f"\n📋 Found {len(receipt_files)} receipt(s) to process\n")
    
    for i, filepath in enumerate(receipt_files, 1):
        print(f"[{i}/{len(receipt_files)}] Processing: {filepath.name}")
        print("-" * 40)
        
        # Step 1: Extract text via OCR
        raw_text = extract_text_from_image(filepath)
        if not raw_text:
            print("  ⚠️  No text found, skipping...\n")
            continue
        
        print(f"  📝 Raw text: {raw_text[:100]}...")
        
        # Step 2: Extract structured data via LLM
        receipt_data = extract_receipt_data(raw_text)
        
        # Step 3: Display results
        if "error" not in receipt_data:
            print(f"  🏪 Vendor: {receipt_data.get('vendor', 'N/A')}")
            print(f"  📅 Date: {receipt_data.get('date', 'N/A')}")
            print(f"  💰 Total: {receipt_data.get('total_amount', 'N/A')} {receipt_data.get('currency', '')}")
            print(f"  📦 Items: {len(receipt_data.get('items', []))}")
        else:
            print(f"  ❌ Extraction error: {receipt_data.get('error')}")
            print(f"  Raw output: {receipt_data.get('raw', 'N/A')[:100]}")
        
        # Step 4: Save to CSV
        save_to_csv(receipt_data, OUTPUT_CSV)
        print(f"  💾 Saved to {OUTPUT_CSV}")
        print()

    print(f"✅ Done! All data saved to {OUTPUT_CSV}")

# ============================
# 5. SIMPLE SPENDING ANALYSIS
# ============================

def show_spending_summary():
    """Show a quick summary of your spending."""
    if not os.path.exists(OUTPUT_CSV):
        print("No data yet. Process some receipts first.")
        return
    
    import pandas as pd  # pip install pandas
    
    df = pd.read_csv(OUTPUT_CSV)
    print("\n📊 SPENDING SUMMARY")
    print("=" * 40)
    print(f"Total entries: {len(df)}")
    print(f"Total spending: ₱{df['Total'].sum():,.2f}")
    print("\nBy category:")
    print(df.groupby('Category')['Total'].agg(['sum', 'count']))

# ============================
# 6. RUN IT
# ============================

if __name__ == "__main__":
    process_all_receipts()
    show_spending_summary()