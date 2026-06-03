# Wati AI-First GTM Engine

**Automated lead lifecycle · Pipeline intelligence · AI-powered outbound detection**

An end-to-end Go-To-Market automation engine for [Wati](https://wati.io), the world's leading WhatsApp-first conversational growth platform. This system turns fragmented tools, workflows, and data into a unified, intelligent revenue engine — leveraging automation and AI to enable revenue growth without headcount growth.

## Why This Exists

Wati serves 16,000+ customers across 190+ countries. As the platform scaled, the GTM team faced:

- **Manual lead triage** — every inbound lead was touched by a human before routing
- **Blind pipeline** — deals went dark until they slipped or closed
- **Reactive outbound** — no system to proactively detect buying signals
- **Fragmented tools** — data locked in silos across HubSpot, Intercom, Stripe, and spreadsheets

This system was designed to automate the operational layer so revenue teams could focus on relationships and strategy.

## What It Does

The engine is three independent but complementary workflows:

| Workflow | Trigger | Automation | Outcome |
|----------|---------|------------|---------|
| [Lead Lifecycle](./workflows/lead-lifecycle) | New contact in CRM | AI ICP scoring + enrichment + routing | HOT leads assigned in minutes |
| [Pipeline Intelligence](./workflows/pipeline-intel) | Daily cron | Risk detection + next-best-action + velocity analysis | Surface at-risk deals proactively |
| [Outbound Detection](./workflows/outbound-scout) | Every 6 hours | Signal scraper + prioritizer + sequence generator | High-fit pipeline on autopilot |

## Architecture

```
                     ┌─────────────────────────────────────────────────┐
                     │               DATA LAKE / BI                   │
                     │   (SQL pipeline velocity + conversion queries)  │
                     └──────────────────┬──────────────────────────────┘
                                        │
┌──────────────────┐    ┌───────────────┴────────────────┐    ┌───────────────────┐
│   INBOUND LEADS  │    │      PIPELINE INTELLIGENCE     │    │  OUTBOUND SIGNALS │
│  (Web, Chat, DM) │    │      ┌──────────────────┐      │    │  (Jobs, Funding,  │
│        ▼         │    │      │ Deal Risk Engine │      │    │   News, Tech)     │
│  HubSpot Forms   │    │      │ (Python + LLM)   │      │    │                   │
│  + Intercom      │    │      └──────────────────┘      │    │       ▼           │
│        ▼         │    │      ┌──────────────────┐      │    │  Python Scout     │
│  HubSpot CRM     │    │      │ Velocity Analysis│      │    │  (multi-source)   │
│  (Contact/Deal)  │    │      │ (SQL queries)    │      │    │       ▼           │
│        ▼         │    │      └──────────────────┘      │    │  Prioritizer      │
│  AI Qualifier    │    │      ┌──────────────────┐      │    │  (ICP x Signal)   │
│  (Python + LLM)  │    │      │ Next-Best-Action │      │    │       ▼           │
│        ▼         │    │      │ (rules engine)   │      │    │  n8n Sequence     │
│  Clay Enrichment │    │      └──────────────────┘      │    │  Builder          │
│        ▼         │    └───────────────┬────────────────┘    └────────┬──────────┘
│  n8n Routing     │                    │                             │
│        ▼         │                    └──────── ALL DATA ───────────┘
│  HubSpot Assign  │                             │
└──────────────────┘                    ┌────────▼────────┐
                                        │  SLACK ALERTS   │
                                        └─────────────────┘
```

## Tech Stack

| Layer | Tools |
|-------|-------|
| CRM & CX | **HubSpot** (system of record), **Intercom** |
| Automation | **n8n** (self-hosted, all workflows exportable as JSON) |
| AI/ML | **Python** (LLM scoring, risk analysis, signal processing) |
| Enrichment | **Clay** (firmographic + contact data) |
| Analytics | **SQL** (conversion rates, velocity, dashboards) |
| Notifications | **Slack** webhooks |

## Design Principles

1. **Demo-first** — every agent has a `--demo` flag that pulls sample data from the [gtm-skills.com](https://gtm-skills.com) API. Reviewers see real output without configuring API keys.
2. **Config-driven AI** — ICP criteria and LLM prompts are externalized in `shared/config/`, not hardcoded.
3. **Exportable automation** — all n8n workflows are standalone JSON files. Import into any n8n instance.
4. **Safe by default** — every agent supports `--dry-run` to print what it would do without writing to any system.
5. **Modular** — each workflow operates independently. You can deploy lead lifecycle without pipeline intel.

## Workflows

- [Lead Lifecycle](./workflows/lead-lifecycle) — AI qualification → Clay enrichment → n8n routing → Slack alert
- [Pipeline Intelligence](./workflows/pipeline-intel) — Daily risk scoring → next-best-action → velocity SQL → Slack digest
- [Outbound Detection](./workflows/outbound-scout) — Signal scraper → ICP prioritizer → LLM sequence generator

## Quick Start

```bash
# From this directory
pip install -r shared/requirements.txt

# Run any agent in demo mode
python workflows/lead-lifecycle/code/qualify_lead.py --demo
python workflows/pipeline-intel/code/analyze_pipeline.py --demo
python workflows/outbound-scout/code/scout_signals.py --demo

# Dry-run (no external writes)
python workflows/lead-lifecycle/code/qualify_lead.py --demo --dry-run
```

## Architecture Document

For a deep dive into system design, data flows, and decisions: [`docs/architecture.md`](./docs/architecture.md)

---

*Built as part of a GTM engineering portfolio. Not affiliated with Wati.*
