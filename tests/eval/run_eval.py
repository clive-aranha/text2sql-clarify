import time
from decimal import Decimal
from pathlib import Path

import yaml

from t2s.config import settings
from t2s.engine import Answer, Clarify, Engine, Refusal
from t2s.executor import run_query


def normalize(rows):
    cleaned = []
    for row in rows:
        cleaned.append(
            tuple(
                round(float(v), 2)
                if isinstance(v, (int, float, Decimal)) and not isinstance(v, bool)
                else v
                for v in row
            )
        )
    return sorted(cleaned, key=lambda r: [str(x) for x in r])


def classify(result) -> str:
    if isinstance(result, Clarify):
        return "clarify"
    if isinstance(result, Answer):
        return "answer"
    if isinstance(result, Refusal):
        return "refuse"
    return "error"


def main() -> None:
    cases = yaml.safe_load(Path(__file__).with_name("cases.yaml").read_text(encoding="utf-8"))
    engine = Engine()
    rows_out = []

    for case in cases:
        question, expect = case["q"], case["expect"]
        try:
            result = engine.handle(question)
            got = classify(result)
        except Exception as e:  # keep going if one case crashes
            result, got = None, "error"
            print("  error:", e)

        correct = got == expect
        if expect == "answer" and got == "answer":
            _, gold_rows = run_query(case["gold_sql"], settings.database_url)
            correct = normalize(result.rows) == normalize(gold_rows)

        rows_out.append({"q": question, "expect": expect, "got": got, "correct": correct})
        print(("PASS" if correct else "FAIL"), f"[expected {expect}, got {got}]", question)
        time.sleep(1)

    def rate(group, predicate):
        items = [r for r in rows_out if r["expect"] == group]
        hits = [r for r in items if predicate(r)]
        return len(hits), len(items)

    recall = rate("clarify", lambda r: r["got"] == "clarify")
    answer_ok = rate("answer", lambda r: r["correct"])
    false_ask = rate("answer", lambda r: r["got"] == "clarify")
    refused = rate("refuse", lambda r: r["got"] == "refuse")
    total_ok = sum(r["correct"] for r in rows_out)

    lines = [
        "| Metric | Result |",
        "|---|---|",
        f"| Clarification recall (asked when it should) | {recall[0]}/{recall[1]} |",
        f"| Execution accuracy on clear questions | {answer_ok[0]}/{answer_ok[1]} |",
        f"| False clarifications (asked when it should not) | {false_ask[0]}/{false_ask[1]} |",
        f"| Correct refusals | {refused[0]}/{refused[1]} |",
        f"| Overall | {total_ok}/{len(rows_out)} |",
    ]
    report = "\n".join(lines)
    print("\n" + report)
    Path("eval_report.md").write_text(report + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
