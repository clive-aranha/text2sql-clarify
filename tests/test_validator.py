import pytest

from t2s.validator import UnsafeSQLError, validate

TABLES = {"customers", "orders", "order_items", "products"}


def test_adds_limit_when_missing():
    assert "LIMIT 200" in validate("SELECT * FROM customers", TABLES)


def test_keeps_existing_limit():
    result = validate("SELECT * FROM customers LIMIT 5", TABLES)
    assert "LIMIT 5" in result
    assert "LIMIT 200" not in result


def test_allows_join_and_aggregate():
    sql = (
        "SELECT c.name, SUM(oi.quantity * oi.unit_price) AS revenue "
        "FROM customers c JOIN orders o ON o.customer_id = c.id "
        "JOIN order_items oi ON oi.order_id = o.id GROUP BY c.name"
    )
    assert "SELECT" in validate(sql, TABLES)


def test_allows_cte():
    sql = "WITH t AS (SELECT * FROM orders) SELECT COUNT(*) FROM t"
    assert "WITH" in validate(sql, TABLES)


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE customers",
        "DELETE FROM orders",
        "UPDATE customers SET name = 'x'",
        "SELECT 1; DROP TABLE orders",
        "SELECT * FROM pg_shadow",
        "SELECT pg_sleep(100)",
        "this is not sql",
    ],
)
def test_blocks_unsafe_sql(sql):
    with pytest.raises(UnsafeSQLError):
        validate(sql, TABLES)
