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
| 1 | Scrape signals from 4 sources: job postings, funding, leadership changes, tech stack changes | `scout_signals.py` |
| 2 | Score each detected company: signal strength × recency → priority (HIGH/MEDIUM/LOW) | `scout_signals.py` |
| 3 | Aggregate signals per lead: weight sources (funding=30, leadership=25, jobs=20, tech=15) + count bonus | `prioritize_outbound.py` |
| 4 | Generate multi-channel outreach sequences with timing, channel, and copy per signal type | `build_sequence.py` |
| 5 | Send Slack digest + email report with sequences ready for SDR review | n8n |

## Signal Sources & Scoring

| Source | What We Look For | Priority Weight | Typical Template |
|--------|-----------------|-----------------|------------------|
| Job postings | VP Sales, Head of CS, CRO hiring | 20 | "Growing team → automation helps new hires focus on revenue" |
| Funding rounds | Seed through Series C | 30 | "Congrats on raise → Wati helps post-funding scale support" |
| Leadership changes | New CRO, CMO, VP Sales | 25 | "New leaders re-evaluate tech stack in first 90 days" |
| Tech adoption | New/displaceable tools (HubSpot, SFDC, Intercom) | 15 | "Seen on {{tool}} → Wati complements it with WhatsApp" |

**Scoring formula:** `total_score = min(70, Σ signal_weights) + min(20, signal_count × 20)`  
**Thresholds:** HIGH ≥ 60 | MEDIUM ≥ 30 | LOW < 30

## Why It Works

- **Proactive, not reactive** — reach prospects while they're showing intent
- **Prioritized** — only the highest-fit accounts get human attention
- **Personalized** — signal-specific templates (funding email ≠ job posting email)
- **Human-in-the-loop** — signals flagged, sequences generated, but approval required before sending
- **No LLM dependency** — all scoring and sequences are deterministic rule-based (demo-safe)

## Tech Used

Python · n8n · Slack · Email

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
