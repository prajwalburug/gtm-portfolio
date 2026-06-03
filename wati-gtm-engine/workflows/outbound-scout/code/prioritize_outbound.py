#!/usr/bin/env python3
"""Prioritize Outbound — Scores leads by signal strength + ICP fit for outreach priority."""

import argparse
import json
import sys

SIGNAL_PRIORITY_WEIGHTS = {
    "funding": 30,
    "leadership": 25,
    "jobs": 20,
    "tech_adoption": 15,
}

SIGNAL_COUNT_WEIGHT = 20


def score_lead_for_outbound(lead: dict, signals: list[dict]) -> dict:
    relevant = [s for s in signals if s.get("lead_name") == lead.get("name")]
    if not relevant:
        return {
            "lead_name": lead.get("name", "Unknown"),
            "lead_industry": lead.get("industry", ""),
            "lead_size": lead.get("size", 0),
            "total_score": 0,
            "signal_count": 0,
            "signal_score": 0,
            "priority": "LOW",
        }

    signal_score = sum(SIGNAL_PRIORITY_WEIGHTS.get(s.get("source", ""), 0) for s in relevant)
    signal_score = min(70, signal_score)
    count_score = min(20, len(relevant) * SIGNAL_COUNT_WEIGHT)
    total = signal_score + count_score

    return {
        "lead_name": lead.get("name", "Unknown"),
        "lead_industry": lead.get("industry", ""),
        "lead_size": lead.get("size", 0),
        "total_score": total,
        "signal_count": len(relevant),
        "signal_sources": list(set(s.get("source", "") for s in relevant)),
        "signal_score_component": signal_score,
        "count_score_component": count_score,
        "priority": "HIGH" if total >= 60 else "MEDIUM" if total >= 30 else "LOW",
    }


def main():
    parser = argparse.ArgumentParser(description="Prioritize outbound leads by signal strength")
    parser.add_argument("--demo", action="store_true", help="Run with built-in sample data")
    parser.add_argument("--dry-run", action="store_true", help="Preview without side effects")
    parser.add_argument("--signals", type=str, help="JSON file with scout_signals.py output")
    parser.add_argument("--output", type=str, help="Path to save priority results JSON")
    args = parser.parse_args()

    if args.signals:
        with open(args.signals) as f:
            signals_data = json.load(f)
        signals = signals_data if isinstance(signals_data, list) else signals_data.get("signals", [])
        unique_names = {s.get("lead_name") for s in signals if s.get("lead_name")}
        leads = []
        for n in sorted(unique_names):
            signal_samples = [s for s in signals if s.get("lead_name") == n]
            industry = signal_samples[0].get("lead_industry", "") if signal_samples else ""
            size = signal_samples[0].get("lead_size", 0) if signal_samples else 0
            leads.append({"name": n, "industry": industry, "size": size})
    elif args.demo:
        signals = [
            {"lead_name": "DataStream Inc", "source": "funding"},
            {"lead_name": "DataStream Inc", "source": "jobs"},
            {"lead_name": "ShopGlobal", "source": "leadership"},
            {"lead_name": "ShopGlobal", "source": "tech_adoption"},
            {"lead_name": "ShopGlobal", "source": "jobs"},
            {"lead_name": "PayFlow Solutions", "source": "funding"},
            {"lead_name": "MediSync Health", "source": "tech_adoption"},
        ]
        leads = [
            {"name": "DataStream Inc", "industry": "SaaS", "size": 150},
            {"name": "ShopGlobal", "industry": "E-commerce", "size": 80},
            {"name": "PayFlow Solutions", "industry": "Fintech", "size": 200},
            {"name": "MediSync Health", "industry": "Healthcare", "size": 300},
            {"name": "EduSpark", "industry": "Edtech", "size": 50},
        ]
    else:
        signals = []
        leads = []

    scored = [score_lead_for_outbound(l, signals) for l in leads]
    scored.sort(key=lambda x: x["total_score"], reverse=True)

    result = {
        "results": scored,
        "total": len(scored),
        "high_priority": len([s for s in scored if s["priority"] == "HIGH"]),
        "medium_priority": len([s for s in scored if s["priority"] == "MEDIUM"]),
        "low_priority": len([s for s in scored if s["priority"] == "LOW"]),
        "dry_run": args.dry_run,
    }

    print(json.dumps(result, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults written to {args.output}", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] No outbound actions initiated.", file=sys.stderr)


if __name__ == "__main__":
    main()
