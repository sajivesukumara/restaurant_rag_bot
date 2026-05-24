Given this menu JSON:
[
  {"name": "paneer butter masala", "category": "Main course|Veg|Curry", "ingredients": "Paneer, butter, tomato, cream, spices", "price": "250"},
  {"name": "veg pulao", "category": "Main course|Veg|Rice", "ingredients": "Rice, peas, carrot, spices", "price": "160"}
]

Generate 10 training examples in JSONL format where each entry has:
 - instruction: a customer query about the menu
 - input alway empty
 - output: the correct answer based on the menu
 - 
