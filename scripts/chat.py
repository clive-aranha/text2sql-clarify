from t2s.engine import Answer, Clarify, Engine, Refusal

engine = Engine()
print("Text-to-SQL with clarification. Type 'quit' to exit.")

while True:
    question = input("\nAsk a question: ").strip()
    if question.lower() in {"quit", "exit"}:
        break
    if not question:
        continue

    clarifications: list[str] = []
    while True:
        result = engine.handle(question, clarifications)

        if isinstance(result, Clarify):
            print("\nI need to check something first.")
            for amb in result.ambiguities:
                print(f"\n'{amb.term}': {amb.reason}")
                for i, opt in enumerate(amb.options, 1):
                    print(f"  {i}. {opt.label}")
                choice = input("Pick a number, or type your own answer: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(amb.options):
                    clarifications.append(amb.options[int(choice) - 1].resolves_to)
                else:
                    clarifications.append(choice)
            continue

        if isinstance(result, Answer):
            print("\nSQL:", result.sql)
            print("What it does:", result.explanation)
            if result.assumptions:
                print("Assumptions:")
                for a in result.assumptions:
                    print("  -", a)
            print("\nColumns:", result.columns)
            for row in result.rows[:10]:
                print("  ", row)
            if len(result.rows) > 10:
                print(f"   ... {len(result.rows)} rows total")
        elif isinstance(result, Refusal):
            print("\nCan't do that:", result.reason)
        break
