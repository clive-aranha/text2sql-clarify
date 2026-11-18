import psycopg

from t2s.config import settings

with psycopg.connect(settings.database_url) as conn:
    n = conn.execute("SELECT count(*) FROM customers").fetchone()[0]
    print("Customers visible to read-only user:", n)
    try:
        conn.execute("DELETE FROM customers")
        print("PROBLEM: delete was allowed!")
    except psycopg.errors.InsufficientPrivilege:
        print("Good: delete was blocked")
