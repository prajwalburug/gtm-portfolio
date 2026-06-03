# Outbound Signal Detection

**Proactively identify high-fit companies showing buying intent and generate personalized outreach — on autopilot.**

## The Problem

Outbound was reactive and manual. Reps spent hours researching accounts with no signal prioritization. By the time a prospect was contacted, a competitor had often already reached them. No consistent, repeatable way to turn market signals into pipeline.

## What We Built

A signal-based outbound engine that scrapes four types of buying signals, scores accounts by ICP fit × signal strength, and generates personalized outreach sequences.

```
Signal sources ──► Scout ──► Prioritizer ──► Sequence Builder ──► Human Review
```

## How It Works

| Step | What Happens | Tool |
|------|-------------|------|
| 1 | Scrape signals from 4 sources: job postings, funding, leadership changes, tech stack changes | Python Scout |
| 2 | Score each detected company: ICP fit (0-100) × signal strength weight | Python Prioritizer |
| 3 | Top 10 prioritized accounts → check/create in HubSpot | n8n |
| 4 | Generate personalized cold email + channel mix recommendations via LLM | Python Builder |
| 5 | Send Slack digest with company, signal, score, and email draft for human approval | n8n |

## Signal Sources

| Source | What We Look For | Weight |
|--------|-----------------|--------|
| Job postings | Companies hiring for Sales Ops, RevOps, Customer Experience roles | 1.2x |
| Funding announcements | Series A+ funding rounds (recent 30 days) | 1.5x |
| Leadership changes | New VP Sales, CRO, Head of Growth hires | 1.3x |
| Tech stack changes | Added/removed messaging or CRM tools | 1.0x |

## Why It Works

- **Proactive, not reactive** — reach prospects while they're showing intent
- **Prioritized** — only the highest-fit accounts get human attention
- **Personalized** — LLM generates outreach specific to the signal type (funding email ≠ job posting email)
- **Human-in-the-loop** — signals flagged, sequences generated, but approval required before sending

## Tech Used

Python · OpenAI/Anthropic · n8n · HubSpot · Slack

## How to Run

```bash
# From wati-gtm-engine/
pip install -r shared/requirements.txt

# Demo mode (simulated signals from gtm-skills.com API)
python workflows/outbound-scout/code/scout_signals.py --demo
python workflows/outbound-scout/code/prioritize_outbound.py --demo
python workflows/outbound-scout/code/build_sequence.py --demo

# Dry run
python workflows/outbound-scout/code/scout_signals.py --demo --dry-run
```

## Files

| File | Purpose |
|------|---------|
| [`code/scout_signals.py`](./code/scout_signals.py) | Multi-source signal scraper |
| [`code/prioritize_outbound.py`](./code/prioritize_outbound.py) | ICP × signal weighted scoring |
| [`code/build_sequence.py`](./code/build_sequence.py) | LLM-powered sequence generation |
| [`automation/outbound-scout.json`](./automation/outbound-scout.json) | n8n scheduled workflow |
