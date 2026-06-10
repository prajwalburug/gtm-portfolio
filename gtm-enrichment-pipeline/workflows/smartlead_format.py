"""
Smartlead Export Formatter — Converts scored leads to Smartlead-compatible CSV.

Output columns match Smartlead's import schema:
  First Name, Last Name, Email, Company Name, Position, Personalization
"""

import csv
import json


SMARTLEAD_COLUMNS = [
    "First Name",
    "Last Name",
    "Email",
    "Company Name",
    "Position",
    "List",
    "Priority",
    "Personalization",
]


def extract_first_last(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:])
    return parts[0], ""


def build_personalization(lead):
    return (
        f"Hi {lead['name'].split()[0]}, "
        f"noticed {lead['company']} is scaling. "
        f"Curious how you're handling outbound workflows?"
    )


def run(scored_leads, output_path=None, demo=False):
    if demo:
        print(f"Generating Smartlead export for {len(scored_leads)} leads...")

    rows = []
    for lead in scored_leads:
        if lead["routing"]["list"] == "Excluded":
            continue

        first, last = extract_first_last(lead["name"])
        rows.append({
            "First Name": first,
            "Last Name": last,
            "Email": lead["email"],
            "Company Name": lead["company"],
            "Position": lead["role"],
            "List": lead["routing"]["list"],
            "Priority": lead["routing"]["priority"],
            "Personalization": build_personalization(lead),
        })

    if output_path:
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=SMARTLEAD_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        if demo:
            print(f"  Wrote {len(rows)} leads to {output_path}")
    elif demo:
        print(f"\n{'─' * 60}")
        print(f"Smartlead Export Preview ({len(rows)} leads):")
        print(f"{'─' * 60}")
        print(f"{'Name':<20} {'Email':<30} {'List':<12}")
        print(f"{'─' * 20} {'─' * 30} {'─' * 12}")
        for r in rows:
            print(f"{r['First Name'] + ' ' + r['Last Name']:<20} {r['Email']:<30} {r['List']:<12}")

    return rows


if __name__ == "__main__":
    test = [
        {"name": "Alex Chen", "company": "TestCorp", "role": "Head of Sales",
         "email": "alex@test.io", "routing": {"list": "Active", "priority": "High"},
         "scores": {"composite": 85}},
    ]
    run(test, demo=True)
