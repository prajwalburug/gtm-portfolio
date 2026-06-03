# GTM Portfolio — Engineering Revenue Systems

I build go-to-market systems that turn fragmented tools, messy data, and manual workflows into automated, intelligent revenue engines. This portfolio documents those systems — end-to-end architecture, runnable code, and the thinking behind each design.

---

## Case Studies

| # | Project | Workflows | Problem | Tech | Code |
|---|---------|-----------|---------|------|------|
| 1 | **Wati AI-First GTM Engine** | Lead Lifecycle · Pipeline Intelligence · Outbound Detection | Scaling revenue without scaling headcount for a 16K+ customer WhatsApp platform | HubSpot · n8n · Python · LLM · Clay · SQL | [`wati-gtm-engine/`](./wati-gtm-engine) |

### 1. Wati AI-First GTM Engine

**The Problem:** Wati (16,000+ customers, 190+ countries) needed to scale revenue without adding headcount. Lead triage was manual, pipeline health was reactive, and outbound was spray-and-pray. Fragmented tools meant data lived in silos.

**What We Built:** A unified AI-powered GTM engine across three workflows:

| Workflow | What It Does | Why It Matters | 
|----------|-------------|----------------|
| [Lead Lifecycle](./wati-gtm-engine/workflows/lead-lifecycle) | Auto-qualifies, enriches, and routes every inbound lead by ICP fit score | Speed to lead drops from hours to minutes |
| [Pipeline Intelligence](./wati-gtm-engine/workflows/pipeline-intel) | Daily deal risk detection + next-best-action recommendations | Catch at-risk deals before they slip |
| [Outbound Detection](./wati-gtm-engine/workflows/outbound-scout) | Scans 4 signal sources, prioritizes accounts, generates personalized sequences | Proactive pipeline, not reactive |

**How It Works:**
```
Inbound Lead ──► AI Qualifier (LLM scores ICP fit) ──► Enrichment ──► Route to AE / Nurture
Open Deals   ──► Risk Engine (rules + LLM sentiment) ──► Recommendations ──► Slack Alert
Signals      ──► Scout + Prioritizer ──► Sequence Builder ──► Human Approval
```

**Why It Works:**
- Every agent runs with `--demo` mode — reviewers see real output without API keys
- All n8n workflows are exportable JSON — import into any instance
- LLM prompts are externalized in config — no hardcoded AI logic
- Modular by design — each workflow operates independently

**Tech Stack:** HubSpot · n8n · Python · OpenAI/Anthropic · Clay · SQL · Slack

<span class="tag">Lead Routing</span> <span class="tag">AI Scoring</span> <span class="tag">HubSpot</span> <span class="tag">n8n</span> <span class="tag">Pipeline Analytics</span> <span class="tag">Outbound</span>

➡️ [Full case study →](./wati-gtm-engine)

---

## About This Portfolio

Each case study follows the same structure:

> **The Problem** → **What We Built** → **How It Works** → **Why It Works** → **Tech Stack**

Every workflow has a standalone README so you can read it end-to-end without jumping between files. Code is runnable in `--demo` mode — no credentials needed.

Built by [Prajwal Burug](https://github.com/prajwalburug).
