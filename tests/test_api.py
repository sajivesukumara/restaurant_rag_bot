from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_local_only():
  response = client.post("/chat", params={"query": " Paneer butter masala ingrediants", "use_cloud": False})
  assert response.status_code == 200
  assert "answer" in response.json()

def test_chat_cloud():
  response = client.post("/chat", params = {"query": "Suggest a 3-course vegetarian meal under 500", "use_cloud": True})
  assert response.status_code == 200
  assert "answer" in response.json()
  
                         
