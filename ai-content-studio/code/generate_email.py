#!/usr/bin/env python3
"""Generates cold email, newsletter, and follow-up drafts grounded in a brand's voice.

Reads writing-skills.md (compiled brand voice + swipe file + channel rules),
accepts a topic and email type, and produces email variants.

Usage:
    python code/generate_email.py --brand awesome-hires --topic "30-min screening" --type cold --demo
    python code/generate_email.py --brand awesome-hires --topic "fair hiring" --type newsletter --demo --dry-run
    python code/generate_email.py --brand awesome-hires --topic "checking in" --type follow-up --dry-run
"""

import argparse
import json
import os
import re
import sys
from datetime import date


VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_PATH", "./brands")

EMAIL_TYPES = ["cold", "newsletter", "follow-up"]


def load_writing_skills(brand: str, vault_root: str) -> str:
    """Load writing-skills.md for the brand. Exits with error if missing."""
    path = os.path.join(vault_root, brand, "writing-skills.md")
    if not os.path.isfile(path):
        print(f"Error: writing-skills.md not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return f.read()


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def generate_demo_variants(topic: str, email_type: str, count: int) -> list[dict]:
    """Generate hardcoded demo email variants grounded in the brand voice.

    Content is based on the Awesome Hires brand: AI-powered hiring platform that
    screens, interviews, and shortlists candidates in 30 minutes.
    """
    if email_type == "cold":
        return _demo_cold(topic, count)
    elif email_type == "newsletter":
        return _demo_newsletter(topic, count)
    elif email_type == "follow-up":
        return _demo_followup(topic, count)
    return []


def _demo_cold(topic: str, count: int) -> list[dict]:
    """Generate demo cold email variants."""
    subjects = [
        f"A faster way to handle {topic}",
        f"Your team vs. the {topic} bottleneck",
    ]
    previews = [
        "Your team stops scheduling. Candidates get evaluated 24/7.",
        "Consistent evaluation, ranked shortlists — no scheduling calls needed.",
    ]
    greetings = ["Hi {{name}},"] * count

    bodies_a = (
        f"Hiring teams spend more time scheduling interviews than evaluating candidates. "
        f"When every hire matters, that's time you don't have.\n\n"
        f"We built a platform that handles the entire screening workflow — from application "
        f"to ranked shortlist — without a single scheduling call. Candidates apply, get "
        f"evaluated by AI voice interview in real time, and your team receives a ranked "
        f"shortlist with evidence reports.\n\n"
        f"The process is consistent for every candidate: same questions, same scoring, "
        f"same evaluation criteria. No bias, no gut feelings, no administrative fatigue.\n\n"
        f"Here's the part that matters most for {topic}: we do it in 30 minutes per candidate."
    )

    bodies_b = (
        f"Every hiring team we talk to says the same thing: {topic} is where their "
        f"pipeline slows down. Screening takes too long, evaluation is inconsistent, "
        f"and the best candidates get offers elsewhere while you're still scheduling.\n\n"
        f"There's a better pattern: run evaluation 24/7 with AI that asks the same "
        f"competency-based questions to every applicant. No scheduling. No interviewer "
        f"fatigue. No unconscious bias from the first conversation.\n\n"
        f"The result is a ranked shortlist your team can review in minutes — with "
        f"interview transcripts, scores, and a fitment report for every candidate."
    )

    bodies = [bodies_a, bodies_b]
    ctas = ["Book a 15-min demo \u2192", "See the platform in action \u2192"]
    subjects = subjects[:count]
    if count > len(subjects):
        subjects.extend([
            f"Quick question about your hiring pipeline",
            f"Cut screening time for {topic}",
        ])
        subjects = subjects[:count]
    previews = previews[:count]
    if count > len(previews):
        previews.extend([
            "AI voice interviews that run 24/7. Ranked shortlists in hours.",
            "From application to shortlist without a single calendar ping.",
        ])
        previews = previews[:count]

    # Ensure minimum 2 variants
    while len(subjects) < count:
        subjects.append(f"A more consistent way to screen talent")
        previews.append("Deterministic scoring, evidence reports, one surface.")
        bodies.append(bodies_b)
        ctas.append("Book a 15-min demo \u2192")

    variants = []
    for i in range(count):
        label = chr(ord("a") + i)
        variants.append({
            "variant": label,
            "type": "cold",
            "subject": subjects[i],
            "preview_text": previews[i],
            "greeting": "Hi {{name}},",
            "body": bodies[i % len(bodies)],
            "cta": ctas[i % len(ctas)],
        })

    return variants


def _demo_newsletter(topic: str, count: int) -> list[dict]:
    """Generate demo newsletter variants."""
    subjects = [
        f"This week in {topic}: what's working",
        f"Your {topic} roundup \u2014 3 reads, 1 insight",
    ]
    previews = [
        "Data-driven hiring insights, tools, and frameworks for your team.",
        "Fresh perspectives on fair evaluation and faster hiring pipelines.",
    ]

    body_a = (
        f"Here's what caught our attention this week on {topic}:\n\n"
        f"**1. The case for structured interviews**\n"
        f"A growing body of research shows that structured interviews — where every "
        f"candidate is asked the same questions — produce significantly more reliable "
        f"hiring signals than unstructured conversations. We've seen teams improve "
        f"shortlist quality by 40% just by standardizing their interview framework.\n\n"
        f"**2. Why speed matters in screening**\n"
        f"The window to engage top candidates is shrinking. Teams that respond within "
        f"24 hours convert at 3x the rate of teams that take a week. The bottleneck "
        f"is almost never the decision — it's the scheduling.\n\n"
        f"**3. Bias-proofing your pipeline**\n"
        f"PII-safe evaluation isn't just a compliance checkbox. When you strip candidate "
        f"personal data before AI assessment, you remove the most common source of "
        f"unconscious bias from the screening stage.\n\n"
        f"**Resources**\n"
        f"\u2022 [Read: How to design fair screening rounds \u2192]\n"
        f"\u2022 [Try: Set up a 30-min AI interview round \u2192]\n"
        f"\u2022 [Watch: Product demo (2 min) \u2192]"
    )

    body_b = (
        f"Three things we're thinking about this week on {topic}:\n\n"
        f"**1. Consistency beats intuition**\n"
        f"The best hiring teams don't have better instincts. They have better systems. "
        f"Deterministic scoring rules applied to every candidate produce fairer outcomes "
        f"than any human evaluating resumes on a Friday afternoon.\n\n"
        f"**2. Past talent is untapped talent**\n"
        f"Every job posting triggers a new search. But your best hire might already be "
        f"in your applicant pool. Semantic matching against past applicants surfaces "
        f"strong candidates you've already evaluated — no new sourcing needed.\n\n"
        f"**3. AI interviews scale fairness**\n"
        f"When you automate the screening conversation, you don't just save time. You "
        f"ensure every candidate gets the same questions, the same evaluation, and the "
        f"same opportunity to demonstrate their fit.\n\n"
        f"\u2014 The Awesome Hires Team\n\n"
        f"[Subscribe to this newsletter \u2192]  \u2022  [Read past editions \u2192]"
    )

    bodies = [body_a, body_b]

    while len([s for s in subjects[:count]]) < count:
        subjects.append(f"Fresh thinking on {topic}")
        previews.append("Evidence-backed hiring insights delivered weekly.")

    variants = []
    for i in range(count):
        label = chr(ord("a") + i)
        variants.append({
            "variant": label,
            "type": "newsletter",
            "subject": subjects[i],
            "preview_text": previews[i],
            "greeting": "Hi there,",
            "body": bodies[i % len(bodies)],
            "cta": "Share this with your team \u2192",
        })

    return variants


def _demo_followup(topic: str, count: int) -> list[dict]:
    """Generate demo follow-up email variants."""
    subjects = [
        f"Following up on {topic}",
        f"One more thought on {topic}",
    ]
    previews = [
        "Quick check-in — worth a few minutes of your time?",
        "Wanted to circle back on your hiring workflow.",
    ]

    body_a = (
        f"I wanted to follow up on my previous note about how Awesome Hires handles {topic}.\n\n"
        f"Since we last spoke, we've been running pilots with a few hiring teams and the "
        f"feedback has been consistent: teams are cutting their screening time by over 60% "
        f"while maintaining — and in most cases improving — candidate quality.\n\n"
        f"The key insight? When evaluation runs 24/7, candidates never wait for the next "
        f"available slot. They apply, get assessed, and your team gets a ranked shortlist "
        f"within hours.\n\n"
        f"Would you be open to a 15-minute call to see if this fits your hiring workflow?"
    )

    body_b = (
        f"I'm circling back on my earlier email about {topic}.\n\n"
        f"A quick update: we've added past talent matching — so when you post a new role, "
        f"the system automatically surfaces strong candidates from your existing applicant "
        f"pool ranked by fit score.\n\n"
        f"Curious if this resonates with what you're looking for right now?"
    )

    bodies = [body_a, body_b]
    ctas = [
        "Got 15 minutes to chat?",
        "Does this match what you need?",
    ]

    variants = []
    for i in range(count):
        label = chr(ord("a") + i)
        variants.append({
            "variant": label,
            "type": "follow-up",
            "subject": subjects[i],
            "preview_text": previews[i],
            "greeting": "Hi {{name}},",
            "body": bodies[i % len(bodies)],
            "cta": ctas[i % len(ctas)],
        })

    return variants


def make_obsidian_doc(variants: list[dict], topic: str, brand: str,
                      email_type: str, date_str: str) -> str:
    """Format all variants as a single Obsidian markdown document."""
    type_label = email_type.title()
    lines = [
        f"# Email: {topic}",
        f"**Brand:** {brand}",
        f"**Type:** {type_label}",
        f"**Date:** {date_str}",
        "",
        "---",
        "",
    ]
    for v in variants:
        lines.extend([
            f"## Variant {v['variant']} ({v['type'].title()})",
            "",
            f"**Subject:** {v['subject']}",
            f"**Preview:** {v['preview_text']}",
            "",
            v["greeting"],
            "",
            v["body"],
            "",
            f"**CTA:** {v['cta']}",
            "",
        ])
    return "\n".join(lines).rstrip("\n") + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate email drafts grounded in a brand's voice."
    )
    parser.add_argument("--brand", required=True, help="Brand name (matches vault directory)")
    parser.add_argument("--topic", required=True, help="Topic for the email")
    parser.add_argument(
        "--type", choices=EMAIL_TYPES, required=True,
        help="Email type: cold, newsletter, or follow-up"
    )
    parser.add_argument(
        "--variants", type=int, default=2,
        help="Number of email variants to generate (default: 2)"
    )
    parser.add_argument("--demo", action="store_true", help="Use hardcoded demo content (no LLM call)")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print JSON to stdout and skip file writes"
    )
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    vault_root = VAULT_ROOT
    brand_path = os.path.join(vault_root, args.brand)

    # Validate brand directory exists
    if not os.path.isdir(brand_path):
        print(f"Error: brand directory not found at {brand_path}", file=sys.stderr)
        available = [
            d for d in os.listdir(vault_root)
            if os.path.isdir(os.path.join(vault_root, d))
        ]
        if available:
            print(f"Available brands: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)

    # Load writing-skills.md — required for real mode; checked here so error is consistent
    load_writing_skills(args.brand, vault_root)

    date_str = date.today().isoformat()
    slug = slugify(args.topic)
    content_type = f"email_{args.type}"

    if args.demo:
        variants = generate_demo_variants(args.topic, args.type, args.variants)
    else:
        print("Real mode requires LLM integration. Use --demo for sample output.", file=sys.stderr)
        variants = []

    output = {
        "brand": args.brand,
        "content_type": content_type,
        "topic": args.topic,
        "variants": variants,
        "dry_run": args.dry_run,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))

    if args.dry_run or not variants:
        if args.dry_run:
            print("[dry-run] No files written.", file=sys.stderr)
        return

    # Write single markdown file with all variants
    generated_dir = os.path.join(brand_path, "generated")
    os.makedirs(generated_dir, exist_ok=True)

    filename = f"{date_str}-email-{args.type}-{slug}.md"
    filepath = os.path.join(generated_dir, filename)
    doc = make_obsidian_doc(variants, args.topic, args.brand, args.type, date_str)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"Written to {filepath}", file=sys.stderr)


if __name__ == "__main__":
    main()
