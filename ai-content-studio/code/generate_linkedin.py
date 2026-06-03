#!/usr/bin/env python3
"""Generates LinkedIn post drafts grounded in a brand's voice.

Reads writing-skills.md (compiled brand voice + swipe file + channel rules),
accepts a topic and angle, and produces post variants.

Usage:
    python code/generate_linkedin.py --brand awesome-hires --topic "AI bias in hiring" --demo
    python code/generate_linkedin.py --brand awesome-hires --topic "AI bias in hiring" --demo --dry-run
"""

import argparse
import json
import os
import re
import sys
from datetime import date


VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_PATH", "./brands")

ANGLES = ["thought-leadership", "product", "culture", "educational"]

# Base hashtag pool for demo generation
BROAD_HASHTAGS = ["#hiring", "#ai", "#recruiting", "#hr"]
SPECIFIC_HASHTAGS = ["#hrtech", "#startups", "#dei", "#futureofwork", "#founders", "#talentacquisition"]
BRAND_HASHTAG = "#awesomehires"


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


def generate_demo_variants(topic: str, angle: str, count: int) -> list[dict]:
    """Generate hardcoded demo LinkedIn post variants grounded in the brand voice.

    Variant A is always 'direct' tone (bold claim hook + data-driven body).
    Variant B is always 'storytelling' tone (anecdotal hook + narrative body).
    Additional variants cycle through available tones.
    """
    tones = ["direct", "storytelling", "educational", "contrarian"]
    variants = []

    hooks_direct = [
        f"Most hiring teams are building {topic} into their process without realizing it. Here's the data.",
        f"We analyzed 500+ hiring pipelines and found that {topic} is the #1 factor in screening outcomes.",
        f"Stop pretending {topic} is someone else's problem. Your pipeline has it too.",
    ]
    hooks_story = [
        f"A CTO told me: 'Our AI rejected every qualified candidate last quarter.' That's not a bug. It's {topic}.",
        f"I spent last month inside 12 hiring teams studying {topic}. What I found surprised me.",
        f"A founder I work with said '{topic} keeps me up at night.' So we dug into the data.",
    ]
    hooks_edu = [
        f"Here's a mental model for understanding {topic} — in 3 layers.",
        f"Most teams get {topic} backwards. Here's the framework we use instead.",
    ]
    hooks_contrarian = [
        f"Everyone's worried about {topic} in AI hiring. I think they're worried about the wrong thing.",
        f"Here's the {topic} truth no one in HR tech wants to admit.",
    ]

    bodies_direct = [
        (
            f"The pattern is clear across every dataset we've examined: the tools aren't inherently biased — "
            f"the training data is.\n\n"
            f"When an AI screening model is trained on historical hires from a team that's 80% one demographic, "
            f"it learns to prefer that demographic. It's not malice. It's math.\n\n"
            f"Here's what works instead:\n"
            f"• Audit training data for representation gaps before deployment\n"
            f"• Use deterministic scoring rules that are transparent and testable\n"
            f"• Strip PII before any AI evaluation — name, age, location shouldn't factor\n\n"
            f"The fix isn't less AI. It's better data hygiene and auditability."
        ),
        (
            f"The numbers don't lie: 73% of hiring teams using AI screening tools cannot explain how their "
            f"models make decisions. That's not just a compliance risk — it's a quality risk.\n\n"
            f"When you can't audit the scoring logic, you can't fix the bias. Period.\n\n"
            f"The teams that get this right share three habits:\n"
            f"• They publish their scoring criteria internally\n"
            f"• They run demographic parity checks quarterly\n"
            f"• They treat their AI as a deterministic tool, not a black box\n\n"
            f"Accountability isn't a feature. It's the foundation."
        ),
    ]
    bodies_story = [
        (
            f"We sat down with his team to understand why {topic} was producing skewed results. "
            f"The root cause wasn't the algorithm. It was the historical data — trained on years of hires "
            f"from an industry that's been overwhelmingly homogeneous.\n\n"
            f"They rebuilt the screening criteria from scratch. Same AI engine. New scoring rules. "
            f"Within 60 days, their pipeline diversity improved by 3x at the shortlist stage.\n\n"
            f"The before and after wasn't about changing the model. It was about changing what the model "
            f"was trained to value.\n\n"
            f"Technical debt in hiring takes many forms. Biased training data is the most expensive kind."
        ),
        (
            f"Here's what I learned: most teams don't know their AI is biased until a candidate calls them out. "
            f"By then, the damage is done — to the candidate, to the brand, to the pipeline.\n\n"
            f"The teams that avoid this don't have better AI. They have better processes:\n"
            f"• They test for fairness before going live, not after\n"
            f"• They separate candidate data from AI evaluation entirely\n"
            f"• They build human review checkpoints into every automated decision\n\n"
            f"Fairness isn't a model problem. It's a design problem."
        ),
    ]
    bodies_edu = [
        (
            f"Layer 1: Data — What was your model trained on? If you can't answer this, stop here.\n\n"
            f"Layer 2: Logic — Can you trace every scoring decision to a specific rule? If not, "
            f"you don't have explainability, you have vibes.\n\n"
            f"Layer 3: Outcomes — Are your results consistent across demographic groups? "
            f"Run the parity check. If the numbers don't match, the model needs work.\n\n"
            f"Most teams skip Layer 1 and Layer 3. They wonder why {topic} shows up "
            f"in their pipeline. Now you know."
        ),
    ]
    bodies_contrarian = [
        (
            f"Here's the take: {topic} isn't caused by AI. It's caused by lazy data practices "
            f"that AI exposes.\n\n"
            f"Before AI, the same biases existed — they were just invisible. Hiring managers made "
            f"subjective calls based on gut feel, resume formatting, and schools they recognized.\n\n"
            f"AI didn't create the bias. It made it measurable. And that's actually good news — "
            f"because what you can measure, you can fix.\n\n"
            f"The real question isn't 'is our AI biased?' It's 'are we willing to look at the data?'"
        ),
    ]

    cta_options = [
        "What's your take?",
        "Tag someone who needs to see this",
        "Drop your thoughts in the comments",
        "Have you seen this in your pipeline?",
        "Share this with your hiring team",
    ]

    for i in range(count):
        tone = tones[i % len(tones)]

        if tone == "direct":
            idx = i // len(tones)
            hook = hooks_direct[idx % len(hooks_direct)]
            body = bodies_direct[idx % len(bodies_direct)]
        elif tone == "storytelling":
            idx = i // len(tones)
            hook = hooks_story[idx % len(hooks_story)]
            body = bodies_story[idx % len(bodies_story)]
        elif tone == "educational":
            idx = i // len(tones)
            hook = hooks_edu[idx % len(hooks_edu)]
            body = bodies_edu[idx % len(bodies_edu)]
        else:  # contrarian
            idx = i // len(tones)
            hook = hooks_contrarian[idx % len(hooks_contrarian)]
            body = bodies_contrarian[idx % len(bodies_contrarian)]

        cta = cta_options[i % len(cta_options)]

        # Build hashtags: 2 broad + 2 specific + 1 brand
        # Add a topic-specific hashtag if the topic yields one
        topic_words = topic.lower().split()
        topic_hashtag = None
        for w in topic_words:
            candidate = "#" + re.sub(r"[^a-z0-9]", "", w)
            if candidate not in BROAD_HASHTAGS and candidate not in SPECIFIC_HASHTAGS and candidate != BRAND_HASHTAG:
                topic_hashtag = candidate
                break

        hashtags = list(BROAD_HASHTAGS[:2])
        specific_pool = [h for h in SPECIFIC_HASHTAGS if h not in hashtags]
        hashtags.extend(specific_pool[:2])
        hashtags.append(BRAND_HASHTAG)

        if topic_hashtag and topic_hashtag not in hashtags:
            # Replace last specific with topic hashtag
            hashtags[-2] = topic_hashtag

        # Shuffle isn't needed; just ensure 3-5
        hashtags = hashtags[:5]

        variant_label = chr(ord("a") + i)

        variants.append({
            "variant": variant_label,
            "tone": tone,
            "hook": hook,
            "body": body,
            "cta": cta,
            "hashtags": hashtags,
        })

    return variants


def make_obsidian_doc(variants: list[dict], topic: str, brand: str, angle: str, date_str: str) -> str:
    """Format all variants as a single Obsidian markdown document."""
    lines = [
        f"# LinkedIn: {topic}",
        f"**Brand:** {brand}",
        f"**Angle:** {angle}",
        f"**Date:** {date_str}",
        "",
        "---",
        "",
    ]
    for v in variants:
        lines.extend([
            f"## Variant {v['variant']} ({v['tone']})",
            "",
            v["hook"],
            "",
            v["body"],
            "",
            f"**CTA:** {v['cta']}",
            f"Hashtags: {' '.join(v['hashtags'])}",
            "",
        ])
    return "\n".join(lines).rstrip("\n") + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate LinkedIn post drafts grounded in a brand's voice."
    )
    parser.add_argument("--brand", required=True, help="Brand name (matches vault directory)")
    parser.add_argument("--topic", required=True, help="Topic for the LinkedIn post")
    parser.add_argument(
        "--angle", choices=ANGLES, default="thought-leadership",
        help="Content angle (default: thought-leadership)"
    )
    parser.add_argument(
        "--variants", type=int, default=2,
        help="Number of post variants to generate (default: 2)"
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

    if args.demo:
        variants = generate_demo_variants(args.topic, args.angle, args.variants)
    else:
        print("Real mode requires LLM integration", file=sys.stderr)
        variants = []

    output = {
        "brand": args.brand,
        "content_type": "linkedin_post",
        "topic": args.topic,
        "angle": args.angle,
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

    filename = f"{date_str}-linkedin-{slug}.md"
    filepath = os.path.join(generated_dir, filename)
    doc = make_obsidian_doc(variants, args.topic, args.brand, args.angle, date_str)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"Written to {filepath}", file=sys.stderr)


if __name__ == "__main__":
    main()
