import traceback
from fastapi.testclient import TestClient
from src.main import app

def test_err():
    try:
        c = TestClient(app)
        r = c.post('/api/chat/sessions', json={'user_id': '123e4567-e89b-12d3-a456-426614174000', 'title': 'Test'})
        print(r.status_code, r.text)
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    test_err()
