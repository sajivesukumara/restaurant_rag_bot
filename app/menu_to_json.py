import os
import base64
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ====================== CONFIGURATION ======================
# Choose your provider: "grok", "openai", or "anthropic"
PROVIDER = "grok"          # Change as needed

# Your API Keys (store in .env file)
# XAI_API_KEY=...
# OPENAI_API_KEY=...
# ANTHROPIC_API_KEY=...

# Path to your menu image
IMAGE_PATH = "menu_images/tanjore_menu.jpg"   # Change this

# ===========================================================

def encode_image(image_path):
    """Convert image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_system_prompt():
    return """You are an expert restaurant menu data extractor.
Convert the menu image into a clean, structured JSON following this exact schema.
Be accurate with prices, names, and categories.
Fill normalization fields intelligently."""

def get_user_prompt():
    return """Extract all menu items from this restaurant menu image.

Return ONLY valid JSON in this exact structure (no extra text, no markdown):

{
  "restaurant": {
    "id": "string",
    "name": "string",
    "address": "string or null",
    "cuisine_type": ["array of strings"],
    "source": "Menu Image",
    "source_file": "filename.jpg",
    "menu": [
      {
        "id": "string",
        "original_name": "string",
        "canonical_name": "string (lowercase_with_underscores)",
        "name": "string",
        "category": "string",
        "normalized_category": "string",
        "sub_category": "string",
        "veg_nonveg": "Vegetarian | Non-Vegetarian | Eggetarian",
        "ingredients": ["array"],
        "normalized_ingredients": ["array of clean ingredients"],
        "allergens": ["array"],
        "price": number,
        "currency": "string",
        "description": "string",
        "pairings": ["array"],
        "halal": boolean,
        "jain_available": boolean,
        "availability": {
          "available": true,
          "seasonal": false,
          "meal_slots": ["Lunch", "Dinner"],
          "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        },
        "confidence_score": 0.95
      }
    ]
  }
}
"""

# ==================== LLM CLIENTS ====================

if PROVIDER == "grok":
    from openai import OpenAI
    client = OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    MODEL = "grok-4.3"          # or grok-3, etc.

elif PROVIDER == "openai":
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL = "gpt-4o"

elif PROVIDER == "anthropic":
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    MODEL = "claude-3-5-sonnet-20241022"
else:
    raise ValueError("Invalid PROVIDER")

# ==================== MAIN FUNCTION ====================

def extract_menu_to_json(image_path: str):
    base64_image = encode_image(image_path)
    filename = Path(image_path).name

    if PROVIDER in ["grok", "openai"]:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": get_user_prompt()},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000,
            temperature=0.0
        )
        json_text = response.choices[0].message.content

    elif PROVIDER == "anthropic":
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            temperature=0.0,
            system=get_system_prompt(),
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": get_user_prompt()},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }]
        )
        json_text = response.content[0].text

    # Clean and parse JSON
    json_text = json_text.strip()
    if json_text.startswith("```json"):
        json_text = json_text.split("```json")[1].split("```")[0].strip()

    try:
        data = json.loads(json_text)
        # Save output
        output_path = f"output_{Path(image_path).stem}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Success! JSON saved to: {output_path}")
        return data
    except Exception as e:
        print("❌ JSON parsing failed:", e)
        print("Raw output:", json_text[:500])
        return None


# ================ RUN ================
if __name__ == "__main__":
    extract_menu_to_json(IMAGE_PATH)
