# 0001 — Backend em Python com FastAPI

**Data:** 25/09/2026 · **Status:** aceita

## Contexto
Existiam dois documentos de arquitetura v0.1 com stacks diferentes:
um recomendava .NET, o outro Python/FastAPI.

## Decisão
Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL,
conforme a Arquitetura Técnica v0.1 (documento canônico 06).

## Motivos
- É o documento mais detalhado, inclusive no motor de matching.
- O ecossistema de IA (embeddings, visão computacional) é nativo em Python.
- Análises independentes (Claude e ChatGPT) chegaram à mesma conclusão.

## Consequências
O documento .NET foi movido para `docs/historico/`.
Redis, Celery e armazenamento de objetos entram só quando uma fase precisar deles.
