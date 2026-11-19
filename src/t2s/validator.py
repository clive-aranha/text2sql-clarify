import sqlglot
from sqlglot import exp


class UnsafeSQLError(Exception):
    """Raised when generated SQL is not safe to run."""


BLOCKED_FUNCTIONS = {
    "pg_sleep",
    "pg_read_file",
    "pg_ls_dir",
    "lo_import",
    "lo_export",
    "dblink",
    "pg_terminate_backend",
}

FORBIDDEN_STATEMENTS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.Alter,
    exp.Command,
)


def validate(sql: str, allowed_tables: set[str], max_rows: int = 200) -> str:
    """Return a safe version of the SQL, or raise UnsafeSQLError."""
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except sqlglot.errors.ParseError as e:
        raise UnsafeSQLError(f"Could not parse SQL: {e}") from e

    if len(statements) != 1 or statements[0] is None:
        raise UnsafeSQLError("Exactly one SQL statement is allowed")

    tree = statements[0]

    if not isinstance(tree, (exp.Select, exp.Union)):
        raise UnsafeSQLError("Only SELECT queries are allowed")

    if tree.find(*FORBIDDEN_STATEMENTS):
        raise UnsafeSQLError("Data-changing statements are not allowed")

    for func in tree.find_all(exp.Anonymous):
        if func.name.lower() in BLOCKED_FUNCTIONS:
            raise UnsafeSQLError(f"Function not allowed: {func.name}")

    cte_names = {cte.alias for cte in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        if table.name not in allowed_tables and table.name not in cte_names:
            raise UnsafeSQLError(f"Table not allowed: {table.name}")

    if isinstance(tree, exp.Select) and not tree.args.get("limit"):
        tree = tree.limit(max_rows)

    return tree.sql(dialect="postgres")
