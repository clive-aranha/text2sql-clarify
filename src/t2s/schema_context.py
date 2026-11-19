from pathlib import Path

import psycopg


def get_schema_text(dsn: str) -> tuple[str, set[str]]:
    query = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """
    tables: dict[str, list[str]] = {}
    with psycopg.connect(dsn) as conn:
        for table, column, dtype in conn.execute(query):
            tables.setdefault(table, []).append(f"{column} {dtype}")
    text = "\n".join(f"{t}({', '.join(cols)})" for t, cols in tables.items())
    return text, set(tables)


def get_glossary() -> str:
    return Path(__file__).with_name("glossary.yaml").read_text(encoding="utf-8")
