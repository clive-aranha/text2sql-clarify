from datetime import date

from t2s.config import settings
from t2s.executor import run_query
from t2s.llm import LLM
from t2s.prompts import SQL_SYSTEM
from t2s.schema_context import get_schema_text
from t2s.schemas import SQLDraft
from t2s.validator import validate

schema, tables = get_schema_text(settings.database_url)
system = SQL_SYSTEM.format(schema=schema, today=date.today())
llm = LLM()

questions = [
    "How many new customers signed up in the previous full calendar month?",
    "Which customer had the highest total revenue in the previous full calendar month?",
    "What are the top 5 product categories by gross revenue, excluding cancelled and refunded orders?",
]

for q in questions:
    draft = llm.structured(system, q, SQLDraft)
    safe_sql = validate(draft.sql, tables, settings.max_rows)
    columns, rows = run_query(safe_sql, settings.database_url)
    print("Q:", q)
    print("SQL:", safe_sql)
    print("Assumptions:", draft.assumptions)
    print("Columns:", columns)
    for row in rows[:5]:
        print("  ", row)
    print()
