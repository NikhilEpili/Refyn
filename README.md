# Refyn AI

**The code reviewer that learns your team.**

Refyn AI is an open-source GitHub App that reviews pull requests using a multi-agent AI pipeline — and gets better over time by learning from your team's feedback. Unlike generic AI review tools, Refyn AI indexes your entire codebase for context and adapts its strictness to what your engineers actually care about.

---

## The problem

Senior engineers at small startups spend 30–90 minutes a day on pull request reviews. Generic AI reviewers exist, but teams abandon them within weeks — they comment on everything, don't understand your codebase, and never improve. The noise erodes trust faster than the signal builds it.

Refyn AI is different. It learns.

---

## How it works

Install Refyn AI as a GitHub App. That's it. From that point on, every PR in your selected repos gets reviewed automatically — inline comments appear on the diff, just like a human reviewer.

React 👍 or 👎 on any comment. Refyn AI uses those reactions to adjust how strictly each agent reviews your code. After two weeks, it sounds like your senior engineer — not a generic bot.

```
Developer opens PR
        ↓
Refyn AI retrieves relevant context from your codebase (RAG)
        ↓
Three specialised agents review in parallel:
  🔒 Security   ⚡ Performance   ✏️ Style
        ↓
Inline comments posted on the PR diff
        ↓
Team reacts 👍 / 👎
        ↓
Refyn AI adjusts — gets smarter every week
```

---

## Features

**Codebase-aware reviews**
Refyn AI indexes your entire repository at install time. When it flags an issue, it tells you how your own codebase handles similar patterns elsewhere — not generic best practices from the internet.

**Multi-agent specialisation**
Three dedicated agents run in parallel. A security agent focused on OWASP Top 10. A performance agent that catches N+1 queries and blocking I/O. A style agent that knows your naming conventions. Each agent is narrow and precise — no single prompt trying to do everything.

**RLHF personalisation loop**
Your team's 👍/👎 reactions train the system. Acceptance rate above 70%? The agent increases volume. Below 40%? It dials back. After a few weeks, Refyn AI's comment acceptance rate climbs to match what your team actually finds useful.

**Self-hostable**
Run Refyn AI entirely on your own infrastructure. Your code never leaves your servers. One command to get started.

**Zero workflow change**
No new dashboard to learn. No new tool to open. Reviews appear where developers already work — directly on GitHub PRs.

---

## Quickstart (self-hosted)

### Prerequisites
- Docker and Docker Compose
- A GitHub account to create a GitHub App
- 2GB RAM minimum on your server

### 1. Clone the repo

```bash
git clone https://github.com/[org]/refyn-ai
cd refyn-ai
```

### 2. Create a GitHub App

1. Go to **GitHub → Settings → Developer settings → GitHub Apps → New GitHub App**
2. Set the webhook URL to `https://your-domain.com/webhook`
3. Grant permissions: Pull requests (read & write), Contents (read)
4. Subscribe to events: Pull request, Pull request review comment
5. Generate and download a private key

### 3. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:

```env
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY_PATH=/run/secrets/github_private_key
GITHUB_WEBHOOK_SECRET=your_webhook_secret
OPENAI_API_KEY=your_openai_key
LLM_PROVIDER=openai
POSTGRES_DSN=postgresql://refyn:refyn@postgres:5432/refyn
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379
CONFIDENCE_THRESHOLD=0.65
```

### 4. Start everything

```bash
docker compose up -d
```

This starts Refyn AI along with Qdrant, PostgreSQL, and Redis.

### 5. Run migrations

```bash
docker compose exec app alembic upgrade head
```

### 6. Install the GitHub App on your repos

Go to your GitHub App's page and click **Install**. Select the repos you want Refyn AI to review. Open a PR — your first review will appear within 45 seconds.

---

## Local development

```bash
# Install dependencies
pip install uv && uv sync --all-extras

# Start infrastructure only
docker compose up -d qdrant postgres redis

# Run migrations
alembic upgrade head

# Expose local server for GitHub webhooks
ngrok http 8000

# Start dev server
uvicorn app.main:app --reload --port 8000
```

Set the ngrok URL as your GitHub App's webhook URL in GitHub settings.

---

## Configuration

### Onboarding

When you first install Refyn AI, visit `https://your-domain.com/onboard` to configure your repo. You'll answer five quick questions:

- Primary languages in this repo
- Whether you have a linter or style guide configured
- Your test coverage policy
- Initial security strictness preference
- File paths to exclude from review (e.g. `migrations/`, `vendor/`)

These seed the initial agent weights so week 1 is already more useful than any generic reviewer.

### Manual strictness overrides

Go to `https://your-domain.com/dashboard/{repo_id}/settings` to manually adjust strictness for any agent at any time. Scale of 1–5 per agent.

---

## Architecture

```
refyn-ai/
├── app/          # GitHub App webhook layer (FastAPI)
├── rag/          # Codebase indexing and retrieval (Qdrant + tree-sitter)
├── agents/       # Multi-agent review engine (LangGraph)
├── feedback/     # RLHF personalisation loop (PostgreSQL + Redis)
├── dashboard/    # Metrics dashboard and weekly digest
└── infra/        # Docker, Kubernetes manifests, GitHub Actions
```

Full architecture documentation lives in [`CONTEXT_RefynAI.md`](./CONTEXT_RefynAI.md) — this is also the context file to load into AI coding assistants when contributing to this project.

---

## Tech stack

| Component | Technology |
|---|---|
| API server | FastAPI + Uvicorn |
| Agent orchestration | LangGraph |
| Vector store | Qdrant |
| Code parsing | tree-sitter |
| LLM | OpenAI GPT-4o / Mistral Large |
| Database | PostgreSQL (asyncpg) |
| Cache | Redis |
| Containers | Docker |
| Orchestration | Kubernetes (k3s compatible) |
| CI/CD | GitHub Actions |

---

## Pricing (cloud-hosted at refyn.ai)

| Tier | Price | What's included |
|---|---|---|
| **Open Source** | Free | Self-host, unlimited repos, full feature set |
| **Starter** | ₹4,999 / month | Cloud-hosted, up to 3 repos |
| **Team** | ₹12,999 / month | Unlimited repos, RLHF dashboard, priority support |
| **Enterprise** | Custom | On-prem deploy, SSO, custom LLM, SLA |

Pricing is per company, not per seat.

---

## Comparison

| | Refyn AI | CodeRabbit | Greptile | Qodo |
|---|---|---|---|---|
| Codebase-aware RAG | ✅ | ❌ | ✅ SaaS only | ❌ |
| Learns from feedback | ✅ | ❌ | ❌ | ❌ |
| Multi-agent | ✅ | ❌ | ❌ | ❌ |
| Self-hostable | ✅ | ❌ | ❌ | ✅ |
| Per-company pricing | ✅ | ❌ | ❌ | ❌ |
| Open source | ✅ | ❌ | ❌ | ✅ |

---

## Roadmap

- [x] GitHub App webhook integration
- [x] RAG pipeline with tree-sitter chunking
- [x] Multi-agent LangGraph orchestration
- [x] RLHF feedback loop
- [x] Kubernetes deployment
- [ ] VS Code extension (inline suggestions before PR)
- [ ] GitLab support
- [ ] Custom LLM support (Ollama, local models)
- [ ] Slack digest integration
- [ ] PR description auto-generation

---

## Contributing

Contributions are welcome. Before opening a PR, please:

1. Read [`CONTEXT_RefynAI.md`](./CONTEXT_RefynAI.md) — it covers all architecture decisions, coding conventions, and module boundaries
2. Run `ruff check .` and `mypy .` locally before pushing
3. Ensure test coverage stays above 80% (`pytest --cov`)
4. Open an issue first for any significant feature additions

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

---

## Contact

Built by [your name]. If you're a startup and want to try Refyn AI, reach out at [your email] or open an issue. Early adopters get free setup support and direct access to the roadmap.