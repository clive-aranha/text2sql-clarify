from pathlib import Path

import psycopg


def get_schema_text(dsn: str) -> tuple[str, set[str]]:
    query = """
        SELECT c.table_name,
               c.column_name,
               c.data_type,
               col_description(
                   format('public.%I', c.table_name)::regclass,
                   c.ordinal_position::int
               ) AS comment
        FROM information_schema.columns c
        WHERE c.table_schema = 'public'
        ORDER BY c.table_name, c.ordinal_position
    """
    tables: dict[str, list[str]] = {}
    with psycopg.connect(dsn) as conn:
        for table, column, dtype, comment in conn.execute(query):
            text = f"{column} {dtype}"
            if comment:
                text += f" /* {comment} */"
            tables.setdefault(table, []).append(text)
    schema = "\n".join(f"{t}({', '.join(cols)})" for t, cols in tables.items())
    return schema, set(tables)


def get_glossary() -> str:
    return Path(__file__).with_name("glossary.yaml").read_text(encoding="utf-8")
