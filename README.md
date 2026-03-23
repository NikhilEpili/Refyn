<div align="center">

```
██████╗ ███████╗███████╗██╗   ██╗███╗   ██╗
██╔══██╗██╔════╝██╔════╝╚██╗ ██╔╝████╗  ██║
██████╔╝█████╗  █████╗   ╚████╔╝ ██╔██╗ ██║
██╔══██╗██╔══╝  ██╔══╝    ╚██╔╝  ██║╚██╗██║
██║  ██║███████╗██║        ██║   ██║ ╚████║
╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝   ╚═╝  ╚═══╝
                                         AI
```

### The code reviewer that learns your team.

**Stop teaching your bot. Let it learn.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-blueviolet.svg)](https://github.com/langchain-ai/langgraph)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![Self-hostable](https://img.shields.io/badge/Self--hostable-yes-success.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#-features) • [How It Works](#-how-it-works) • [Quick Start](#-quick-start) • [Pricing](#-pricing) • [Roadmap](#%EF%B8%8F-roadmap) • [Contributing](#-contributing)

</div>

---

## The Problem with AI Code Review Today

Your senior engineer spends **45–90 minutes every day** reviewing pull requests.

You try CodeRabbit. Week one, it's exciting. By week three, your devs are dismissing every comment without reading them. Why?

> *"It flags the same things we don't care about. It doesn't know we use async everywhere. It doesn't know our naming conventions. It's just noise."*

Generic AI reviewers don't know your codebase. They don't learn. And noise is worse than silence — it trains developers to ignore the bot entirely, including the valid warnings.

**Refyn AI is different. It learns what your team cares about.**

---

## ✨ Features

### 🧠 Codebase-Aware Reviews
Refyn AI indexes your entire repository at install time. When it flags an issue, it doesn't quote Stack Overflow — it references *your own codebase*, pointing to how your team has solved the same pattern before.

```
🔒 Security · blocking

This endpoint accepts user input directly in a raw SQL string.
Use parameterised queries instead.

→ See: /src/db/queries.py:47 for the pattern used elsewhere in this codebase.
```

That last line? No other tool does that.

---

### 🤖 Three Specialised Agents, Not One Giant Prompt

| Agent | Catches |
|---|---|
| 🔒 **Security** | SQL injection, auth bypass, secrets in code, OWASP Top 10 |
| ⚡ **Performance** | N+1 queries, blocking I/O in async context, memory leaks, unnecessary loops |
| ✏️ **Style** | Naming conventions, dead code, missing tests, over-complexity |

Each agent is narrow and deep. A security agent that also reviews style is a mediocre agent at both. Refyn AI runs all three in parallel and deduplicates before posting.

---

### 📈 RLHF Personalisation Loop — The Core Differentiator

React 👍 or 👎 on any Refyn comment. That's it. Behind the scenes:

```
Week 1:  Acceptance rate ~45%  (getting to know you)
Week 2:  Acceptance rate ~58%  (learning your patterns)
Week 4:  Acceptance rate ~71%  (sounds like your senior engineer)
```

Acceptance rate above 70%? The agent increases volume — your team trusts it.
Below 40%? It dials back — too noisy, needs recalibration.

No dashboards to configure. No prompts to tweak. Just react to comments like you would with any human reviewer.

---

### 🏠 Fully Self-Hostable

Your code never leaves your servers. One `docker compose up` and you're running the full stack — app, vector store, database, cache — entirely on your own infrastructure.

This is not a lite version. Self-hosted Refyn AI has every feature the cloud version has.

---

## 🔍 How It Works

```
                    ┌─────────────────────────────┐
                    │       Developer opens PR      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Refyn AI fetches diff      │
                    │  + retrieves codebase context │   ← RAG over your entire repo
                    │    from vector store (Qdrant) │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
┌─────────▼────────┐    ┌──────────▼──────────┐  ┌─────────▼────────┐
│  🔒 Security      │    │  ⚡ Performance      │  │  ✏️  Style        │
│  Agent            │    │  Agent              │  │  Agent           │
│                   │    │                     │  │                  │
│  OWASP Top 10     │    │  N+1 queries        │  │  Conventions     │
│  Auth issues      │    │  Blocking I/O       │  │  Dead code       │
│  Secrets          │    │  Memory leaks       │  │  Test gaps       │
└─────────┬────────┘    └──────────┬──────────┘  └─────────┬────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │  deduplicate + confidence filter
                    ┌──────────────▼──────────────┐
                    │   Inline comments posted      │
                    │   on the PR diff              │   ← within 45 seconds
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Developer reacts 👍 / 👎   │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   RLHF loop updates weights   │   ← daily aggregation
                    │   Refyn gets smarter          │
                    └─────────────────────────────┘
```

---

## 🚀 Quick Start

### Option 1 — Cloud (refyn.ai)

1. Visit [refyn.ai](https://refyn.ai)
2. Click **Install on GitHub**
3. Select your repos
4. Open a PR

Your first review in under 60 seconds. No server. No config.

---

### Option 2 — Self-Hosted 🏠

#### Prerequisites
- Docker + Docker Compose
- A GitHub account to register a GitHub App
- 2 GB RAM minimum on your host

#### Step 1 — Clone

```bash
git clone https://github.com/[org]/refyn-ai
cd refyn-ai
```

#### Step 2 — Register a GitHub App

1. Go to **GitHub → Settings → Developer Settings → GitHub Apps → New GitHub App**
2. Set webhook URL: `https://your-domain.com/webhook`
3. Permissions: **Pull requests** (read & write), **Contents** (read)
4. Events: `pull_request`, `pull_request_review_comment`
5. Generate and download a private key (`.pem` file)

#### Step 3 — Configure

```bash
cp .env.example .env
```

```env
# GitHub App
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY_PATH=/run/secrets/github_private_key
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# LLM — OpenAI default, Mistral for cost-sensitive deployments
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai           # "openai" | "mistral"

# Infrastructure — defaults work with docker compose out of the box
POSTGRES_DSN=postgresql://refyn:refyn@postgres:5432/refyn
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379

# Review quality
CONFIDENCE_THRESHOLD=0.65     # comments below this score are suppressed
```

#### Step 4 — Launch

```bash
docker compose up -d
docker compose exec app alembic upgrade head
```

Install the GitHub App on your repos and open a PR. That's it.

#### Access Points

| Service | URL |
|---|---|
| 🤖 Refyn AI | Runs as a background service — no UI needed |
| 📊 Dashboard | `http://localhost:8000/dashboard/{repo_id}` |
| 📖 API Docs | `http://localhost:8000/docs` |
| 📐 Metrics | `http://localhost:8000/metrics` |

---

### Option 3 — Local Development

```bash
# Install dependencies
pip install uv && uv sync --all-extras

# Start infrastructure only
docker compose up -d qdrant postgres redis

# Run migrations
alembic upgrade head

# Expose local server to GitHub via ngrok
ngrok http 8000
# Paste the HTTPS URL into your GitHub App webhook settings

# Start dev server with hot reload
uvicorn app.main:app --reload --port 8000
```

---

## 📁 Project Structure

```
refyn-ai/
│
├── 📂 app/                      # GitHub App integration layer
│   ├── main.py                  # FastAPI entrypoint
│   ├── webhook_handler.py       # Webhook parsing + HMAC validation
│   ├── github_client.py         # GitHub REST API async client
│   ├── auth.py                  # App JWT + installation token auth
│   ├── background.py            # run_review_pipeline() background task
│   └── config.py                # All config via pydantic-settings
│
├── 📂 rag/                      # Retrieval-Augmented Generation pipeline
│   ├── indexer.py               # Repo cloning + full codebase indexing
│   ├── chunker.py               # tree-sitter AST chunking
│   ├── embedder.py              # Embedding generation (OpenAI / local)
│   ├── store.py                 # Qdrant async client wrapper
│   └── retriever.py             # retrieve_context() — query + rerank
│
├── 📂 agents/                   # Multi-agent review engine
│   ├── schemas.py               # ReviewComment, ReviewState (source of truth)
│   ├── prompts.py               # All prompt templates
│   ├── base_agent.py            # Abstract base agent
│   ├── security_agent.py        # 🔒 SecurityAgent
│   ├── performance_agent.py     # ⚡ PerformanceAgent
│   ├── style_agent.py           # ✏️  StyleAgent
│   └── graph.py                 # LangGraph orchestrator
│
├── 📂 feedback/                 # RLHF personalisation loop
│   ├── listener.py              # Reaction webhook handler
│   ├── store.py                 # PostgreSQL write layer
│   ├── aggregator.py            # Strictness weight computation
│   └── scheduler.py             # Daily APScheduler job
│
├── 📂 dashboard/                # Metrics UI + weekly digest
│   ├── router.py
│   ├── templates/
│   └── email.py
│
├── 📂 infra/
│   ├── 📂 k8s/                  # Kubernetes manifests
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   ├── qdrant.yaml
│   │   └── postgres.yaml
│   └── 📂 docker/
│       └── Dockerfile
│
├── 📂 tests/
│   ├── 📂 unit/                 # Mocked I/O, fast
│   └── 📂 integration/          # testcontainers, real infra
│
├── 📂 alembic/                  # DB migrations
├── 📂 .github/workflows/        # CI/CD pipelines
├── docker-compose.yml           # Full local stack
├── pyproject.toml               # ruff + mypy + pytest config
├── .env.example
├── CONTEXT_RefynAI.md           # LLM context doc for coding assistants
└── README.md                    # You are here
```

---

## 🛠 Tech Stack

**Core**

| Layer | Technology | Why |
|---|---|---|
| API server | FastAPI + Uvicorn | Async-native, handles webhooks without blocking |
| Agent orchestration | LangGraph | Explicit state machine, parallel node execution |
| Vector store | Qdrant | Self-hostable, fast ANN search, rich metadata filtering |
| Code parsing | tree-sitter | Language-agnostic AST chunking at function/class level |
| LLM | GPT-4o / Mistral Large | Switchable via env — cost vs quality tradeoff |
| Embeddings | text-embedding-3-small | Or `nomic-embed-text` for fully local deployment |

**Infrastructure**

| Layer | Technology |
|---|---|
| Database | PostgreSQL via asyncpg — no ORM overhead |
| Cache / weights | Redis |
| Containers | Docker multi-stage, ~180 MB runtime image |
| Orchestration | Kubernetes, k3s compatible — runs on a cheap VPS |
| CI/CD | GitHub Actions → GHCR → rolling deploy |
| Background jobs | APScheduler — no Celery overhead |

---

## 💰 Pricing

**Per company. Not per seat.** Growing your team shouldn't cost more.

| Tier | Price | Repos | Features |
|---|---|---|---|
| 🆓 **Open Source** | Free forever | Unlimited | Full feature set, self-hosted |
| 🚀 **Starter** | ₹4,999 / month | Up to 3 | Cloud-hosted, managed infra |
| 🏢 **Team** | ₹12,999 / month | Unlimited | RLHF dashboard, priority support, weekly digest |
| 🔐 **Enterprise** | Custom | Unlimited | On-prem deploy, SSO, custom LLM, SLA |

The open source tier is not a cut-down version. It is the full product. The cloud tiers pay for managed infrastructure and support — not features.

---

## 📊 Observability

Prometheus metrics at `/metrics` out of the box. Plug into Grafana with the provided dashboard config in `infra/grafana/`.

| Metric | What it tells you |
|---|---|
| `refyn_review_latency_seconds` | How fast reviews complete (target p95 < 45s) |
| `refyn_comments_posted_total` | Volume by agent and severity |
| `refyn_comment_acceptance_rate` | Quality signal — are devs acting on suggestions? |
| `refyn_confidence_filter_total` | How much noise is being suppressed before it reaches devs |
| `refyn_llm_tokens_total` | Cost tracking by agent and provider |

---

## ⚖️ Refyn AI vs The Alternatives

| | **Refyn AI** | CodeRabbit | Greptile | Qodo | SonarQube |
|---|---|---|---|---|---|
| Codebase-aware RAG | ✅ | ❌ | ✅ SaaS only | ❌ | ❌ |
| Learns from team feedback | ✅ RLHF | ❌ | ❌ | ❌ | ❌ |
| Multi-agent specialisation | ✅ 3 agents | ❌ | ❌ | ❌ | ✅ rules |
| Self-hostable | ✅ | ❌ | ❌ | ✅ | ✅ |
| Open source | ✅ | ❌ | ❌ | ✅ | ✅ community |
| Per-company pricing | ✅ | ❌ per seat | ❌ | ❌ per seat | ❌ |
| References your own code in comments | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 🗺️ Roadmap

**v1.0 — Core (in progress)**
- [x] GitHub App webhook integration
- [x] RAG pipeline with tree-sitter AST chunking
- [x] Multi-agent LangGraph orchestration (security, performance, style)
- [x] RLHF feedback loop with daily weight aggregation
- [x] Kubernetes deployment + GitHub Actions CI/CD
- [x] Prometheus metrics
- [ ] Onboarding flow (5-question repo config at install)
- [ ] Weekly digest email (Monday morning, sent to team lead)

**v1.1 — Polish**
- [ ] Dashboard UI — acceptance rate, cost, top issue categories per week
- [ ] Manual strictness overrides per agent via dashboard
- [ ] Slack notification integration
- [ ] PR description auto-generation

**v2.0 — Expand**
- [ ] VS Code extension — inline suggestions before the PR is even opened
- [ ] GitLab support
- [ ] Ollama integration — fully local LLM, zero API cost
- [ ] Custom agent builder — define your own review domain

---

## 🤝 Contributing

Contributions are welcome — especially from developers who feel the pain of noisy AI reviewers first-hand.

### Getting started

```bash
# Fork the repo, then:
git clone https://github.com/your-username/refyn-ai
cd refyn-ai
uv sync --all-extras
cp .env.example .env
docker compose up -d qdrant postgres redis
alembic upgrade head
uvicorn app.main:app --reload
```

### Before you open a PR

1. **Read [`CONTEXT_RefynAI.md`](./CONTEXT_RefynAI.md)** — all architecture decisions, module boundaries, and coding conventions. This is not optional.
2. Run the full check suite locally:

```bash
ruff check .
mypy .
pytest --cov --cov-fail-under=80
```

3. All three must pass. CI will reject PRs that don't.

### Commit style

```
Add:      new feature or capability
Fix:      bug fix
Update:   change to existing behaviour
Docs:     documentation only
Refactor: code change with no behaviour change
Test:     adding or updating tests
```

### Good first issues

New here? Look for the `good first issue` label. Some starting points:

- 🐛 Fix a reported bug
- 📝 Improve inline documentation on a complex module
- 🧪 Add test coverage to an undertested module
- 🌐 Add tree-sitter support for a new language (Go, Rust, Java)
- ⚡ Optimise the Qdrant retrieval query

### Code of conduct

Be excellent to each other. Constructive criticism of code is encouraged. Personal criticism is not.

---

## 🔧 Troubleshooting

<details>
<summary><b>Webhook isn't being received</b></summary>

1. Verify your GitHub App webhook URL is publicly accessible
2. Check `GITHUB_WEBHOOK_SECRET` matches what's set in the GitHub App settings
3. Inspect webhook delivery logs: GitHub App settings → Advanced → Recent Deliveries
4. For local dev, make sure ngrok is running and the URL hasn't expired

```bash
docker compose logs app --tail=50
```
</details>

<details>
<summary><b>Reviews are slow (longer than 45 seconds)</b></summary>

1. Check Qdrant is healthy: `curl http://localhost:6333/healthz`
2. First review on a new repo is slower — the RAG index is being built
3. Mistral is generally faster than GPT-4o for review workloads — try switching `LLM_PROVIDER=mistral`
4. Scale up Kubernetes replicas if handling many concurrent repos

```bash
kubectl logs deployment/refyn-ai --tail=100
```
</details>

<details>
<summary><b>Too many comments / feels noisy</b></summary>

1. Increase `CONFIDENCE_THRESHOLD` in `.env` (try bumping from `0.65` to `0.75`)
2. Go to Dashboard → Settings → manually lower strictness for the noisiest agent
3. Keep reacting 👎 to bad comments — the RLHF loop self-corrects within a week
4. Confirm your repo completed onboarding (the 5-question setup at install)
</details>

<details>
<summary><b>Database connection errors on startup</b></summary>

```bash
# Check postgres container status
docker compose ps postgres

# View logs
docker compose logs postgres --tail=30

# Re-run migrations
docker compose exec app alembic upgrade head
```
</details>

<details>
<summary><b>Qdrant index seems stale / missing recent code</b></summary>

Force a full re-index for a specific repo:

```bash
docker compose exec app python -c "
from rag.indexer import index_repository
import asyncio
asyncio.run(index_repository('your-org/your-repo', force=True))
"
```
</details>

---

## 📄 License

MIT — see [LICENSE](./LICENSE). Free to use, modify, and distribute.

If Refyn AI saves your team time, consider ⭐ starring the repo or sharing it with another startup drowning in PR review queues.

---

## 💬 Support & Contact

| Channel | Link |
|---|---|
| 🐛 Bug reports | [Open an issue](https://github.com/[org]/refyn-ai/issues) |
| 💡 Feature requests | [Open an issue](https://github.com/[org]/refyn-ai/issues) |
| 💬 Discussions | [GitHub Discussions](https://github.com/[org]/refyn-ai/discussions) |
| 📧 Direct | [your email] |

If you're a startup and want to try the cloud version free for 30 days, reach out directly. Early adopters get free onboarding support and direct input into the roadmap.

---

<div align="center">

**Built because senior engineers deserve better than reviewing the same mistakes twice.**

⭐ Star this repo if Refyn AI saves your team time &nbsp;•&nbsp; 🍴 Fork it if you want to make it your own

*Made with ☕ and deep frustration with noisy AI reviewers*

</div>