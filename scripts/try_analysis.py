from t2s.llm import LLM
from t2s.schemas import Analysis

system = (
    "You decide whether a question about an online shop's database can be answered "
    "with ONE unambiguous SQL query. If a reasonable analyst could get materially "
    "different results (e.g. 'best' without a metric), set status to needs_clarification "
    "and list each ambiguity with 2-4 concrete options. Otherwise set status to ready."
)

for q in ["Show me last month's best customer", "How many customers are in India?"]:
    result = LLM().structured(system, q, Analysis)
    print("QUESTION:", q)
    print(result.model_dump_json(indent=2))
    print()
