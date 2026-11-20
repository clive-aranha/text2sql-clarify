import sys

from t2s.engine import Clarify, Engine

question = " ".join(sys.argv[1:])
result = Engine().handle(question)
print("Result type:", type(result).__name__)
if isinstance(result, Clarify):
    print("It asked:", result.question)
    for amb in result.ambiguities:
        print("Term:   ", amb.term)
        print("Reason: ", amb.reason)
        print("Options:", [o.label for o in amb.options])
