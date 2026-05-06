from transformers import pipeline

# Load your LoRA fine-tuned local model
local_bot = pipeline("text-generation", model="./menu_bot_lora")

def local_generate(query: str, context: str):
    prompt = f"Customer asked: {query}\nRelevant menu items:\n{context}\nAnswer:"
    response = local_bot(prompt, max_length=150)
    return response[0]["generated_text"]
