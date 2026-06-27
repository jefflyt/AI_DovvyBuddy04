---
name: dovvybuddy-adk-rag-dev
description: Best practices and guidelines for writing, testing, and debugging DovvyBuddy RAG pipelines and ADK multi-agent orchestrator graphs.
---

# DovvyBuddy RAG & ADK Development Guide

This skill provides guidelines and recipes for designing, developing, and verifying DovvyBuddy RAG features and agent orchestrations.

## 1. 🗄️ Database Session Rules

- **Parallel Querying:** When querying PostgreSQL concurrently (e.g., combining semantic search and keyword search in `asyncio.gather`), **never** reuse a single SQLAlchemy `AsyncSession`. Always spawn separate sessions from the session factory:
  ```python
  session_maker = get_session()
  async with session_maker() as session:
      # Perform database operations
  ```
- **Initialization:** Ensure `init_db()` is called once before any database access. In test scripts, use the `db_engine` session fixture.

## 2. 🧪 Testing Guardrails (Legacy vs. Native ADK)

- **Disable Native Graph in Router Tests:** When writing integration tests for legacy routing paths or mock agent returns, disable the native ADK graph executor to prevent live API requests and 503 errors:
  ```python
  @pytest.fixture(autouse=True)
  def disable_native_graph(monkeypatch):
      monkeypatch.setattr("app.core.config.settings.enable_adk_native_graph", False)
  ```
- **Grounded Citations Mocking:** If verifying that citations flow into final responses, ensure the mock `AgentContext` contains both `rag_citations` and a truthy `rag_context` string:
  ```python
  context = AgentContext(
      query="...",
      conversation_history=[],
      rag_context="Dummy verified info", # Essential!
      metadata={"has_rag": True, "rag_citations": ["some_file.md"]}
  )
  ```

## 3. 🔍 Static Analysis

- Run Python linting and imports sorting using:
  ```bash
  ruff check . --fix && ruff format .
  ```
