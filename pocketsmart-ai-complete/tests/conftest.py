import os
os.environ["USE_GEMINI"]="false"
os.environ["DATABASE_URL"]="sqlite:///./test_pocketsmart.db"
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(scope="session",autouse=True)
def database():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    try: os.remove("test_pocketsmart.db")
    except FileNotFoundError: pass

@pytest.fixture
def client():
    with TestClient(app) as c: yield c

@pytest.fixture
def auth_client(client):
    client.post("/register",data={"name":"Test User","email":"test@example.com","password":"password123"},follow_redirects=False)
    r=client.post("/login",data={"email":"test@example.com","password":"password123"},follow_redirects=False)
    assert r.status_code==303
    assert client.cookies.get("access_token")
    return client
