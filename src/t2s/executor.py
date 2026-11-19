import psycopg


def run_query(sql: str, dsn: str) -> tuple[list[str], list[tuple]]:
    """Run a validated SELECT query and return (column names, rows)."""
    with psycopg.connect(dsn) as conn:
        conn.read_only = True
        cur = conn.execute(sql)
        columns = [d.name for d in cur.description or []]
        return columns, cur.fetchall()
