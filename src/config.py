import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """ Centralized config file for ollama-related prompts"""
    
    # model name
    MODEL_NAME = os.getenv("MODEL_NAME")
    
    # base dir
    BASE_DIR = Path(__file__).parent.parent
    RECEIPTS_DIR = BASE_DIR / "receipts"
    OUTPUT_DIR = BASE_DIR / "output"
    OUTPUT_CSV = OUTPUT_DIR / "spending_data.csv"
    
    # LLM parameters
    EXTRACTION_TEMPERATURE = 0.1
    EXTRACTION_TOP_P = 0.9
    ANALYSIS_TEMPERATURE = 0.3
    ANALYSIS_TOP_P = 0.5

    # JSON format of receipts
    receipt_schema = {
    "format": "json",
    "schema": {
        "type": "array",
        "properties": {
            "Merchant Name": {"type": "string"},
            "Expense Category": {"type": "string"},
            "Transaction Date": {"type": "string", "format": "date"},
            "Total Amount": {"type": "number", "format": "float"},
            "Currency": {"type": "string"},
            "Payment Method": {"type": "string"},
            "Items": {
                "type": "array",
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": "number"},
                    "price": {"type": "number"}
                },
                "required": ["name", "quantity", "price"]
            }
        },
        "required": ["Merchant Name", "Expense Category", "Transaction Date", "Total Amount", "Currency", "Payment Method", "Items"]
    }
}

@classmethod
def get_receipt_schema(cls):
    return cls.receipt_schema


    
    