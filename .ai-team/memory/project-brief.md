---
title: Project Brief
tags:
  - ai-team/memory
  - context
status: active
---

# Project Brief

> Keep this file short. It is loaded by every agent, so every stale sentence costs tokens and can cause mistakes.

## Project Identity

- Project name: 售后退款决策 Agent
- Current purpose: 面向在线教育售后场景的可运行 MVP，用 RAG + Tool Calling + LangGraph 编排 + Human-in-the-loop 生成有证据的退款处理建议。
- Repository root: `D:/yangjw/workspace/refund-decision-agent`
- Working directory: `D:/yangjw/workspace/refund-decision-agent`

## Technical Context

- Java service: Java 21, Spring Boot 3.2, JPA, MySQL, Redis, Flyway, deterministic refund eligibility rules.
- Python service: FastAPI, LangGraph, Pydantic v2, OpenAI-compatible LLM client, Elasticsearch BM25 retrieval, Redis Streams worker/events.
- Runtime: local Docker Compose for MySQL/Redis/Elasticsearch plus local Java/Python processes.
- Python environment: `D:/yangjw/software/Miniconda/envs/refund-agent/python.exe`.

## Project Structure

- `java-service/`: deterministic business base, domain model, REST APIs, refund eligibility checks.
- `python-agent/`: Agent workflow, nodes, ports/adapters, LLM client, RAG retrieval, Redis Streams, tests.
- `docs/`: architecture, development, security, evaluation report, resume draft.
- `tests/`: seed dataset and supporting test material.
- `.ai-team/`: product memory, task cards, run evidence, collaboration state.

## Default Commands

- Java test: `cd java-service; mvn test`
- Python test: `cd python-agent; D:/yangjw/software/Miniconda/envs/refund-agent/python.exe -m pytest`
- Python compile: `cd python-agent; D:/yangjw/software/Miniconda/envs/refund-agent/python.exe -m compileall app`
- AI Team status: `powershell -NoProfile -ExecutionPolicy Bypass -File .ai-team/scripts/Get-AiTeamStatus.ps1`

## Current State

- MVP feature phases 0-6 are implemented.
- Current focus is polish, verification, status consistency, demo readiness, and interview-quality evidence.
- Real API keys must stay only in local ignored env files, especially `python-agent/.env`.
