"""
Enrichment Waterfall Engine — Clay-style orchestration.

Simulates a multi-source enrichment waterfall:
  Source A (Primary)  -> Source B (Fallback) -> Source C (Inferred)

Each company is enriched with:
  - Firmographic data (company size, industry, location)
  - Tech stack detection (CRM tools, sales tools)
  - Decision-maker identification (role-based targeting)
  - LinkedIn profile resolution
"""

import csv
import json
import os
import random
import sys
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent.parent / "samples"

ROLE_TARGETS = [
    "Head of Sales",
    "VP of Sales",
    "VP of Revenue",
    "CRO",
    "Director of Sales",
    "Head of Revenue Operations",
    "VP of Growth",
]

TECH_STACKS = {
    "crm": ["Salesforce", "HubSpot", "Pipedrive", "Zoho CRM", "Freshsales"],
    "enrichment": ["Clay", "ZoomInfo", "Apollo", "Lusha", "Clearbit"],
    "outbound": ["Outreach", "SalesLoft", "Smartlead", "Lemlist", "Instantly"],
    "analytics": ["Mixpanel", "Amplitude", "Heap", "PostHog", "ChartMogul"],
}


def load_companies(path=None):
    if path is None:
        path = SAMPLE_DIR / "input_companies.csv"
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def source_a_firmographics(company):
    """Primary source: Returns firmographic data with high confidence."""
    confidence = random.uniform(0.85, 0.98)
    return {
        "source": "Clearbit (simulated)",
        "confidence": round(confidence, 2),
        "employees": random.randint(50, 500),
        "location": random.choice(["San Francisco, CA", "New York, NY", "Austin, TX",
                                    "Boston, MA", "Denver, CO"]),
        "founded_year": random.randint(2016, 2022),
        "funding_stage": random.choice(["Series A", "Series B", "Series C", "Seed"]),
    }


def source_b_decision_makers(company, count=2):
    """Secondary source: Resolves decision-makers and their roles."""
    confidence = random.uniform(0.70, 0.90)
    selected = random.sample(ROLE_TARGETS, min(count, len(ROLE_TARGETS)))
    makers = []
    for i, role in enumerate(selected):
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Sam"]
        last_names = ["Chen", "Patel", "Kim", "Martinez", "Johnson", "Williams", "Davis"]
        makers.append({
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "role": role,
            "linkedin_url": f"https://linkedin.com/in/{random.choice(first_names).lower()}-{random.choice(last_names).lower()}-{random.randint(100, 999)}",
        })
    return {
        "source": "Apollo (simulated)",
        "confidence": round(confidence, 2),
        "decision_makers": makers,
    }


def source_c_tech_stack(company):
    """Tertiary source: Detects technology stack from domain."""
    confidence = random.uniform(0.60, 0.85)
    return {
        "source": "BuiltWith (simulated)",
        "confidence": round(confidence, 2),
        "tech_stack": {
            "crm": [random.choice(TECH_STACKS["crm"])],
            "enrichment": random.sample(TECH_STACKS["enrichment"], random.randint(0, 2)),
            "outbound": random.sample(TECH_STACKS["outbound"], random.randint(0, 2)),
            "analytics": random.sample(TECH_STACKS["analytics"], random.randint(0, 2)),
        },
    }


def waterfall_enrich(company):
    """
    Clay-style waterfall: try Source A, fall back to B, fall back to C.
    Each source has independent confidence.
    """
    result = {"company": company["company_name"], "domain": company["domain"]}

    result["firmographics"] = source_a_firmographics(company)
    result["decision_makers"] = source_b_decision_makers(company)
    result["tech_stack"] = source_c_tech_stack(company)

    result["waterfall_summary"] = {
        "firmographics": {"status": "found", "confidence": result["firmographics"]["confidence"]},
        "decision_makers": {"status": "found", "confidence": result["decision_makers"]["confidence"]},
        "tech_stack": {"status": "found", "confidence": result["tech_stack"]["confidence"]},
    }

    return result


def run(companies=None, demo=False):
    if companies is None:
        companies = load_companies()

    print(f"Enriching {len(companies)} companies via waterfall...")
    enriched = []
    for idx, company in enumerate(companies, 1):
        if demo:
            print(f"  [{idx}/{len(companies)}] {company['company_name']}...", end=" ")
        result = waterfall_enrich(company)
        enriched.append(result)
        if demo:
            print(f"done (confidence: {result['decision_makers']['confidence']:.0%})")

    return enriched


if __name__ == "__main__":
    run(demo=True)
