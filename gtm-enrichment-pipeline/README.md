# GTM Enrichment Pipeline

A Clay-inspired enrichment waterfall engine built for a real-world use case: **Find and prioritize decision-makers at B2B SaaS companies for cold outbound campaigns.**

This project demonstrates the same design patterns and workflow logic used in Clay when building enrichment tables — waterfall enrichment, conditional routing, deduplication, scoring, and Smartlead-ready output.

## The Use Case

You have 100 target accounts from an ICP fit list. You need:

1. **Find decision-makers** — Head of Sales, VP Revenue, CRO at each account
2. **Enrich** — Get LinkedIn profiles, company info, tech stack
3. **Verify emails** — Check deliverability (Million Verifier pattern)
4. **Score** — Rank leads by ICP fit and engagement potential
5. **Export to Smartlead** — Ready for multi-channel sequencing

## Architecture

```
input.csv
  │
  ▼
┌──────────────────────┐
│  Enrichment Waterfall │  Clay-style: try source A → fallback to B → fallback to C
│  (workflows/          │
│   enrichment_waterfall│
│   .py)                │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Email Verification   │  Million Verifier pattern: syntax → MX → SMTP
│  (workflows/          │
│   email_verifier.py)  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Scoring Engine       │  Weighted: ICP match × role seniority × email quality × signal
│  (workflows/          │
│   scoring_engine.py)  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Smartlead Export     │  Formatted for Smartlead CSV import
│  (workflows/          │
│   smartlead_format.py)│
└──────┬───────────────┘
       │
       ▼
output_enriched.csv
```

## Tools This Maps To

| Real Tool | This Project's Equivalent |
|-----------|--------------------------|
| Clay | `enrichment_waterfall.py` — Orchestrated enrichment waterfall with conditional routing |
| Airscale | Company firmographic enrichment module |
| Million Verifier | `email_verifier.py` — Syntax → MX → SMTP verification pipeline |
| Smartlead | `smartlead_format.py` — Multi-channel sequence ready export |
| Apollo | LinkedIn + role resolution module |

## Quick Start

```bash
python demo/run.py
```

This runs a full end-to-end demo with sample data.

## Project Structure

```
gtm-enrichment-pipeline/
├── README.md
├── docs/
│   └── use-case.md              # Detailed use case walkthrough
├── workflows/
│   ├── enrichment_waterfall.py  # Core enrichment engine
│   ├── email_verifier.py        # Email verification (syntax → MX → SMTP)
│   ├── scoring_engine.py        # Lead scoring and routing logic
│   └── smartlead_format.py      # Smartlead-compatible output
├── samples/
│   ├── input_companies.csv      # Sample input data
│   └── output_enriched.csv      # Expected enriched output
├── n8n/
│   └── enrichment_workflow.json # Importable n8n workflow
└── demo/
    └── run.py                   # One-command demo
```
