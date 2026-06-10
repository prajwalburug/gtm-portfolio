"""
Lead Scoring Engine — Multi-factor weighted scoring with routing logic.

Scores leads 0-100 based on:
  - ICP Fit (35%): Industry match, company size, funding stage
  - Role Seniority (25%): How senior is the decision-maker role?
  - Email Quality (20%): Verification score from verifier
  - Signal Strength (20%): Tech stack overlap, recent activity signals

Routes leads to appropriate Smartlead lists based on score.
"""


ROLE_SENIORITY = {
    "CRO": 100,
    "VP of Revenue": 95,
    "VP of Sales": 90,
    "VP of Growth": 85,
    "Head of Sales": 80,
    "Head of Revenue Operations": 75,
    "Director of Sales": 70,
}

ROUTE_RULES = [
    {"min_score": 80, "list": "Active", "priority": "High", "description": "Send immediately, high daily volume"},
    {"min_score": 50, "list": "Active", "priority": "Medium", "description": "Send with moderate daily volume"},
    {"min_score": 20, "list": "Nurture", "priority": "Low", "description": "Educational sequence, weekly"},
    {"min_score": 0, "list": "Excluded", "priority": "None", "description": "Do not contact"},
]


def score_icp_fit(company):
    """Score ICP fit: industry + size + funding stage."""
    score = 70

    industry = company.get("firmographics", {}).get("firmographics", {}).get("source", "")
    if not industry:
        industry = company.get("industry", "")

    company_name = company.get("company", company.get("company_name", ""))
    domain = company.get("domain", "")

    if "tech_stack" in company:
        ts = company["tech_stack"].get("tech_stack", {})
        if ts.get("crm"):
            score += 15
        if ts.get("outbound"):
            score += 10
        if ts.get("enrichment"):
            score += 5
    else:
        score += 15

    funding = company.get("firmographics", {}).get("funding_stage", "")
    if funding in ("Series A", "Series B"):
        score += 10
    elif funding == "Series C":
        score += 5

    return min(score, 100)


def score_role_seniority(role):
    """Score based on role seniority mapping."""
    return ROLE_SENIORITY.get(role, 50)


def score_email_quality(email_info):
    """Score based on email verification result."""
    if not email_info:
        return 0
    return email_info.get("score", 0)


def score_signals(company):
    """Score based on available signals and intent data."""
    score = 50
    ts = company.get("tech_stack", {}).get("tech_stack", {})
    if ts.get("outbound"):
        score += 20
    if ts.get("crm"):
        score += 15
    if ts.get("analytics"):
        score += 15
    return min(score, 100)


def calculate_composite(icp, seniority, email_quality, signals):
    """Weighted composite score."""
    return (
        icp * 0.35 +
        seniority * 0.25 +
        email_quality * 0.20 +
        signals * 0.20
    )


def route_lead(score):
    """Route a lead to the appropriate list based on score."""
    for rule in sorted(ROUTE_RULES, key=lambda r: r["min_score"], reverse=True):
        if score >= rule["min_score"]:
            return {"list": rule["list"], "priority": rule["priority"],
                    "description": rule["description"]}
    return {"list": "Excluded", "priority": "None", "description": "Below minimum threshold"}


def run(verified_results, enriched_companies, demo=False):
    print(f"Scoring {len(verified_results)} leads...")
    scored = []

    enriched_map = {c["company"]: c for c in enriched_companies}

    for idx, lead in enumerate(verified_results, 1):
        company = enriched_map.get(lead["company"], {})

        icp = score_icp_fit(company)
        seniority = score_role_seniority(lead.get("role", ""))
        email_quality = score_email_quality(lead.get("best_email"))
        signals = score_signals(company)
        composite = calculate_composite(icp, seniority, email_quality, signals)
        route = route_lead(composite)

        entry = {
            "company": lead["company"],
            "name": lead["name"],
            "role": lead["role"],
            "email": lead["best_email"]["email"],
            "email_verdict": lead["best_email"]["verdict"],
            "scores": {
                "icp_fit": icp,
                "role_seniority": seniority,
                "email_quality": email_quality,
                "signals": signals,
                "composite": round(composite, 1),
            },
            "routing": route,
        }

        scored.append(entry)

        if demo:
            s = entry["scores"]
            r = entry["routing"]
            print(f"  [{idx}/{len(verified_results)}] {entry['name']} @ {entry['company']}")
            print(f"    ICP={s['icp_fit']} Seniority={s['role_seniority']} Email={s['email_quality']} Signals={s['signals']}")
            print(f"    Composite: {s['composite']}/100 -> {r['list']} ({r['priority']})")

    return scored


if __name__ == "__main__":
    test_vr = [{"company": "TestCorp", "name": "Alex Chen", "role": "Head of Sales",
                "best_email": {"email": "alex@test.io", "verdict": "verified", "score": 95}}]
    test_ec = [{"company": "TestCorp", "domain": "test.io",
                "firmographics": {"funding_stage": "Series A"},
                "tech_stack": {"tech_stack": {"crm": ["Salesforce"], "outbound": ["Outreach"]}}}]
    run(test_vr, test_ec, demo=True)
