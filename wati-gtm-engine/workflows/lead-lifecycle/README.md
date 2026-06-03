# Lead Lifecycle Automation

**Automatically qualify, enrich, and route every inbound lead within minutes.**

## The Problem

Inbound leads arrived in HubSpot from multiple sources (web forms, Intercom chat, inbound email). Without automation:
- Every lead required manual review before routing
- HOT leads sat untouched for hours (sometimes days)
- WARM leads were contacted too aggressively
- NURTURE leads got lost in the noise
- No consistent ICP scoring across the team

## What We Built

A three-stage pipeline that processes every inbound lead in under 60 seconds:

```
Lead enters HubSpot ──► AI Qualifier (LLM scores 1-100) ──► Clay Enrichment ──► Route + Alert
```

## How It Works

| Step | What Happens | Tool |
|------|-------------|------|
| 1 | New contact created in HubSpot → webhook fires | HubSpot |
| 2 | POST contact data to AI Qualifier | n8n |
| 3 | LLM scores lead 1-100 on ICP fit (industry, size, title, signals) | Python + LLM |
| 4 | Classifies: HOT (70+) / WARM (40-69) / NURTURE (10-39) / DISQUALIFIED | Python |
| 5 | HOT → Clay enrichment → assign to AE → Slack alert | n8n + Clay |
| 6 | WARM → tag + enroll in nurture sequence | n8n + HubSpot |
| 7 | All scores logged to HubSpot custom properties | n8n |

## Why It Works

- **Speed to lead** drops from hours to minutes for HOT leads
- **Consistent scoring** — every lead evaluated against the same ICP criteria
- **Right treatment** — each tier gets the appropriate level of attention
- **Visible reasoning** — score breakdown and LLM rationale stored in HubSpot

## Tech Used

HubSpot · n8n · Python · OpenAI/Anthropic · Clay · Slack

## How to Run

```bash
# From wati-gtm-engine/
pip install -r shared/requirements.txt

# Demo mode (simulated leads from gtm-skills.com API)
python workflows/lead-lifecycle/code/qualify_lead.py --demo

# Dry run (no API calls to external tools)
python workflows/lead-lifecycle/code/qualify_lead.py --demo --dry-run
```

## Files

| File | Purpose |
|------|---------|
| [`code/qualify_lead.py`](./code/qualify_lead.py) | AI ICP scoring + classification agent |
| [`automation/lead-lifecycle.json`](./automation/lead-lifecycle.json) | n8n workflow (importable) |
| [`sql/lead_conversion.sql`](./sql/lead_conversion.sql) | Source-to-meeting conversion analysis |
