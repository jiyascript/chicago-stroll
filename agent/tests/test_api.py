from fastapi.testclient import TestClient
from app.api.server import app

def test_health():
    c=TestClient(app); assert c.get('/api/health').json()=={'status':'ok'}
