from t2s.engine import Answer, Clarify, Engine, Failure, Refusal
from t2s.schemas import Ambiguity, Analysis, Option, SQLDraft, Status


class FakeLLM:
    """Returns pre-written answers instead of calling a real model."""

    def __init__(self, analysis: Analysis, drafts: list[SQLDraft] | None = None):
        self.analysis = analysis
        self.drafts = list(drafts or [])

    def structured(self, system, user, model_cls, retries=2):
        if model_cls is Analysis:
            return self.analysis
        return self.drafts.pop(0)


GOOD = SQLDraft(sql="SELECT COUNT(*) AS n FROM customers", explanation="Counts customers")
BAD = SQLDraft(sql="DROP TABLE customers", explanation="Bad query")

AMBIGUOUS = Analysis(
    status=Status.NEEDS_CLARIFICATION,
    ambiguities=[
        Ambiguity(
            term="best customer",
            reason="No metric given",
            options=[
                Option(label="Revenue", resolves_to="Highest total revenue"),
                Option(label="Orders", resolves_to="Most orders"),
            ],
        )
    ],
    clarifying_question="Which metric?",
    confidence=0.9,
)

READY = Analysis(status=Status.READY, refined_question="Count customers", confidence=0.99)
OUT_OF_SCOPE = Analysis(
    status=Status.OUT_OF_SCOPE, clarifying_question="No cost data", confidence=0.99
)


def test_ambiguous_question_returns_clarification():
    result = Engine(FakeLLM(AMBIGUOUS)).handle("best customer?")
    assert isinstance(result, Clarify)
    assert result.question == "Which metric?"
    assert len(result.ambiguities[0].options) == 2


def test_never_asks_twice_after_user_answered():
    engine = Engine(FakeLLM(AMBIGUOUS, [GOOD]))
    result = engine.handle("best customer?", ["Highest total revenue"])
    assert isinstance(result, Answer)


def test_clear_question_runs_query():
    result = Engine(FakeLLM(READY, [GOOD])).handle("How many customers?")
    assert isinstance(result, Answer)
    assert result.rows == [[300]]


def test_out_of_scope_is_refused():
    result = Engine(FakeLLM(OUT_OF_SCOPE)).handle("profit margin?")
    assert isinstance(result, Refusal)


def test_unsafe_sql_is_repaired_once():
    result = Engine(FakeLLM(READY, [BAD, GOOD])).handle("How many customers?")
    assert isinstance(result, Answer)


def test_unsafe_sql_twice_is_refused():
    result = Engine(FakeLLM(READY, [BAD, BAD])).handle("How many customers?")
    assert isinstance(result, Refusal)


class BrokenLLM:
    def structured(self, *args, **kwargs):
        raise RuntimeError("model unavailable")


def test_llm_failure_is_handled_gracefully():
    result = Engine(BrokenLLM()).handle("anything")
    assert isinstance(result, Failure)
