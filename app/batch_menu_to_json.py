import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import time

load_dotenv()

# ====================== CONFIGURATION ======================
PROVIDER = "grok"          # Options: "grok", "openai", "anthropic"

IMAGE_FOLDER = "menu_images"          # Folder containing your menu JPGs
OUTPUT_FOLDER = "output_json"         # Where JSON files will be saved

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ===========================================================

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def get_system_prompt():
    return "You are an expert at extracting restaurant menus into structured JSON format. Be precise with names, prices, categories, and ingredients."

def get_user_prompt(filename: str):
    return f"""Extract all menu items from this restaurant menu image.

Return ONLY valid JSON in this exact structure (no explanations, no markdown):

{{
  "restaurant": {{
    "id": "string",
    "name": "string",
    "address": "string or null",
    "cuisine_type": ["array of strings"],
    "source": "Menu Image",
    "source_file": "{filename}",
    "menu": [
      {{
        "id": "string",
        "original_name": "string",
        "canonical_name": "string (lowercase_with_underscores)",
        "name": "string",
        "category": "string",
        "normalized_category": "string",
        "sub_category": "string",
        "veg_nonveg": "Vegetarian | Non-Vegetarian | Eggetarian",
        "ingredients": ["array"],
        "normalized_ingredients": ["array"],
        "allergens": ["array"],
        "price": number,
        "currency": "string",
        "description": "string",
        "pairings": ["array"],
        "halal": boolean,
        "jain_available": boolean,
        "availability": {{
          "available": true,
          "seasonal": false,
          "meal_slots": ["Lunch", "Dinner"],
          "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        }},
        "confidence_score": 0.9
      }}
    ]
  }}
}}"""

# ===================== LLM CLIENT =====================
if PROVIDER == "grok":
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
    MODEL = "grok-4.3"   # or grok-3-vision
elif PROVIDER == "openai":
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL = "gpt-4o"
elif PROVIDER == "anthropic":
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    MODEL = "claude-3-5-sonnet-20241022"

# ===================== MAIN BATCH FUNCTION =====================
def process_menu_image(image_path: Path):
    try:
        base64_image = encode_image(image_path)
        filename = image_path.name

        print(f"Processing: {filename}")

        if PROVIDER in ["grok", "openai"]:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": get_system_prompt()},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": get_user_prompt(filename)},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                max_tokens=4000,
                temperature=0.1
            )
            json_text = response.choices[0].message.content

        elif PROVIDER == "anthropic":
            response = client.messages.create(
                model=MODEL,
                max_tokens=4000,
                temperature=0.1,
                system=get_system_prompt(),
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": get_user_prompt(filename)},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}}
                    ]
                }]
            )
            json_text = response.content[0].text

        # Clean JSON response
        json_text = json_text.strip()
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].strip()

        data = json.loads(json_text)

        # Save output
        output_path = Path(OUTPUT_FOLDER) / f"{image_path.stem}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved: {output_path.name}")
        return True

    except Exception as e:
        print(f"❌ Failed {image_path.name}: {e}")
        return False


# ===================== RUN BATCH =====================
if __name__ == "__main__":
    # Get all image files
    supported_formats = ['*.jpg', '*.jpeg', '*.png']
    image_files = []
    for fmt in supported_formats:
        image_files.extend(Path(IMAGE_FOLDER).glob(fmt))

    if not image_files:
        print(f"No images found in '{IMAGE_FOLDER}' folder.")
        exit()

    print(f"Found {len(image_files)} menu images. Starting batch processing...\n")

    success_count = 0
    for image_path in tqdm(image_files):
        if process_menu_image(image_path):
            success_count += 1
        time.sleep(1.5)  # Avoid rate limits

    print("\n" + "="*50)
    print(f"Batch Processing Completed!")
    print(f"Successfully processed: {success_count}/{len(image_files)} images")
    print(f"Output folder: ./{OUTPUT_FOLDER}/")
    print("="*50)
