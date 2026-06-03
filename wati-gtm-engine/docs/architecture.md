# Wati AI-First GTM Engine — Architecture

## Overview

This document describes the architecture for Wati's AI-first Go-To-Market engine. The system integrates HubSpot, n8n, Python AI agents, Clay enrichment, and SQL analytics into three automated workflows that collectively power lead lifecycle management, pipeline intelligence, and outbound signal detection.

**Company Context:** Wati is a WhatsApp-first conversational growth platform serving 16,000+ customers across 190+ countries. The GTM engine is designed to scale revenue without scaling headcount by replacing manual processes with AI-driven automation.

---

## 1. System Architecture

### System of Record

**HubSpot CRM** serves as the single source of truth for all contacts, companies, deals, and pipeline data. All automations read from and write back to HubSpot via its REST API.

### Automation Layer

**n8n** (self-hosted) orchestrates all multi-step workflows. Each workflow is exportable as a single JSON file that can be imported into any n8n instance. n8n handles:
- Webhook reception from HubSpot and other sources
- HTTP calls to Python agents (triggered as scripts)
- API calls to Clay, Slack, and HubSpot
- Conditional routing and error handling

### AI Layer

**Python** scripts handle all logic that requires LLM inference or complex business rules:
- ICP scoring (LLM evaluates against configurable criteria)
- Deal risk analysis (rules + LLM sentiment on notes)
- Next-best-action recommendations (rules engine)
- Signal detection and prioritization (multi-source scraping + scoring)
- Sequence generation (LLM generates personalized outreach)

### Data Flow Model

```ascii
┌──────────────────────────────────────────────────────────────────────────────┐
│                              TRIGGER SOURCES                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────────────┐     │
│  │ Web Form │  │ Intercom │  │ Inbound  │  │ External Signals        │     │
│  │          │  │  Chat    │  │  Email   │  │ (Jobs, Funding, News)   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────────┬─────────────┘     │
│       │             │             │                    │                    │
│       └─────────────┴─────────────┴────────────────────┘                    │
│                                    ▼                                        │
│                          ┌─────────────────────┐                           │
│                          │     HUBSPOT CRM     │                           │
│                          │  (Contacts, Deals,  │                           │
│                          │   Companies, Notes) │                           │
│                          └──────────┬──────────┘                           │
│                                     │                                      │
│                          ┌──────────▼──────────┐                           │
│                          │   n8n Orchestrator  │                           │
│                          │  (workflow routing, │                           │
│                          │   webhooks, API)    │                           │
│                          └──────────┬──────────┘                           │
│                                     │                                      │
│                    ┌────────────────┼────────────────┐                     │
│                    ▼                ▼                ▼                     │
│           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │
│           │  Python AI   │ │ Clay        │ │ Slack       │              │
│           │  Agents      │ │ Enrichment  │ │ Alerts      │              │
│           │  (LLM+Rules) │ │ (API)       │ │ (Webhooks)  │              │
│           └──────────────┘ └──────────────┘ └──────────────┘              │
│                                     │                                      │
│                                     ▼                                      │
│                          ┌─────────────────────┐                           │
│                          │   SQL Analytics     │                           │
│                          │ (Velocity, Conv.   │                           │
│                          │  Rates, Dashboards) │                           │
│                          └─────────────────────┘                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Workflow A: Lead Lifecycle Automation

### Purpose
Automatically qualify, enrich, and route every inbound lead within minutes of entry — no manual triage.

### Trigger
New contact created in HubSpot (from web form submission, Intercom chat, inbound email parsing)

### Step-by-Step

```
1. HubSpot: Contact created → webhook fires to n8n
2. n8n: POST contact data to qualify_lead.py (HTTP endpoint or subprocess)
3. Python: LLM scores contact 1-100 against ICP criteria
   - Industry fit (30%)
   - Company size (25%)
   - Job title relevance (25%)
   - Signal strength (20%)
4. Python: Returns classification + score + reasoning
5. n8n: Route based on classification:
   ┌────────────────────────────────────────────────────────────────┐
   │ HOT (score ≥ 70):                                             │
   │   → Call Clay enrichment API (phone, LinkedIn, company data)   │
   │   → Update HubSpot with enrichment fields                      │
   │   → Assign to appropriate AE (round-robin or territory)        │
   │   → Send Slack alert with prospect summary card                │
   ├────────────────────────────────────────────────────────────────┤
   │ WARM (score 40-69):                                            │
   │   → Tag as "WARM" in HubSpot                                   │
   │   → Enroll in 5-touch nurture sequence                         │
   │   → No assignment yet                                          │
   ├────────────────────────────────────────────────────────────────┤
   │ NURTURE (score 10-39):                                         │
   │   → Tag as "NURTURE"                                           │
   │   → Enroll in monthly newsletter drip                          │
   ├────────────────────────────────────────────────────────────────┤
   │ DISQUALIFIED (score < 10):                                     │
   │   → Tag with disqualification reason                           │
   │   → No further action                                          │
   └────────────────────────────────────────────────────────────────┘
6. HubSpot: Log score, classification, enrichment data to custom properties
7. Slack: Alert sent (HOT only) with: name, company, score, enrichment summary
```

### Key Components

| Component | File | Responsibility |
|-----------|------|----------------|
| AI Qualifier | `python/agents/qualify_lead.py` | ICP scoring + classification |
| n8n Workflow | `automations/n8n/lead-lifecycle.json` | Orchestration + routing |
| SQL Analysis | `sql/lead_conversion.sql` | Source-to-meeting conversion tracking |

---

## 3. Workflow B: Pipeline Intelligence

### Purpose
Proactively identify at-risk deals, surface recommendations, and track pipeline health — before it's too late.

### Schedule
Daily at 7:00 AM (cron trigger → n8n)

### Step-by-Step

```
1. n8n: Fetch all open deals from HubSpot API (properties: stage, amount, 
   close_date, created_at, last_activity_date, notes, associated contacts)
2. n8n: POST deal batch to analyze_pipeline.py
3. Python: Per-deal risk assessment:
   ┌────────────────────────────────────────────────────────────────┐
   │ Risk Factor                  │ Weight │ Threshold              │
   ├────────────────────────────────────────────────────────────────┤
   │ Stage staleness              │ 30%    │ >30 days in same stage │
   │ Last activity                │ 25%    │ >7 days since activity │
   │ Stakeholder count            │ 20%    │ <2 engaged contacts    │
   │ Stage-to-amount fit          │ 15%    │ Amount vs typical at   │
   │                              │        │ this stage outlier     │
   │ LLM note sentiment           │ 10%    │ Negative/stalled       │
   └────────────────────────────────────────────────────────────────┘
4. Python: For high-risk deals → call next_best_action.py
   - Rules engine matches risk pattern to recommended action:
     - STALE → "Schedule executive check-in"
     - RISK → "Send case study [X] to address [concern]"
     - LOW VELOCITY → "Propose shorter evaluation pilot"
5. SQL: Run velocity analysis (query against exported HubSpot data)
   - Stage-by-stage conversion rates (90-day window)
   - Average days per stage
   - Historical comparison
6. n8n: Update HubSpot deal with risk_score + recommended_action + 
   last_analyzed_at
7. n8n: Send Slack digest with:
   - Top 5 at-risk deals summary
   - Overall pipeline health score
   - Velocity trends this week vs last
```

### Key Components

| Component | File | Responsibility |
|-----------|------|----------------|
| Risk Engine | `python/agents/analyze_pipeline.py` | Deal risk scoring + LLM sentiment |
| Recommender | `python/agents/next_best_action.py` | Rules-based action recommendation |
| n8n Workflow | `automations/n8n/pipeline-intel.json` | Daily cron orchestration |
| SQL Queries | `sql/pipeline_velocity.sql` | Conversion rates + stage velocity |

---

## 4. Workflow D: Outbound Signal Detection

### Purpose
Proactively identify high-fit companies showing buying intent, and generate personalized outreach — before competitors reach them.

### Schedule
Every 6 hours (cron trigger → n8n)

### Step-by-Step

```
1. Python scout_signals.py: Scrape signals from configured sources:
   ┌────────────────────────────────────────────────────────────────┐
   │ Signal Source           │ Example                             │
   ├────────────────────────────────────────────────────────────────┤
   │ Job postings            │ Companies hiring for Sales Ops,     │
   │                         │ RevOps, or Customer Experience roles│
   │ Funding announcements   │ Series A+ rounds (Crunchbase RSS)   │
   │ Leadership changes      │ New VP Sales / CRO hires            │
   │ Tech stack changes      │ Added/removed WhatsApp or           │
   │                         │ messaging platform tools            │
   └────────────────────────────────────────────────────────────────┘
2. Python prioritize_outbound.py: Score each detected company:
   Score = ICP_fit_score × signal_strength_weight
   - ICP fit: industry, size, tech stack match (0-100)
   - Signal weight: funding=1.5, job_posting=1.2, leadership=1.3, 
     tech_change=1.0
3. Python: Return prioritized list sorted descending
4. n8n: For top 10 prioritized accounts:
   - Check if company already exists in HubSpot
   - If not → create company + contact record (if contact data available)
   - If exists → update with new signal info
5. Python build_sequence.py: For each top account:
   - LLM generates personalized cold email based on signal type
   - Suggests channel mix: Email (Day 1), LinkedIn (Day 3), Phone (Day 7)
   - Generates 3 subject line variants
6. n8n: Send Slack digest to SDR team for human review
   - Includes: company, signal type, priority score, generated email draft
   - SDR: One-click approval triggers sequence enrollment
```

### Signal Configuration

Each signal source is configured in `config/signals_config.json` with:
- Source URL or RSS feed
- Search keywords
- Rate limit settings
- Minimum score threshold

This makes the system adaptable to different industries or ICPs without code changes.

### Key Components

| Component | File | Responsibility |
|-----------|------|----------------|
| Signal Scout | `python/agents/scout_signals.py` | Multi-source signal scraping |
| Prioritizer | `python/agents/prioritize_outbound.py` | ICP x Signal scoring |
| Sequence Builder | `python/agents/build_sequence.py` | LLM-powered outreach generation |
| n8n Workflow | `automations/n8n/outbound-scout.json` | Scheduled orchestration |

---

## 5. Demo Mode

Every Python agent supports a `--demo` flag that pulls realistic sample data from the [gtm-skills.com](https://gtm-skills.com) API (anonymized company/industry profiles and sales prompts). This allows portfolio reviewers to see real output without configuring API keys.

```bash
python agents/qualify_lead.py --demo
# Output: scored leads with ICP reasoning, printed to stdout

python agents/analyze_pipeline.py --demo
# Output: deal risk scores with recommendations

python agents/scout_signals.py --demo
# Output: detected signals with priority scores
```

Every agent also supports `--dry-run` to print what it would do without writing to any external system.

---

## 6. Tech Stack Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python | AI/ML ecosystem, LLM libraries, portable, portfolio-standard |
| Orchestration | n8n | Self-hosted, free, exportable JSON workflows, 250+ integrations |
| CRM | HubSpot | REST API, webhooks, custom properties, free tier available |
| Enrichment | Clay | Best-in-class data, API-first, no-code mergeable |
| AI | LLM API | Flexible, minimal infra, best for text-based scoring |
| Data format | SQL queries | Standard for analytics, run against any DB |

---

## 7. Error Handling

| Scenario | Behavior |
|----------|----------|
| HubSpot API down | n8n retries 3x (exponential backoff), Slack alert on failure |
| LLM API timeout | Fallback to rule-based scoring (no AI), flag for review |
| Enrichment partial data | Proceed with available data, log missing fields |
| Signal source unreachable | Skip that source, log error, continue with others |
| Webhook payload invalid | Reject + log payload for debugging |
