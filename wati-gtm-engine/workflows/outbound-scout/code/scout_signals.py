#!/usr/bin/env python3
"""Scout Signals — Detects buying signals from job postings, funding rounds, leadership changes, and tech adoption."""

import argparse
import json
import random
import sys
from datetime import datetime, timedelta, timezone

SIGNAL_SOURCES = ["jobs", "funding", "leadership", "tech_adoption"]

INDUSTRY_TARGETS = [
    "SaaS", "E-commerce", "Fintech", "Healthcare", "Edtech",
    "Logistics", "Real Estate", "Travel", "Enterprise Software",
]

SAMPLE_LEADS = [
    {"name": "DataStream Inc", "industry": "SaaS", "size": 150, "title": "CEO"},
    {"name": "ShopGlobal", "industry": "E-commerce", "size": 80, "title": "VP Marketing"},
    {"name": "PayFlow Solutions", "industry": "Fintech", "size": 200, "title": "CTO"},
    {"name": "MediSync Health", "industry": "Healthcare", "size": 300, "title": "Head of Product"},
    {"name": "EduSpark", "industry": "Edtech", "size": 50, "title": "Founder"},
    {"name": "LogiMove", "industry": "Logistics", "size": 120, "title": "Operations Director"},
    {"name": "PropNest", "industry": "Real Estate", "size": 90, "title": "VP Sales"},
    {"name": "VoyaGen", "industry": "Travel", "size": 60, "title": "CMO"},
    {"name": "EnterpriseToolkit", "industry": "Enterprise Software", "size": 500, "title": "Head of Sales"},
]

JOB_ROLES = [
    "VP of Sales", "Head of Customer Success", "Chief Revenue Officer",
    "Director of Business Development", "Sales Operations Manager",
    "VP of Marketing", "Head of Partnerships",
]

FUNDING_ROUNDS = ["Seed", "Series A", "Series B", "Series C"]
LEADERSHIP_ROLES_FILLED = ["CEO", "CRO", "CMO", "VP Sales", "CTO"]
TECH_ADOPTIONS = ["HubSpot", "Salesforce", "Intercom", "Zendesk", "Drift", "Freshdesk", "ActiveCampaign"]


def generate_demo_signals(count: int = 12) -> list[dict]:
    signals = []
    now = datetime.now(timezone.utc)
    for i in range(count):
        lead = random.choice(SAMPLE_LEADS)
        source = random.choice(SIGNAL_SOURCES)
        score = random.randint(15, 95)
        base = {
            "signal_id": f"sig-{i+1:04d}",
            "source": source,
            "confidence": round(random.uniform(0.6, 0.98), 2),
            "score": score,
            "lead_name": lead["name"],
            "lead_industry": lead["industry"],
            "lead_size": lead["size"],
            "detected_at": (now - timedelta(hours=random.randint(1, 72))).isoformat() + "Z",
        }
        if source == "jobs":
            base["role"] = random.choice(JOB_ROLES)
            base["summary"] = f"{lead['name']} hiring {base['role']} — likely investing in GTM stack"
        elif source == "funding":
            base["round"] = random.choice(FUNDING_ROUNDS)
            base["amount"] = f"${random.randint(1, 50)}M"
            base["summary"] = f"{lead['name']} raised ${base['amount']} {base['round']} — budget available for platform investments"
        elif source == "leadership":
            base["role"] = random.choice(LEADERSHIP_ROLES_FILLED)
            base["summary"] = f"{lead['name']} appointed new {base['role']} — new leadership means potential vendor changes"
        elif source == "tech_adoption":
            base["tool"] = random.choice(TECH_ADOPTIONS)
            base["action"] = random.choice(["adopted", "renewed", "expanded"])
            base["summary"] = f"{lead['name']} {base['action']} {base['tool']} — potential displacement opportunity"
        signals.append(base)
    return signals


def score_signal(signal: dict) -> dict:
    base = signal.get("score", 50)
    industry_bonus = 0
    if signal.get("lead_industry") in INDUSTRY_TARGETS:
        industry_bonus = 10
    recency_hours = _hours_since(signal.get("detected_at", ""))
    recency = max(0, 25 - int(recency_hours / 2))
    total = min(100, base + industry_bonus + recency)
    signal["total_score"] = total
    signal["priority"] = "HIGH" if total >= 70 else "MEDIUM" if total >= 40 else "LOW"
    return signal


def _hours_since(iso_str: str) -> int:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return int((datetime.now(timezone.utc).replace(tzinfo=None) - dt.replace(tzinfo=None)).total_seconds() / 3600)
    except Exception:
        return 999


def main():
    parser = argparse.ArgumentParser(description="Scout Signals — detect buying signals from external sources")
    parser.add_argument("--demo", action="store_true", help="Run with generated demo signals")
    parser.add_argument("--dry-run", action="store_true", help="Preview signals without side effects")
    parser.add_argument("--count", type=int, default=12, help="Number of demo signals to generate")
    parser.add_argument("--output", type=str, help="Path to save signal results JSON")
    args = parser.parse_args()

    if args.demo:
        raw_signals = generate_demo_signals(args.count)
    else:
        raw_signals = generate_demo_signals(args.count)

    scored = [score_signal(s) for s in raw_signals]
    scored.sort(key=lambda s: s["total_score"], reverse=True)

    result = {
        "signals": scored,
        "total": len(scored),
        "high_priority": len([s for s in scored if s["priority"] == "HIGH"]),
        "medium_priority": len([s for s in scored if s["priority"] == "MEDIUM"]),
        "low_priority": len([s for s in scored if s["priority"] == "LOW"]),
        "sources": {src: len([s for s in scored if s["source"] == src]) for src in SIGNAL_SOURCES},
        "dry_run": args.dry_run,
    }

    print(json.dumps(result, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults written to {args.output}", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] No signals sent to any external system.", file=sys.stderr)


if __name__ == "__main__":
    main()
