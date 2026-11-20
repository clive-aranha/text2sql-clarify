from fastapi.testclient import TestClient

from t2s import api
from t2s.engine import Refusal

client = TestClient(api.app)


class FakeEngine:
    def handle(self, question, clarifications=None):
        return Refusal(reason="not allowed")


def test_health():
    assert client.get("/health").json() == {"ok": True}


def test_ask_returns_engine_result(monkeypatch):
    monkeypatch.setattr(api, "get_engine", lambda: FakeEngine())
    response = client.post("/ask", json={"question": "delete everything"})
    assert response.status_code == 200
    assert response.json()["kind"] == "refusal"
