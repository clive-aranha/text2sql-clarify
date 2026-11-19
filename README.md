# Text-to-SQL with a Clarification Engine

[![CI](https://github.com/clive-aranha/text2sql-clarify/actions/workflows/ci.yml/badge.svg)](https://github.com/clive-aranha/text2sql-clarify/actions/workflows/ci.yml)

Ask questions about a database in plain English. If a question is ambiguous
(like "best customer"), the app asks a follow-up question instead of guessing.

**Status:** work in progress.

## How it works

1. An **analyzer** checks whether the question is clear, using the database schema and a business glossary.
2. If it is ambiguous, the app asks **one** clarifying question with concrete options.
3. A **SQL generator** writes the query.
4. A **validator** blocks anything that is not a safe, single SELECT.
5. The query runs as a **read-only** database user.

## Tech stack

Python, PostgreSQL, Pydantic, sqlglot, Docker, GitHub Actions, Groq (OpenAI-compatible API).
