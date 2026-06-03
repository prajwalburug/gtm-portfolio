# GTM Portfolio — Engineering Revenue Systems

I build go-to-market systems that turn fragmented tools, messy data, and manual workflows into automated, intelligent revenue engines. This portfolio documents those systems — end-to-end architecture, runnable code, and the thinking behind each design.

---

## Case Studies

| # | Project | Workflows | Problem | Tech | Code |
|---|---------|-----------|---------|------|------|
| 1 | **Wati AI-First GTM Engine** | Lead Lifecycle · Pipeline Intelligence · Outbound Detection | Scaling revenue without scaling headcount for a 16K+ customer WhatsApp platform | HubSpot · n8n · Python · LLM · Clay · SQL | [`wati-gtm-engine/`](./wati-gtm-engine) |

### 1. Wati AI-First GTM Engine

**The Problem:** Wati (16,000+ customers, 190+ countries) needed to scale revenue without adding headcount. Lead triage was manual, pipeline health was reactive, and outbound was spray-and-pray. Fragmented tools meant data lived in silos.

**What We Built:** A unified intelligent GTM engine with 7 agents across three workflows:

| Workflow | Agents | What It Does | Why It Matters | 
|----------|--------|-------------|----------------|
| [Lead Lifecycle](./wati-gtm-engine/workflows/lead-lifecycle) | `qualify_lead.py` | Auto-qualifies inbound leads by ICP fit score using 4 weighted factors | Speed to lead drops from hours to minutes |
| [Pipeline Intelligence](./wati-gtm-engine/workflows/pipeline-intel) | `analyze_pipeline.py`, `next_best_action.py` | Daily deal risk scoring (5 factors) + rules-based action recommendations | Catch at-risk deals before they slip |
| [Outbound Detection](./wati-gtm-engine/workflows/outbound-scout) | `scout_signals.py`, `prioritize_outbound.py`, `build_sequence.py` | Scans 4 signal sources, scores accounts, generates multi-channel sequences | Proactive pipeline, not reactive |

**How It Works:**
```
Lead ──► Qualifier (ICP score: industry×size×title×signal) ──► Route to AE / Nurture
Deals ──► Risk Engine (staleness×activity×threading×amount×sentiment) ──► NBA ──► Slack
Signals ──► Scout (jobs/funding/leadership/tech) ──► Prioritizer ──► Builder ──► SDR
```

**Why It Works:**
- Every agent has `--demo` + `--dry-run` modes — reviewers see real output with zero setup
- All n8n workflows are exportable JSON — import into any instance
- Rule-based scoring (no LLM key needed) — runs fully offline
- Modular by design — each workflow operates independently

**Tech Stack:** Python 3 · n8n · SQL · HubSpot · Slack

<span class="tag">Lead Routing</span> <span class="tag">AI Scoring</span> <span class="tag">HubSpot</span> <span class="tag">n8n</span> <span class="tag">Pipeline Analytics</span> <span class="tag">Outbound</span>

➡️ [Full case study →](./wati-gtm-engine)

---

## About This Portfolio

Each case study follows the same structure:

> **The Problem** → **What We Built** → **How It Works** → **Why It Works** → **Tech Stack**

Every workflow has a standalone README so you can read it end-to-end without jumping between files. Code is runnable in `--demo` mode — no credentials needed.

Built by [Prajwal Burug](https://github.com/prajwalburug).
