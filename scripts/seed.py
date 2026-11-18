import os
import random
from datetime import date, timedelta

import psycopg
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

dsn = os.getenv(
    "ADMIN_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/shop",
)
today = date.today()

with psycopg.connect(dsn) as conn, conn.cursor() as cur:
    cur.execute(
        "TRUNCATE order_items, orders, products, customers RESTART IDENTITY CASCADE"
    )

    for _ in range(300):
        cur.execute(
            "INSERT INTO customers(name, email, country, signup_date, is_active) "
            "VALUES (%s, %s, %s, %s, %s)",
            (
                fake.name(),
                fake.unique.email(),
                fake.country(),
                today - timedelta(days=random.randint(0, 540)),
                random.random() > 0.15,
            ),
        )

    categories = ["Electronics", "Books", "Home", "Toys", "Apparel"]
    for _ in range(60):
        cur.execute(
            "INSERT INTO products(name, category, price) VALUES (%s, %s, %s)",
            (
                fake.word().title(),
                random.choice(categories),
                round(random.uniform(5, 500), 2),
            ),
        )

    for _ in range(2500):
        status = random.choices(
            ["placed", "shipped", "delivered", "cancelled", "refunded"],
            weights=[5, 10, 70, 10, 5],
        )[0]
        cur.execute(
            "INSERT INTO orders(customer_id, order_date, status, discount) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (
                random.randint(1, 300),
                today - timedelta(days=random.randint(0, 540)),
                status,
                random.choice([0, 0, 0, 5, 10]),
            ),
        )
        order_id = cur.fetchone()[0]
        for _ in range(random.randint(1, 4)):
            product_id = random.randint(1, 60)
            cur.execute(
                "INSERT INTO order_items(order_id, product_id, quantity, unit_price) "
                "SELECT %s, %s, %s, price FROM products WHERE id = %s",
                (order_id, product_id, random.randint(1, 5), product_id),
            )

    conn.commit()

print("Seeding complete")
