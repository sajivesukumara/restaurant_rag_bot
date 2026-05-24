# restaurant_rag_bot

```
restaurant_rag_bot/
├── ocr/
│   └── cloud_ocr.py
├── parser/
│   └── menu_parser.py
├── embeddings/
│   └── embedder.py
├── vectordb/
│   └── vector_store.py
├── rag/
│   └── query_engine.py
├── llm/
│   ├── local_llm.py
│   └── cloud_llm.py
├── app/
│   ├── main.py
│   ├── routes.py
│   └── services.py
└── tests/
    └── test_api.py
```

## Deployment Options

* Local Testing : Run ```uvicorn app.main:app --reload``` and test endpoints
* Cloud Deployment: Upload the zip of the repository to a server (AWS EC2, Asure VM, GCP Compute) and unzip. Install requirements, then run the uvicorn.
* Containerzation: Use the dockerfile to build and deploy

```
docker-compose up --build

http://localhost:8000

curl -X POST "http://localhost:8000/upload_menu" -F "file=@data/simple_menu.pdf"

curl -X POST "http://localhost:8000/chat" -d "query=Show me vegetarian dishes under 200"

```

## Use local vector DB
Use open-source models (sentence-transformers, InstructorXL) instead of cloud embeddings.


## Menu Fields - The json key fields that should be expected from the LLM to respond with

# Enhanced Menu Item JSON Schema

| Field                  | Type                     | Description                                                                 | Why Useful                                                                 | Example |
|------------------------|--------------------------|-----------------------------------------------------------------------------|----------------------------------------------------------------------------|---------|
| `id`                   | string                   | Unique identifier for the menu item                                         | Enables tracking, deduplication, and referencing across datasets          | `tanjore_001` |
| `name`                 | string                   | Name of the dish                                                            | Core identifier for search, display, and model training                   | `Paneer Mattar` |
| `category`             | string                   | Main category of the item                                                   | Helps in hierarchical classification and menu filtering                   | `Vegetables` |
| `sub_category`         | string                   | More specific subcategory                                                   | Improves fine-grained classification and recommendation systems           | `Curry` |
| `veg_nonveg`           | string                   | Dietary classification (Veg / Non-Veg)                                      | Essential for dietary preference filtering                                | `Vegetarian` |
| `dietary_tags`         | array[string]            | Additional dietary labels                                                   | Supports advanced filtering (vegan, gluten-free, etc.)                    | `["vegetarian", "gluten-free"]` |
| `ingredients`          | array[string]            | List of main ingredients                                                    | Critical for allergen detection, recipe generation, and nutritional analysis | `["paneer", "green peas", "spices"]` |
| `allergens`            | array[string]            | List of common allergens                                                    | Vital for food safety, user health, and compliance                        | `["dairy"]` |
| `price`                | number                   | Price of the item                                                           | Enables pricing analysis, value comparison, and dynamic pricing models    | `9.99` |
| `currency`             | string                   | Currency code                                                               | Supports multi-currency datasets and international use                    | `CAD` |
| `calories`             | number                   | Estimated calories per serving                                              | Important for nutrition apps and health-based recommendations             | `380` |
| `protein_g`            | number                   | Protein content in grams                                                    | Supports macronutrient analysis and fitness/diet apps                     | `18` |
| `carbs_g`              | number                   | Carbohydrate content in grams                                               | Key for nutritional modeling and diabetic-friendly filtering              | `42` |
| `fat_g`                | number                   | Fat content in grams                                                        | Completes macronutrient profile for ML-based nutrition prediction         | `22` |
| `portion`              | object                   | Portion details (`size`, `serves`)                                          | Helps in quantity-based analysis and cost-per-serving calculations        | `{ "size": "Full Plate", "serves": 2 }` |
| `spiciness_level`      | integer (0-5)            | Spiciness level                                                             | Useful for preference matching and personalization                       | `2` |
| `preparation_time`     | string                   | Approximate preparation time                                                 | Important for operational efficiency and kitchen scheduling models        | `18 minutes` |
| `popularity_score`     | number (0-5)             | Estimated popularity rating                                                 | Powers recommendation engines and trend analysis                          | `4.7` |
| `description`          | string                   | Short descriptive text                                                      | Useful for NLP tasks, embeddings, and text generation                     | `Green peas & cottage cheese in spiced gravy` |
| `pairings`             | array[string]            | Suggested food/drink pairings                                               | Enhances recommendation systems and cross-selling models                  | `["garlic naan", "raita"]` |
| `image_url`            | string                   | Path or URL to the dish image                                               | Enables multimodal (vision + language) model training                     | `images/paneer_mattar.jpg` |
| `restaurant_name`      | string                   | Name of the restaurant                                                      | Provides context and supports restaurant-specific analysis                | `Tanjore North Indian Cuisine` |
| `cuisine_type`         | string                   | Type of cuisine                                                             | Critical for cuisine classification and cultural context                  | `North Indian` |
| `availability`         | object                   | Structured availability information                                         | Allows time-based and seasonal filtering in apps                          | `{ "available": true, "meal_slots": ["Lunch", "Dinner"], ... }` |
| `tags`                 | array[string]            | Custom tags for the item                                                    | Flexible multi-label classification and marketing insights                | `["popular", "creamy"]` |
| `halal`                | boolean                  | Whether the dish is Halal                                                   | Important for religious dietary compliance                                | `false` |
| `jain_available`       | boolean                  | Whether Jain version (no onion/garlic) is available                         | Supports strict vegetarian/Jain dietary filtering                         | `false` |
| `source`               | string                   | Origin of the data (image, website, etc.)                                   | Crucial for data lineage, auditing, and quality control                   | `Menu Image - Tanjore` |
| `search_text`          | string                   | Combined searchable text for full-text / vector search                      | Improves search performance and semantic search capabilities              | `paneer mattar vegetarian curry peas cheese north indian` |


## JSON Schema

```
{
  "id": "string",
  "name": "string",
  "category": "string",
  "sub_category": "string",
  "veg_nonveg": "Vegetarian | Non-Vegetarian | Eggetarian",
  "dietary_tags": ["array"],
  "ingredients": ["array of strings"],
  "allergens": ["array"],
  "price": number,
  "currency": "string",
  "calories": number,
  "protein_g": number,
  "carbs_g": number,
  "fat_g": number,
  "portion": {
    "size": "string",
    "serves": number
  },
  "spiciness_level": number,
  "preparation_time": "string",
  "popularity_score": number,
  "description": "string",
  "pairings": ["array of strings"],
  "image_url": "string",
  "restaurant_name": "string",
  "cuisine_type": "string",
  "availability": {
    "available": true,
    "seasonal": false,
    "season_name": null,
    "meal_slots": ["array"],
    "days": ["array"]
  },
  "tags": ["array"],
  "halal": boolean,
  "jain_available": boolean,
  "source": "string",
  "search_text": "string"
}
```
Sample Data: test/data/tanjaor-menu1.json, test/data/japanese-menu1.json



Assisted by : Microsoft Copilot, Grok
