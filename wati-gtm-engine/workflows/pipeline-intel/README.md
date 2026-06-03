# Pipeline Intelligence

**Proactively detect at-risk deals and surface actionable recommendations — daily.**

## The Problem

Pipeline reviews were reactive and infrequent. Deals went dark for weeks before anyone noticed. Reps couldn't see aggregate risk patterns, and managers relied on gut feel rather than data for pipeline health.

## What We Built

A daily pipeline analysis engine that scores every open deal for risk, generates next-best-action recommendations, and tracks velocity trends over time.

```
Daily cron ──► Fetch open deals ──► Risk scoring + LLM sentiment ──► Recommendations ──► Slack digest
```

## How It Works

| Step | What Happens | Tool |
|------|-------------|------|
| 1 | Daily cron triggers pipeline analysis | n8n |
| 2 | Fetch all open deals from HubSpot API | n8n |
| 3 | Per-deal risk scoring: stage staleness, activity gap, stakeholder count, amount fit, LLM note sentiment | Python |
| 4 | High-risk deals → next-best-action recommendation (rules engine) | Python |
| 5 | Run velocity SQL queries (conversion rates, avg days per stage) | SQL |
| 6 | Update HubSpot with risk score + recommendation | n8n |
| 7 | Send Slack digest: top 5 at-risk deals + pipeline health score | n8n |

## Risk Scoring Model

| Factor | Weight | Threshold |
|--------|--------|-----------|
| Stage staleness | 30% | >30 days in same stage |
| Last activity | 25% | >7 days since activity |
| Stakeholder count | 20% | <2 engaged contacts |
| Stage-to-amount fit | 15% | Amount outlier for stage |
| LLM note sentiment | 10% | Negative/stalled language |

## Why It Works

- **Catches slippage early** — deals flagged before they go cold
- **Actionable, not just data** — every risk comes with a recommended action
- **Trend-aware** — velocity analysis shows whether pipeline health is improving or declining
- **No manual effort** — runs daily without anyone touching it

## Tech Used

HubSpot · n8n · Python · OpenAI/Anthropic · SQL · Slack

## How to Run

```bash
# From wati-gtm-engine/
pip install -r shared/requirements.txt

# Demo mode (simulated deals from gtm-skills.com API)
python workflows/pipeline-intel/code/analyze_pipeline.py --demo
python workflows/pipeline-intel/code/next_best_action.py --demo

# Dry run
python workflows/pipeline-intel/code/analyze_pipeline.py --demo --dry-run
```

## Files

| File | Purpose |
|------|---------|
| [`code/analyze_pipeline.py`](./code/analyze_pipeline.py) | Deal risk scoring + LLM sentiment analysis |
| [`code/next_best_action.py`](./code/next_best_action.py) | Rules-based recommendation engine |
| [`automation/pipeline-intel.json`](./automation/pipeline-intel.json) | n8n daily cron workflow |
| [`sql/pipeline_velocity.sql`](./sql/pipeline_velocity.sql) | Stage conversion + velocity queries |
