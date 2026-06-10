# Use Case: Find Decision-Makers at Series A B2B SaaS Companies

## Context

You're a GTM Engineer at a company that sells sales intelligence tools. Your ICP is B2B SaaS companies between Series A and Series C, headquartered in the US, with 50-500 employees.

Your SDR team has identified 100 target accounts from a combination of:
- G2/Saasworthy intent signals
- Crunchbase funding alerts
- Tech stack fit (using HubSpot, Salesforce, or Outreach)

**Goal:** Find the right decision-makers at each account, verify their contact data, and load them into Smartlead for a multi-channel outbound sequence.

## The Clay Workflow (Design)

In Clay, you'd build a table like this:

| Column | Source | Logic |
|--------|--------|-------|
| Company Domain | Input | From target list |
| Company Size | Clearbit/Airscale | API enrichment |
| Tech Stack | BuiltWith | Detect CRM usage |
| Decision Maker | Apollo/LinkedIn | Head of Sales / VP Revenue / CRO |
| Email | Enrichment Waterfall | Try Apollo → Hunter → Dropcontact |
| Email Verdict | Million Verifier | Syntax → MX → SMTP check |
| Score | Formula | ICP × Seniority × Email Quality |
| Smartlead List | Route | Score > 70 → Active, else → Nurture |

## This Project's Implementation

The `enrichment_waterfall.py` engine replicates this exact logic — just without the Clay UI.

### Waterfall Strategy

```
For each company:
  1. Try Source A (Primary API)
     └── If found → use it
  2. Try Source B (Fallback API)
     └── If found → use it  
  3. Try Source C (Scraped/Inferred)
     └── Use whatever we got
```

### Scoring Formula

```
Score = (ICP Match × 0.35) + (Role Seniority × 0.25) + 
        (Email Quality × 0.20) + (Signal Strength × 0.20)
```

### Routing Logic

| Score | Action | List |
|-------|--------|------|
| 80-100 | High priority, send immediately | Active |
| 50-79 | Send with lower daily volume | Active |
| 20-49 | Nurture with educational sequence | Nurture |
| 0-19 | Skip, add to negative list | Excluded |

## Why This Matters

This is exactly how Clay workflows are designed in production. The tools change (Clay UI vs Python script) but the **thinking** — waterfall architecture, conditional routing, weighted scoring — is identical.
