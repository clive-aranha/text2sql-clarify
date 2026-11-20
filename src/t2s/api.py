from fastapi import FastAPI
from pydantic import BaseModel

from .engine import Engine

app = FastAPI(title="Text-to-SQL with Clarification")

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = Engine()
    return _engine


class AskRequest(BaseModel):
    question: str
    clarifications: list[str] = []


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/ask")
def ask(req: AskRequest):
    return get_engine().handle(req.question, req.clarifications)
