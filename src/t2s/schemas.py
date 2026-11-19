from enum import Enum

from pydantic import BaseModel, Field


class Status(str, Enum):
    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"
    OUT_OF_SCOPE = "out_of_scope"


class Option(BaseModel):
    label: str = Field(description="Short choice shown to the user, e.g. 'Highest total revenue'")
    resolves_to: str = Field(description="Unambiguous restatement of the question if this is chosen")


class Ambiguity(BaseModel):
    term: str = Field(description="The unclear word or phrase, e.g. 'best customer'")
    reason: str = Field(description="Why it is unclear")
    options: list[Option] = Field(min_length=2, max_length=4)


class Analysis(BaseModel):
    status: Status
    ambiguities: list[Ambiguity] = []
    clarifying_question: str | None = None
    refined_question: str | None = Field(
        default=None, description="The question with all assumptions made explicit"
    )
    confidence: float = Field(ge=0, le=1)


class SQLDraft(BaseModel):
    sql: str
    explanation: str
    assumptions: list[str] = []
