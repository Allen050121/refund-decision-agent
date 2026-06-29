---
title: Repo Map
tags:
  - ai-team/index
  - repo-map
status: active
---

# Repo Map

> Compact project index for Codex and Claude. Keep this short and update it when structure changes.

## Project Shape

- Type: two-service backend MVP for refund decision support.
- Main languages: Java 21 and Python 3.13 in conda env.
- Framework/runtime: Spring Boot 3.2, FastAPI, LangGraph, Pydantic v2.
- Package managers: Maven for Java, `requirements.txt` + conda Python for Python.

## Important Directories

- `java-service/src/main/java/com/example/aftersale/`: Java domain, application services, persistence adapters, controllers, DTOs.
- `java-service/src/main/resources/`: Spring config, Flyway migrations, seed/config resources.
- `python-agent/app/agent/`: LangGraph state, graph, and node implementations.
- `python-agent/app/infrastructure/`: Java API client, LLM client, retrieval, Redis Streams, observability.
- `python-agent/app/tests/`: Python regression, graph, node, retrieval, Redis, security, and API tests.
- `python-agent/data/`: rules and evaluation/test data.
- `docs/`: architecture, development, security, evaluation report, resume draft.

## Entry Points

- Java service: `java-service/src/main/java/com/example/aftersale/AftersaleServiceApplication.java`
- Java refund API: `java-service/src/main/java/com/example/aftersale/interfaces/controller/RefundQueryController.java`
- Python API: `python-agent/app/main.py`
- Python workflow: `python-agent/app/agent/graph.py`
- Python nodes: `python-agent/app/agent/nodes/__init__.py`

## Data / State

- Java owns deterministic business facts and refund eligibility.
- Python Agent calls Java APIs and does not decide final refund authority by itself.
- RAG rules are retrieved from Elasticsearch/BM25 and backed by `python-agent/data/refund_rules.json`.
- Redis Streams are used for async task execution and progress/event publishing.
- AI Team state lives in `.ai-team/state/tasks.json`, `.ai-team/state/runs.json`, and `.ai-team/state/collaboration.json`.

## Tests And Verification

- Java: `cd java-service; mvn test`
- Python: `cd python-agent; D:/yangjw/software/Miniconda/envs/refund-agent/python.exe -m pytest`
- Current baseline on 2026-06-29: Java build success, Python `88 passed`.

## Deployment

- Local/demo deployment uses Docker Compose for MySQL, Redis, Elasticsearch, Java service, and Python Agent.
- Secrets belong in ignored `.env` files only; never commit `python-agent/.env`.

## Notes For Agents

- Read this map before broad repository searches.
- Prefer task cards and run evidence over chat history.
- For new optimization work, create or claim a new AI Team task instead of rewriting completed phase tasks.
