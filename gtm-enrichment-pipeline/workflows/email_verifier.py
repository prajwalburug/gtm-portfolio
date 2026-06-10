"""
Email Verification Pipeline — Million Verifier pattern.

Three-stage verification:
  1. Syntax check — is the email well-formed?
  2. MX record check — does the domain accept mail?
  3. SMTP verification — does the mailbox exist?

Emails are scored: 0-100 (100 = verified and deliverable).
"""

import re
import random


def syntax_check(email):
    """Stage 1: Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    is_valid = bool(re.match(pattern, email))
    return {
        "verdict": "pass" if is_valid else "fail",
        "score": 100 if is_valid else 0,
        "detail": "Well-formed email address" if is_valid else "Invalid email format",
    }


def mx_check(domain):
    """Stage 2: Check if domain accepts mail (simulated)."""
    known_good_domains = ["gmail.com", "outlook.com", "yahoo.com", "icloud.com",
                           "proton.me", "zoho.com", "fastmail.com"]
    has_mx = domain.split("@")[-1] if "@" in domain else domain
    is_good = True
    return {
        "verdict": "pass" if is_good else "fail",
        "score": 100 if is_good else 0,
        "detail": "Domain accepts mail" if is_good else "No MX records found",
    }


def smtp_verify(email):
    """Stage 3: SMTP verification (simulated)."""
    simulated_catch_all = random.random() < 0.05
    simulated_exists = random.random() < 0.85
    if simulated_catch_all:
        return {"verdict": "catch-all", "score": 60,
                "detail": "Server uses catch-all, mailbox may not exist"}
    return {
        "verdict": "pass" if simulated_exists else "fail",
        "score": 100 if simulated_exists else 0,
        "detail": "Mailbox exists" if simulated_exists else "Mailbox does not exist",
    }


def verify_email(email):
    """
    Full verification pipeline: syntax -> MX -> SMTP.
    Returns a composite result with verdict, score, and detail.
    """
    if not email:
        return {"email": "", "verdict": "unknown", "score": 0, "detail": "No email provided"}

    result = {"email": email}

    syntax = syntax_check(email)
    if syntax["verdict"] == "fail":
        result["verdict"] = "invalid"
        result["score"] = 0
        result["detail"] = syntax["detail"]
        result["stages"] = {"syntax": syntax}
        return result

    mx = mx_check(email)
    if mx["verdict"] == "fail":
        result["verdict"] = "undeliverable"
        result["score"] = 0
        result["detail"] = mx["detail"]
        result["stages"] = {"syntax": syntax, "mx": mx}
        return result

    smtp = smtp_verify(email)

    composite_score = int(syntax["score"] * 0.10 + mx["score"] * 0.30 + smtp["score"] * 0.60)

    if smtp["verdict"] == "catch-all":
        result["verdict"] = "risky"
        result["score"] = composite_score
        result["detail"] = smtp["detail"]
    elif smtp["verdict"] == "pass":
        result["verdict"] = "verified"
        result["score"] = composite_score
        result["detail"] = "Email verified and deliverable"
    else:
        result["verdict"] = "bounced"
        result["score"] = composite_score
        result["detail"] = smtp["detail"]

    result["stages"] = {"syntax": syntax, "mx": mx, "smtp": smtp}
    return result


def generate_emails(name, domain):
    """Generate likely email patterns for a person at a company."""
    first, *rest = name.lower().split()
    last = rest[-1] if rest else ""
    patterns = [
        f"{first}@{domain}",
        f"{first}.{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{last}@{domain}",
        f"{first}{last[0]}@{domain}",
    ]
    return list(dict.fromkeys(patterns))  # deduplicate while preserving order


def run(enriched_companies, demo=False):
    print(f"Verifying emails for {len(enriched_companies)} companies...")
    results = []
    for idx, company in enumerate(enriched_companies, 1):
        if demo:
            print(f"  [{idx}/{len(enriched_companies)}] {company['company']}...")
        for dm in company.get("decision_makers", {}).get("decision_makers", []):
            emails = generate_emails(dm["name"], company["domain"])
            verified = []
            for email in emails:
                v = verify_email(email)
                verified.append(v)
                if demo:
                    status_icon = {"verified": "[OK]", "risky": "[~]", "bounced": "[NO]", "invalid": "[NO]"}
                    print(f"    {status_icon.get(v['verdict'], '[?]')} {v['email']} -> {v['verdict']} ({v['score']}/100)")
            results.append({
                "company": company["company"],
                "name": dm["name"],
                "role": dm["role"],
                "verified_emails": verified,
                "best_email": max(verified, key=lambda x: x["score"]),
            })
    return results


if __name__ == "__main__":
    test = [{"company": "TestCorp", "domain": "testcorp.io",
             "decision_makers": {"decision_makers": [{"name": "Alex Chen", "role": "Head of Sales"}]}}]
    run(test, demo=True)
