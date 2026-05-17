import json
import ollama

class LlamaExtractor:
    """Handles all communication with the local Llama model."""
    
    def __init__(self, model_name: str, temperature: float = 0.0, top_p: float = 0.3):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        print(f"🤖 Using model: {model_name}")
    
    def extract_receipt(self, ocr_text: str, schema: dict) -> dict:
        """Extract structured data from receipt text using JSON schema."""
        print("  🤖 Extracting with Llama...")
        
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise receipt data extractor. Return only valid JSON matching the schema."
                },
                {
                    "role": "user",
                    "content": f"Extract from this receipt:\n\n{ocr_text}"
                }
            ],
            format=schema,
            options={
                "temperature": self.temperature,
                "top_p": self.top_p,
            }
        )
        
        return json.loads(response['message']['content'])
    
    def analyze_spending(self, receipts: list, temperature: float = 0.3) -> dict:
        """Analyze collected receipts for insights."""
        print("  📊 Analyzing spending patterns...")
        
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst. Return ONLY valid JSON."
                },
                {
                    "role": "user",
                    "content": f"Analyze this spending data:\n{json.dumps(receipts, indent=2)}\n\nReturn JSON with: total_spent, weekly_average, monthly_estimate, top_category, insights, recommendations (as list)"
                }
            ],
            format="json",
            options={
                "temperature": temperature,
                "top_p": 0.5,
            }
        )
        
        return json.loads(response['message']['content'])