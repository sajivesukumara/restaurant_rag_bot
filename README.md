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

# Final Restaurant Menu JSON Schema

| Field                          | Type                     | Description                                                                 | Why Useful                                                                 | Example |
|--------------------------------|--------------------------|-----------------------------------------------------------------------------|----------------------------------------------------------------------------|---------|
| `restaurant.id`                | string                   | Unique identifier for the restaurant                                        | Tracking and deduplication of restaurants                                  | `tanjore_001` |
| `restaurant.name`              | string                   | Name of the restaurant                                                      | Display and identification                                                 | `Tanjore North Indian Cuisine` |
| `restaurant.address`           | string                   | Physical address of the restaurant                                          | Location-based services and context                                        | `151 Pinnacle Street, Belleville, Ontario` |
| `restaurant.cuisine_type`      | array[string]            | List of cuisine types (supports multi-cuisine)                              | Accurate representation of restaurants offering multiple cuisines          | `["North Indian", "South Indian"]` |
| `restaurant.source`            | string                   | Source of the menu data (e.g. Image, Website)                               | Data lineage and quality tracking                                          | `Menu Image` |
| `restaurant.source_file`       | string                   | Original filename or image source                                           | Traceability back to original menu image                                   | `Tanjore-North-Indian-Cuisine-Menu-1-1.jpg` |
| `restaurant.menu`              | array                    | List of all menu items                                                      | Core data structure containing all dishes                                  | `[ {menu item objects} ]` |
| **Menu Item Fields**           |                          |                                                                             |                                                                            |         |
| `menu[].id`                    | string                   | Unique ID for each menu item                                                | Item tracking and referencing                                              | `tanjore_001` |
| `menu[].name`                  | string                   | Name of the dish                                                            | Core identifier for search and display                                     | `Paneer Mattar` |
| `menu[].category`              | string                   | Main category                                                               | Menu organization and filtering                                            | `Vegetables` |
| `menu[].sub_category`          | string                   | Specific subcategory                                                        | Fine-grained classification                                                | `Curry` |
| `menu[].veg_nonveg`            | string                   | Vegetarian / Non-Vegetarian classification                                  | Dietary filtering                                                          | `Vegetarian` |
| `menu[].dietary_tags`          | array[string]            | Additional dietary preferences                                              | Advanced filtering (vegan, gluten-free, etc.)                              | `["vegetarian", "gluten-free"]` |
| `menu[].ingredients`           | array[string]            | List of main ingredients                                                    | Allergen detection, recipe generation, nutrition                           | `["paneer", "green peas"]` |
| `menu[].allergens`             | array[string]            | List of allergens                                                           | Food safety and user health                                                | `["dairy"]` |
| `menu[].price`                 | number                   | Price of the item                                                           | Pricing analysis and comparison                                            | `9.99` |
| `menu[].currency`              | string                   | Currency code                                                               | Multi-currency support                                                     | `CAD` |
| `menu[].description`           | string                   | Short description of the dish                                               | NLP, embeddings, and user display                                          | `Green peas & cottage cheese...` |
| `menu[].pairings`              | array[string]            | Recommended food/drink pairings                                             | Recommendation and cross-selling                                           | `["garlic naan", "raita"]` |
| `menu[].halal`                 | boolean                  | Halal availability                                                          | Religious dietary compliance                                               | `false` |
| `menu[].jain_available`        | boolean                  | Jain version availability                                                   | Strict vegetarian filtering                                                | `false` |
| `menu[].availability`          | object                   | Structured availability information                                         | Time-based, seasonal, and day-wise filtering                               | `{ "available": true, "meal_slots": ["Lunch", "Dinner"], ... }` |


## Enhanced Menu Item JSON Schema

```
{
  "restaurant": {
    "id": "string",
    "name": "string",
    "address": "string",
    "cuisine_type": ["array of strings"],
    "source": "string",
    "source_file": "string",
    "menu": [
      {
        "id": "string",
        "name": "string",
        "category": "string",
        "sub_category": "string",
        "veg_nonveg": "string",
        "dietary_tags": ["array"],
        "ingredients": ["array"],
        "allergens": ["array"],
        "price": number,
        "currency": "string",
        "description": "string",
        "pairings": ["array"],
        "halal": boolean,
        "jain_available": boolean,
        "availability": {
          "available": boolean,
          "seasonal": boolean,
          "season_name": "string | null",
          "meal_slots": ["array"],
          "days": ["array"]
        },
      }
    ]
  }
}
```
Sample Data: test/data/tanjaor-menu1.json, test/data/japanese-menu1.json


|Approach | How It Works | Pros| Cons | Recommended For|
|---------|--------------|-----|------|----------------|
|1. LLM-based Filling (Current)| You give the raw/existing JSON to an LLM (like me), and I intelligently fill the new normalization fields. | Fast, smart, understands context, good quality | Slightly expensive at scale, less consistent | Early stage, small-medium datasets, high quality
|2. Normalization Script | A Python script reads previous JSON → applies rules + optional LLM calls → outputs new enriched JSON.|"Scalable, reproducible, cheap, consistent | Requires development effort | Large-scale production dataset|

Assisted by : Microsoft Copilot, Grok
