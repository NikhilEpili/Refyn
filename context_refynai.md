# Refyn AI — LLM Context Document

> **This file is the single source of truth for AI coding assistants (Cursor, GitHub Copilot, Codeium, etc.).**
> Load this file as context before generating any code, tests, configs, or documentation for this project.
> All architecture decisions, module boundaries, naming conventions, data schemas, and business logic defined here are authoritative and must be respected in all generated output.

---

## 0. Quick Reference Card (read this first)

| Property | Value |
|---|---|
| **Project name** | Refyn AI |
| **Tagline** | The code reviewer that learns your team |
| **What it is** | A GitHub App that performs AI-powered PR reviews, personalised to each team via RLHF |
| **Primary language** | Python 3.12 |
| **API framework** | FastAPI + Uvicorn (async throughout) |
| **Agent framework** | LangGraph |
| **Vector store** | Qdrant (self-hosted) |
| **Primary DB** | PostgreSQL via asyncpg |
| **Cache** | Redis |
| **Deployment** | Docker + Kubernetes (k3s compatible) |
| **CI/CD** | GitHub Actions |
| **LLM** | OpenAI GPT-4o (default) / Mistral Large (cost tier) |
| **Embeddings** | OpenAI text-embedding-3-small / nomic-embed-text (local fallback) |
| **Target customer** | Seed to Series A startups, 3–15 engineers, cannot justify $100+/month for CodeRabbit |
| **Core differentiator** | RLHF personalisation loop — Refyn learns what *your* team cares about |
| **Business model** | Open-core: free self-hosted OSS tier + paid cloud-hosted tiers |
| **Repo visibility** | Public (open source) |

---

## 1. Problem Statement

At early-stage startups, senior engineers spend 30–90 minutes per day on pull request reviews. This is one of the highest-leverage activities in engineering — but also one of the most draining. Generic AI review tools like CodeRabbit and Qodo exist, but teams abandon them within weeks because:

1. **They are too noisy.** They comment on everything — including things the team doesn't care about. Developers start ignoring all comments, including valid ones.
2. **They don't know your codebase.** A reviewer that has never seen your auth layer, your ORM patterns, or your async conventions gives irrelevant suggestions.
3. **They don't learn.** Every PR review is stateless — the tool never improves based on whether the team accepted or rejected its suggestions.

Refyn AI solves all three. It is a codebase-aware, multi-agent reviewer that becomes more precise over time by learning from developer feedback.

---

## 2. Product Overview

### 2.1 How end users interact with Refyn AI

Refyn AI is delivered as a **GitHub App**. There is no separate UI that developers need to learn or adopt.

**Installation flow:**
```
Visit refyn.ai → Click "Install on GitHub"
→ GitHub OAuth → Select repos to grant access → Done
```

After installation, Refyn AI automatically reviews every new PR opened in the selected repos. Review comments appear inline on the PR diff — exactly like a human reviewer would comment. Developers interact with Refyn AI entirely within GitHub using native GitHub UI.

**The only active interaction required from developers:** React with 👍 or 👎 on Refyn AI's comments. This is the signal that drives the RLHF personalisation loop. No new tool to learn. No dashboard to check. Zero workflow change.

**Self-hosted tier:** Companies with compliance requirements (cannot send code to external services) clone the repo, run `docker compose up`, configure their own GitHub App credentials, and host Refyn AI on their own infrastructure. This tier is fully functional with no feature restrictions — it is the open-source offering.

### 2.2 What a review looks like

When a PR is opened, Refyn AI:
1. Retrieves relevant context from the indexed codebase (RAG)
2. Runs three specialised agents in parallel (security, performance, style)
3. Posts inline comments on the PR diff within ~45 seconds
4. Each comment shows which agent raised it and its severity level

Example comment format:
```
🔒 Security · blocking
This endpoint accepts user-supplied input directly in a raw SQL query.
Use parameterised queries or the ORM's filter() method instead.
See: /src/db/queries.py:47 for the pattern used elsewhere in this codebase.
```

The "See: [file]:[line]" reference is generated from RAG context — it points to how the team has solved similar problems before. This is the key feature that generic tools cannot replicate.

---

## 3. Business Context

### 3.1 Target customer

- Seed to Series A startups
- Engineering team size: 3–15 developers
- At least one senior engineer whose time is the bottleneck
- India-first go-to-market, then expand to SEA and global

### 3.2 Competitive landscape

| Tool | Price | Codebase-aware | Learns over time | Self-hostable |
|---|---|---|---|---|
| **Refyn AI** | Free OSS / ₹4,999/mo | ✅ | ✅ RLHF | ✅ |
| CodeRabbit | $19/user/mo | ❌ | ❌ | ❌ |
| Greptile | Custom pricing | ✅ | ❌ | ❌ |
| Qodo | $19/user/mo | ❌ | Partial | ✅ |
| SonarQube | $150+/mo | ❌ | ❌ | ✅ |

### 3.3 Pricing tiers

| Tier | Price | Limits | Notes |
|---|---|---|---|
| **Open Source** | Free | Unlimited repos, self-hosted only | Core marketing engine |
| **Starter** | ₹4,999/month | Up to 3 repos, cloud-hosted | Target: 3–5 person teams |
| **Team** | ₹12,999/month | Unlimited repos, RLHF dashboard, priority support | Target: 8–15 person teams |
| **Enterprise** | Custom | On-prem deploy, SSO, SLA, custom LLM | Target: compliance-sensitive cos |

Pricing is **per company, not per seat** — this is a deliberate product decision to remove friction for growing teams.

### 3.4 Key business metrics to track

- **Comment acceptance rate** — primary quality signal, target >60% within 4 weeks of install
- **Senior engineer time saved per day** — headline ROI metric for sales conversations
- **Week 4 retention** — whether teams are still using Refyn AI 4 weeks after install
- **Time to first accepted comment** — onboarding quality signal

---

## 4. System Architecture

```
GitHub PR Event (webhook)
        │
        ▼
┌───────────────────────┐
│   GitHub App Layer     │   FastAPI + Uvicorn
│   POST /webhook        │   Responds HTTP 200 immediately
│   Background task →   │   Actual processing is async background task
└──────────┬────────────┘
           │  PR diff + metadata
           ▼
┌───────────────────────┐
│   RAG Context Layer    │   Qdrant vector store
│   retrieve_context()   │   Indexed at install time, incremental updates on push
│                        │   tree-sitter AST chunking at function/class boundaries
└──────────┬────────────┘
           │  diff + top-12 relevant codebase chunks
           ▼
┌──────────────────────────────────────────┐
│         LangGraph Orchestrator            │
│                                          │
│   ┌──────────────┐  ┌─────────────────┐  │
│   │ Security     │  │ Performance     │  │
│   │ Agent        │  │ Agent           │  │
│   └──────────────┘  └─────────────────┘  │
│              ┌─────────────┐             │
│              │ Style Agent │             │
│              └─────────────┘             │
│         (all three run in parallel)      │
└──────────┬───────────────────────────────┘
           │  structured ReviewComment objects
           ▼
┌───────────────────────┐
│  Deduplication Layer   │   Same line + same issue = keep highest confidence
│  Confidence Filter     │   Comments below threshold suppressed (reduces noise)
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  GitHub Comment API    │   Posts inline review comments via REST API
│  post_review()         │
└──────────┬────────────┘
           │  developer reacts 👍 or 👎
           ▼
┌───────────────────────┐
│  RLHF Feedback Store   │   PostgreSQL
│  (feedback table)      │   Stores: comment_id, reaction, agent_type, repo_id, confidence
└──────────┬────────────┘
           │  daily aggregation job (APScheduler)
           ▼
┌───────────────────────┐
│  Strictness Weights    │   Redis
│  per agent per repo    │   Read on every review to adjust agent prompt strictness
└───────────────────────┘
```

---

## 5. Module Reference

### 5.1 `/app` — GitHub App integration layer

| File | Exported names | Responsibility |
|---|---|---|
| `app/main.py` | `app` (FastAPI instance) | Entrypoint, registers routers, startup/shutdown events |
| `app/webhook_handler.py` | `handle_webhook()` | Parses GitHub webhook payload, validates HMAC signature, dispatches background task |
| `app/github_client.py` | `GitHubClient` | Async GitHub REST API client — post comments, fetch file trees, fetch diff, react to comments |
| `app/auth.py` | `get_installation_token()` | GitHub App JWT auth, installation access token generation and refresh |
| `app/config.py` | `Settings` | `pydantic-settings` config class — all env vars declared here, nowhere else |
| `app/background.py` | `run_review_pipeline()` | Async background task — orchestrates RAG + agents + post comments |

**Critical behaviour:** The webhook endpoint must return HTTP 200 within 10 seconds (GitHub's timeout). All actual processing happens in `BackgroundTasks`. Never do LLM calls or DB writes in the request handler.

**Webhook events subscribed:**
- `pull_request` → `opened`, `synchronize` — triggers review pipeline
- `pull_request_review_comment` → reaction events — triggers feedback capture

**Environment variables (all declared in `app/config.py`):**
```
GITHUB_APP_ID
GITHUB_PRIVATE_KEY_PATH
GITHUB_WEBHOOK_SECRET
OPENAI_API_KEY
MISTRAL_API_KEY          # optional, for cost tier
LLM_PROVIDER             # "openai" | "mistral"
QDRANT_URL
POSTGRES_DSN
REDIS_URL
CONFIDENCE_THRESHOLD     # float, default 0.65 — comments below this are suppressed
```

---

### 5.2 `/rag` — Retrieval-Augmented Generation pipeline

| File | Exported names | Responsibility |
|---|---|---|
| `rag/indexer.py` | `index_repository()`, `update_index()` | Clones repo, chunks files, upserts to Qdrant |
| `rag/embedder.py` | `embed_chunks()`, `embed_query()` | Generates embeddings, switchable via `LLM_PROVIDER` env var |
| `rag/store.py` | `QdrantStore` | Qdrant async client wrapper — upsert, delete, search |
| `rag/retriever.py` | `retrieve_context()` | Given PR diff, returns top-k relevant chunks |
| `rag/chunker.py` | `chunk_file()` | tree-sitter AST parsing, splits files at function/class boundaries |

**Chunking strategy:**
- Parser: `tree-sitter` with language packs for Python, TypeScript, JavaScript, Go, Java, Rust
- Chunk unit: one function or class definition + its docstring
- Chunk size target: 512 tokens, overlap: 64 tokens
- Each chunk stores: `repo_id`, `file_path`, `chunk_type`, `language`, `content`, `last_modified`

**Retrieval strategy:**
- Query vector: embedding of the first 512 tokens of the unified PR diff
- Top-k: 12 chunks per review
- Recency re-ranking: chunks from files modified in last 30 days get +20% score boost

**Qdrant collection schema:**
```python
# Collection name: f"refyn_{repo_id}"  (one collection per repo)
{
    "repo_id": str,
    "file_path": str,
    "chunk_type": "function" | "class" | "module",
    "language": str,
    "content": str,
    "last_modified": str,   # ISO 8601
}
```

---

### 5.3 `/agents` — Multi-agent review engine

| File | Exported names | Responsibility |
|---|---|---|
| `agents/schemas.py` | `ReviewComment`, `ReviewState` | Shared data models — import from here, never redefine elsewhere |
| `agents/graph.py` | `build_review_graph()`, `run_review()` | LangGraph state machine — fans out to 3 agents, collects outputs |
| `agents/security_agent.py` | `SecurityAgent` | SQL injection, auth bypass, secrets in code, insecure deserialisation, OWASP Top 10 |
| `agents/performance_agent.py` | `PerformanceAgent` | N+1 queries, blocking I/O in async context, unnecessary loops, memory leaks |
| `agents/style_agent.py` | `StyleAgent` | Naming conventions, dead code, over-complexity, missing tests, unclear abstractions |
| `agents/base_agent.py` | `BaseAgent` | Abstract base — prompt construction, LLM call, JSON parse, confidence scoring |
| `agents/prompts.py` | `SECURITY_SYSTEM_PROMPT`, `PERFORMANCE_SYSTEM_PROMPT`, `STYLE_SYSTEM_PROMPT` | All prompt templates live here — never inline prompts in agent files |

**Data schemas (defined in `agents/schemas.py`, never redefined elsewhere):**

```python
from typing import TypedDict, Literal
from dataclasses import dataclass

@dataclass
class ReviewComment:
    file_path: str
    line_number: int
    body: str                          # human-readable comment, includes RAG reference if available
    severity: Literal["blocking", "suggestion", "nit"]
    agent_type: Literal["security", "performance", "style"]
    confidence: float                  # 0.0 – 1.0

class ReviewState(TypedDict):
    pr_diff: str
    context_chunks: list[str]          # retrieved from Qdrant
    repo_id: str
    pr_number: int
    strictness: dict[str, float]       # {"security": 3.2, "performance": 2.8, "style": 3.5}
    security_comments: list[ReviewComment]
    performance_comments: list[ReviewComment]
    style_comments: list[ReviewComment]
    final_comments: list[ReviewComment]
```

**Agent prompt structure:**
```
System:
You are a senior {role} reviewer for a software engineering team.
You will receive a pull request diff and relevant code chunks from the same repository.

Your task: identify {focus_area} issues ONLY. Do not comment on issues outside your domain.
Strictness level: {strictness}/5. At level 5 flag everything. At level 1 flag only critical issues.

If a context chunk shows how the team has handled a similar pattern before, reference it in your comment
using the format: "See: {file_path}:{line_number} for the pattern used elsewhere in this codebase."

Respond ONLY with a JSON array of ReviewComment objects. No prose. No markdown. Raw JSON only.

User:
PR Diff:
{diff}

Codebase context:
{context_chunks}
```

**LangGraph graph structure:**
```python
# graph.py — node names are canonical, do not rename
graph.add_node("retrieve_weights", retrieve_strictness_weights)
graph.add_node("security", run_security_agent)
graph.add_node("performance", run_performance_agent)
graph.add_node("style", run_style_agent)
graph.add_node("aggregate", aggregate_and_deduplicate)

graph.add_edge(START, "retrieve_weights")
graph.add_edge("retrieve_weights", "security")
graph.add_edge("retrieve_weights", "performance")
graph.add_edge("retrieve_weights", "style")
graph.add_edge("security", "aggregate")
graph.add_edge("performance", "aggregate")
graph.add_edge("style", "aggregate")
graph.add_edge("aggregate", END)
```

---

### 5.4 `/feedback` — RLHF personalisation loop

| File | Exported names | Responsibility |
|---|---|---|
| `feedback/listener.py` | `handle_reaction_event()` | Parses GitHub reaction webhook, identifies Refyn AI's own comments |
| `feedback/store.py` | `FeedbackStore` | asyncpg write layer — inserts feedback records |
| `feedback/aggregator.py` | `compute_strictness_weights()` | Computes per-agent per-repo acceptance rate, returns weight dict |
| `feedback/scheduler.py` | `start_scheduler()` | APScheduler job — runs aggregation daily at 02:00 UTC, writes to Redis |

**PostgreSQL schema:**
```sql
CREATE TABLE feedback (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_id      TEXT NOT NULL,
    comment_id   BIGINT NOT NULL,
    agent_type   TEXT NOT NULL,       -- 'security' | 'performance' | 'style'
    reaction     SMALLINT NOT NULL,   -- +1 (thumbs up) or -1 (thumbs down)
    confidence   FLOAT NOT NULL,      -- confidence score of the original comment
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_repo_agent ON feedback (repo_id, agent_type);
CREATE INDEX idx_feedback_created    ON feedback (created_at);

-- Tracked separately to avoid re-processing reactions
CREATE TABLE processed_reactions (
    reaction_id  BIGINT PRIMARY KEY,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Strictness weight computation logic:**
```python
def compute_strictness(repo_id: str, agent_type: str) -> float:
    """
    Returns strictness level in range [1.0, 5.0]. Default: 3.0.

    Uses rolling 30-day window of reactions.
    acceptance_rate = positive_reactions / total_reactions

    acceptance_rate >= 0.70 → strictness += 1.0  (team trusts this agent, increase volume)
    acceptance_rate <= 0.40 → strictness -= 1.0  (too noisy, reduce volume)
    0.40 < acceptance_rate < 0.70 → no change

    Clamped to [1.0, 5.0]. Written to Redis key: f"strictness:{repo_id}:{agent_type}"
    TTL: 25 hours (refreshed daily by scheduler)
    """
```

---

### 5.5 `/dashboard` — lightweight metrics UI

A simple FastAPI-served HTML dashboard for team leads. Not a complex SPA — server-rendered with Jinja2 templates and Chart.js for graphs. The dashboard is an optional add-on, not core to the review pipeline.

| Page | Route | Content |
|---|---|---|
| Overview | `/dashboard/{repo_id}` | Acceptance rate over time, comments by agent type |
| Weekly digest | `/dashboard/{repo_id}/weekly` | Pre-rendered version of the weekly email |
| Settings | `/dashboard/{repo_id}/settings` | Onboarding config, manual strictness overrides |

**Weekly digest email:** APScheduler sends every Monday 09:00 local time to the team's configured email. Content: total PRs reviewed, total comments posted, acceptance rate per agent, top issue categories. Sent via SendGrid or Resend (configurable).

---

### 5.6 `/infra` — deployment

| File | Responsibility |
|---|---|
| `Dockerfile` | Multi-stage build — builder stage installs deps, runtime stage is slim Python 3.12 |
| `docker-compose.yml` | Local dev: app + Qdrant + PostgreSQL + Redis (all services) |
| `infra/k8s/deployment.yaml` | Kubernetes Deployment — 2 replicas, rolling update strategy |
| `infra/k8s/service.yaml` | ClusterIP service |
| `infra/k8s/ingress.yaml` | Nginx ingress with TLS (cert-manager) |
| `infra/k8s/qdrant.yaml` | Qdrant StatefulSet with PVC |
| `infra/k8s/postgres.yaml` | PostgreSQL StatefulSet with PVC |
| `.github/workflows/deploy.yml` | CI/CD: lint → test → build → push GHCR → rolling deploy |

**CI/CD pipeline:**
```
[push to main]
     ├── ruff lint
     ├── mypy type check
     ├── pytest (80% coverage gate, fails build if below)
     ├── docker build --platform linux/amd64
     ├── push to ghcr.io/[org]/refyn-ai:[git-sha]
     └── kubectl set image deployment/refyn-ai app=ghcr.io/[org]/refyn-ai:[git-sha]
```

**Resource limits per pod:**
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

---

## 6. End-to-End Data Flow

```
1.  Developer opens a PR on a repo with Refyn AI installed
2.  GitHub sends POST /webhook (event: pull_request, action: opened)
3.  webhook_handler.py validates HMAC signature → returns HTTP 200 immediately
4.  run_review_pipeline() dispatched as FastAPI BackgroundTask
5.  github_client.py fetches full PR diff via GitHub REST API
6.  retriever.py embeds diff → queries Qdrant → returns top-12 context chunks
7.  Redis read: retrieve strictness weights for this repo_id (all 3 agents)
8.  build_review_graph() initialises ReviewState with diff + chunks + weights
9.  LangGraph fans out: security, performance, style agents run in parallel
10. Each agent calls LLM with specialised prompt + strictness level
11. Each agent parses JSON response → list[ReviewComment]
12. aggregate_and_deduplicate():
      - remove comments with confidence < CONFIDENCE_THRESHOLD
      - if two agents flag same file+line, keep highest confidence comment only
13. github_client.py posts surviving comments as inline PR review via GitHub REST API
14. Developer sees comments, reacts 👍 or 👎
15. GitHub sends POST /webhook (event: pull_request_review_comment, reaction created)
16. handle_reaction_event() identifies reaction on Refyn AI's own comment
17. FeedbackStore inserts record into feedback table
18. Daily scheduler (02:00 UTC): compute_strictness_weights() for all active repos
19. Updated weights written to Redis (TTL 25h)
20. Next PR review reads updated weights → agents are more or less strict accordingly
```

---

## 7. Onboarding Flow (first install experience)

When a team installs Refyn AI for the first time, the GitHub App redirect lands them on a short onboarding page at `refyn.ai/onboard`. This seeds the agent's initial configuration so week 1 is already personalised.

**Onboarding questions:**
1. Primary language(s) in this repo
2. Do you have a style guide or linter configured? (yes/no — if yes, Style Agent reduces strictness by 1)
3. What is your test coverage policy? (none / best effort / enforced %) — seeds Style Agent's test gap strictness
4. How strict should the security agent be? (low / medium / high) — direct strictness seed
5. Are there any file paths to exclude from review? (e.g. `migrations/`, `vendor/`)

These answers are stored in a `repo_config` table and used to initialise Redis weights before the first PR is reviewed.

---

## 8. Coding Conventions (mandatory for all generated code)

### Language and runtime
- Python 3.12 only. Use `match` statements where appropriate, use `tomllib` for config parsing if needed.
- All I/O-bound functions must be `async def`. No blocking calls (`requests`, `psycopg2`, `time.sleep`) anywhere in the async path.
- Use `asyncpg` directly for PostgreSQL — not SQLAlchemy (too heavy for this project).
- Use `qdrant-client` async API.
- Use `httpx.AsyncClient` for all HTTP calls including GitHub API — never `requests`.

### Configuration
- All config via `pydantic-settings` in `app/config.py`. Import `Settings` and use `settings.FIELD_NAME`.
- Never hardcode values. Never use `os.environ.get()` outside of `config.py`.
- Secrets use `pydantic.SecretStr`. Never log or return secret values.

### Error handling
- Never use bare `except:` or `except Exception: pass`.
- Webhook handlers: catch exceptions, log them with full context, always return HTTP 200 (GitHub retries on non-200).
- LLM calls: wrap in try/except, retry up to 3 times with exponential backoff on rate limit errors.
- If an agent fails entirely: log the error, skip that agent's comments, do not fail the whole review.

### Logging
- Structured JSON logging via `structlog`.
- Every log entry in the review pipeline must include: `repo_id`, `pr_number`, `agent_type` (where applicable).
- Log levels: `DEBUG` for LLM prompt/response, `INFO` for pipeline milestones, `ERROR` for exceptions.
- Never log raw diffs, code content, or API keys.

### Testing
- Unit tests: mock all external I/O (LLM calls via `respx`, GitHub API via `respx`, Qdrant via mock, Redis via `fakeredis`, Postgres via `asyncpg` test pool against a test DB).
- Integration tests: use `testcontainers` for real Qdrant and PostgreSQL instances.
- Coverage gate: 80% minimum, enforced in CI.
- Test file naming: `tests/unit/test_{module_name}.py`, `tests/integration/test_{feature}.py`.

### Code style
- `ruff` for linting and formatting (replaces black + isort + flake8).
- `mypy` in strict mode. All functions must have type annotations.
- Docstrings on all public functions — Google style.
- Maximum function length: 40 lines. If longer, split.

### Comments for AI assistants
- All prompt templates live in `agents/prompts.py`. Never inline prompt strings in agent files.
- All data schemas live in `agents/schemas.py`. Never redefine `ReviewComment` or `ReviewState`.
- All environment variables are declared in `app/config.py`. Never add new env vars without updating `config.py` and `.env.example`.

---

## 9. Project File Structure

```
refyn-ai/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, router registration
│   ├── webhook_handler.py   # GitHub webhook parsing + HMAC validation
│   ├── github_client.py     # GitHub REST API async client
│   ├── auth.py              # GitHub App JWT + installation token
│   ├── background.py        # run_review_pipeline() background task
│   └── config.py            # pydantic-settings Settings class
├── rag/
│   ├── __init__.py
│   ├── indexer.py           # repo cloning + full index
│   ├── chunker.py           # tree-sitter AST chunking
│   ├── embedder.py          # embedding generation (OpenAI / local)
│   ├── store.py             # QdrantStore async wrapper
│   └── retriever.py         # retrieve_context() — query + rerank
├── agents/
│   ├── __init__.py
│   ├── schemas.py           # ReviewComment, ReviewState — source of truth
│   ├── prompts.py           # all prompt templates
│   ├── base_agent.py        # BaseAgent abstract class
│   ├── security_agent.py    # SecurityAgent
│   ├── performance_agent.py # PerformanceAgent
│   ├── style_agent.py       # StyleAgent
│   └── graph.py             # LangGraph orchestrator
├── feedback/
│   ├── __init__.py
│   ├── listener.py          # reaction webhook handler
│   ├── store.py             # FeedbackStore (asyncpg)
│   ├── aggregator.py        # compute_strictness_weights()
│   └── scheduler.py         # APScheduler daily job
├── dashboard/
│   ├── __init__.py
│   ├── router.py            # FastAPI router for dashboard routes
│   ├── templates/           # Jinja2 HTML templates
│   └── email.py             # weekly digest email sender
├── infra/
│   ├── k8s/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   ├── qdrant.yaml
│   │   └── postgres.yaml
│   └── docker/
│       └── Dockerfile
├── tests/
│   ├── unit/
│   │   ├── test_webhook_handler.py
│   │   ├── test_retriever.py
│   │   ├── test_agents.py
│   │   ├── test_aggregator.py
│   │   └── test_github_client.py
│   └── integration/
│       ├── test_review_pipeline.py
│       └── test_feedback_loop.py
├── alembic/                 # DB migrations
│   └── versions/
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       └── pr_checks.yml
├── docker-compose.yml       # local dev: app + qdrant + postgres + redis
├── pyproject.toml           # ruff, mypy, pytest config + dependencies
├── .env.example             # all required env vars with descriptions
├── README.md                # public-facing docs (separate from this file)
└── CONTEXT_RefynAI.md       # this file
```

---

## 10. Local Development Setup

```bash
# 1. Clone repo
git clone https://github.com/[org]/refyn-ai && cd refyn-ai

# 2. Install dependencies (use uv for speed)
pip install uv
uv sync --all-extras

# 3. Copy and fill in env vars
cp .env.example .env

# 4. Start infrastructure (Qdrant + PostgreSQL + Redis)
docker compose up -d qdrant postgres redis

# 5. Run DB migrations
alembic upgrade head

# 6. Expose local server via ngrok (for GitHub webhook delivery)
ngrok http 8000
# Copy the ngrok HTTPS URL → set as webhook URL in your GitHub App settings

# 7. Start the server
uvicorn app.main:app --reload --port 8000

# 8. Install your GitHub App on a test repo and open a PR
```

---

## 11. Observability

**Prometheus metrics** exposed at `/metrics`:

| Metric | Type | Labels |
|---|---|---|
| `refyn_review_latency_seconds` | Histogram | `repo_id` |
| `refyn_comments_posted_total` | Counter | `repo_id`, `agent_type`, `severity` |
| `refyn_comment_acceptance_rate` | Gauge | `repo_id`, `agent_type` |
| `refyn_rag_latency_ms` | Histogram | `repo_id` |
| `refyn_llm_tokens_total` | Counter | `agent_type`, `provider` |
| `refyn_confidence_filter_total` | Counter | `agent_type` — how many comments suppressed |

**Target SLOs:**
- Review latency p95 < 45 seconds
- Comment acceptance rate > 60% within 4 weeks of installation
- Uptime > 99.5%

---

## 12. What Refyn AI is NOT

To prevent scope creep in code generation — Refyn AI does NOT:

- Generate code fixes or open PRs automatically (it reviews only, never writes)
- Replace human review — it is a first-pass filter that reduces senior engineer load
- Support GitLab or Bitbucket (GitHub only in v1)
- Perform full static analysis (that is SonarQube's job — Refyn AI is LLM-powered, not rule-based)
- Store raw code content anywhere except transiently in Qdrant embeddings (no plaintext code in Postgres)

---

*Document version: 2.0 — Refyn AI (renamed from ReviewSense)*
*Last updated: March 2026*
*Maintainer: [your name] — generated as placement portfolio project and early-stage product*
