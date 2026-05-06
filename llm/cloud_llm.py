import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cloud_generate(query: str, context: str):
    prompt = f"Customer asked: {query}\nRelevant menu items:\n{context}\nAnswer:"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a restaurant assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
  
