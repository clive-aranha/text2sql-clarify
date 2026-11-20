from datetime import date

import psycopg
from pydantic import BaseModel

from .config import settings
from .executor import run_query
from .llm import LLM
from .prompts import ANALYZER_SYSTEM, REPAIR_USER, SQL_SYSTEM
from .schema_context import get_glossary, get_schema_text
from .schemas import Ambiguity, Analysis, SQLDraft, Status
from .validator import UnsafeSQLError, validate


class Clarify(BaseModel):
    kind: str = "clarify"
    question: str
    ambiguities: list[Ambiguity]


class Answer(BaseModel):
    kind: str = "answer"
    sql: str
    explanation: str
    assumptions: list[str]
    columns: list[str]
    rows: list[list]


class Refusal(BaseModel):
    kind: str = "refusal"
    reason: str


class Failure(BaseModel):
    kind: str = "failure"
    reason: str


class Engine:
    def __init__(self, llm: LLM | None = None) -> None:
        self.llm = llm or LLM()
        self.schema, self.tables = get_schema_text(settings.database_url)
        self.glossary = get_glossary()

    def handle(
        self, question: str, clarifications: list[str] | None = None
    ) -> Clarify | Answer | Refusal | Failure:
        try:
            return self._handle(question, clarifications)
        except RuntimeError:
            return Failure(reason="The AI model had a temporary problem. Please try again.")

    def _handle(
        self, question: str, clarifications: list[str] | None = None
    ) -> Clarify | Answer | Refusal:
        clarifications = clarifications or []
        user_msg = question
        if clarifications:
            user_msg += "\n\nUser clarifications so far:\n" + "\n".join(
                f"- {c}" for c in clarifications
            )

        analysis = self.llm.structured(
            ANALYZER_SYSTEM.format(
                schema=self.schema, glossary=self.glossary, today=date.today()
            ),
            user_msg,
            Analysis,
        )

        if analysis.status == Status.OUT_OF_SCOPE:
            return Refusal(
                reason=analysis.clarifying_question
                or "That can't be answered from the available data."
            )

        if (
            analysis.status == Status.NEEDS_CLARIFICATION
            and analysis.ambiguities
            and not clarifications
        ):
            return Clarify(
                question=analysis.clarifying_question or "Could you clarify?",
                ambiguities=analysis.ambiguities,
            )

        return self._generate_and_run(analysis.refined_question or user_msg)

    def _generate_and_run(self, question: str) -> Answer | Refusal:
        system = SQL_SYSTEM.format(schema=self.schema, today=date.today())
        draft = self.llm.structured(system, question, SQLDraft)

        for attempt in range(2):
            try:
                safe_sql = validate(draft.sql, self.tables, settings.max_rows)
                columns, rows = run_query(safe_sql, settings.database_url)
                return Answer(
                    sql=safe_sql,
                    explanation=draft.explanation,
                    assumptions=draft.assumptions,
                    columns=columns,
                    rows=[list(r) for r in rows],
                )
            except (UnsafeSQLError, psycopg.Error) as e:
                if attempt == 1:
                    return Refusal(reason=f"Could not produce a valid query: {e}")
                draft = self.llm.structured(
                    system,
                    REPAIR_USER.format(error=e, question=question, sql=draft.sql),
                    SQLDraft,
                )
        return Refusal(reason="Unexpected failure")
