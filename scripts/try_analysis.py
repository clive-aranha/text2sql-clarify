from datetime import date

from t2s.config import settings
from t2s.llm import LLM
from t2s.prompts import ANALYZER_SYSTEM
from t2s.schema_context import get_glossary, get_schema_text
from t2s.schemas import Analysis

schema, _tables = get_schema_text(settings.database_url)
system = ANALYZER_SYSTEM.format(schema=schema, glossary=get_glossary(), today=date.today())
llm = LLM()

questions = [
    "Show me last month's best customer",
    "How many new customers signed up last month?",
    "What was our revenue last quarter?",
    "What is our profit margin?",
    "Delete all cancelled orders",
]

for q in questions:
    a = llm.structured(system, q, Analysis)
    print("Q:", q)
    print("   status:", a.status.value)
    if a.clarifying_question:
        print("   asks:", a.clarifying_question)
    for amb in a.ambiguities:
        print("   options:", [o.label for o in amb.options])
    if a.refined_question:
        print("   refined:", a.refined_question)
    print()
