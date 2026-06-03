#!/usr/bin/env python3
"""Build Sequence — Generates multi-channel outreach sequences from prioritized leads."""

import argparse
import json
import sys
from datetime import datetime, timedelta

SEQUENCE_TEMPLATES = {
    "funding": {
        "steps": [
            {
                "day": 1,
                "channel": "LinkedIn",
                "subject": "Congrats on the funding — here's how Wati helps post-Series companies scale support",
                "body": "Hey {{name}}, congrats on the {{amount}} raise! At Wati, we help funded companies like yours handle 10x message volume without scaling headcount. Worth 15 min?",
                "goal": "Warm intro leveraging the funding event",
            },
            {
                "day": 3,
                "channel": "email",
                "subject": "How {{company}} can convert 2x more from WhatsApp in 30 days",
                "body": "Quick follow-up — companies that add WhatsApp to their GTM stack see 2x conversion rates. Here's a 30-day playbook. <link>",
                "goal": "Educate on WhatsApp business value",
            },
            {
                "day": 7,
                "channel": "phone",
                "body": "Short call to discuss how Wati integrates with {{tech_stack}} to automate customer acquisition at scale.",
                "goal": "Book a discovery call",
            },
        ]
    },
    "leadership": {
        "steps": [
            {
                "day": 1,
                "channel": "email",
                "subject": "Welcome {{name}} — rethinking {{company}}'s customer engagement strategy?",
                "body": "Welcome to {{company}}! New GTM leaders often re-evaluate the tech stack in the first 90 days. Wati's WhatsApp platform helps modernize customer engagement. Would you be open to a brief conversation?",
                "goal": "New-leadership angle — they're evaluating changes",
            },
            {
                "day": 4,
                "channel": "LinkedIn",
                "subject": "What top CROs are doing differently with WhatsApp",
                "body": "Hey {{name}}, our customers see 40% higher engagement when they add WhatsApp to their sales motion. Would you like to see how?",
                "goal": "Social proof + relevance",
            },
            {
                "day": 10,
                "channel": "email",
                "body": "Case studies of GTM teams that transformed their pipeline with WhatsApp automation. <link>",
                "goal": "Provide social proof",
            },
        ]
    },
    "jobs": {
        "steps": [
            {
                "day": 1,
                "channel": "email",
                "subject": "Saw you're hiring a {{role}} — Wati can help them ramp faster",
                "body": "Hi {{name}}, noticed {{company}} is growing the team! When you add headcount, automating the inbound channel with Wati means new hires focus on revenue, not routing. Want to see how?",
                "goal": "Connect hiring signal to efficiency value prop",
            },
            {
                "day": 5,
                "channel": "LinkedIn",
                "body": "Quick thought — most {{industry}} companies that hire {{role}} also invest in automation. Here's why. <link>",
                "goal": "Thought leadership engagement",
            },
        ]
    },
    "tech_adoption": {
        "steps": [
            {
                "day": 1,
                "channel": "email",
                "subject": "See you're on {{tool}} — here's how Wati complements it with WhatsApp",
                "body": "Hi {{name}}, noticed {{company}} uses {{tool}}. Wati integrates seamlessly with {{tool}} to add WhatsApp as a high-conversion channel. Happy to share how.",
                "goal": "Displacement or integration angle",
            },
            {
                "day": 3,
                "channel": "LinkedIn",
                "body": "{{tool}} + WhatsApp = unstoppable GTM. Here's the playbook. <link>",
                "goal": "Short-form engagement",
            },
        ]
    },
}


def build_sequence(lead_signals: list, lead_name: str) -> dict:
    sources = [s.get("source", "") for s in lead_signals]
    merged_steps = {}
    step_counter = 0

    for src in sorted(set(sources)):
        tmpl = SEQUENCE_TEMPLATES.get(src)
        if not tmpl:
            continue
        for step in tmpl["steps"]:
            step_counter += 1
            day = step["day"]
            while day in merged_steps:
                day += 1
            merged_steps[day] = {
                "step": step_counter,
                "day": day,
                "channel": step.get("channel", "email"),
                "trigger_source": src,
                "subject": step.get("subject", ""),
                "body": step.get("body", ""),
                "goal": step.get("goal", ""),
            }

    ordered = [merged_steps[d] for d in sorted(merged_steps.keys())]
    return {
        "lead_name": lead_name,
        "total_steps": len(ordered),
        "execution_window_days": ordered[-1]["day"] if ordered else 0,
        "steps": ordered,
    }


def main():
    parser = argparse.ArgumentParser(description="Build outreach sequences from prioritized leads")
    parser.add_argument("--demo", action="store_true", help="Run with built-in sample data")
    parser.add_argument("--dry-run", action="store_true", help="Preview sequences without side effects")
    parser.add_argument("--input", type=str, help="JSON file with prioritize_outbound.py output")
    parser.add_argument("--signals", type=str, help="JSON file with raw signals (for sequence personalization)")
    parser.add_argument("--output", type=str, help="Path to save sequence results JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
        leads = data.get("results", [])
        signals_raw = data.get("signals", [])
    elif args.demo:
        signals_raw = [
            {"lead_name": "DataStream Inc", "source": "funding", "amount": "$15M", "name": "CEO"},
            {"lead_name": "DataStream Inc", "source": "jobs", "role": "VP of Sales"},
            {"lead_name": "ShopGlobal", "source": "leadership", "name": "CMO", "role": "CMO"},
            {"lead_name": "ShopGlobal", "source": "tech_adoption", "tool": "HubSpot"},
            {"lead_name": "MediSync Health", "source": "tech_adoption", "tool": "Salesforce"},
        ]
        leads = [
            {"lead_name": "DataStream Inc", "priority": "HIGH", "total_score": 80},
            {"lead_name": "ShopGlobal", "priority": "HIGH", "total_score": 65},
            {"lead_name": "MediSync Health", "priority": "MEDIUM", "total_score": 40},
        ]
    else:
        signals_raw = []
        leads = []

    if args.signals:
        with open(args.signals) as f:
            sig_data = json.load(f)
        signals_raw = sig_data if isinstance(sig_data, list) else sig_data.get("signals", [])

    sequences = []
    for lead in leads:
        name = lead.get("lead_name", "")
        lead_signals = [s for s in signals_raw if s.get("lead_name") == name]
        seq = build_sequence(lead_signals, name)
        seq["lead_priority"] = lead.get("priority", "unknown")
        seq["lead_score"] = lead.get("total_score", 0)
        sequences.append(seq)

    sequences.sort(key=lambda s: s.get("lead_score", 0), reverse=True)

    output = {
        "sequences": sequences,
        "total_leads": len(sequences),
        "total_steps": sum(s["total_steps"] for s in sequences),
        "dry_run": args.dry_run,
    }

    print(json.dumps(output, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults written to {args.output}", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] No sequences enqueued in any outreach system.", file=sys.stderr)


if __name__ == "__main__":
    main()
