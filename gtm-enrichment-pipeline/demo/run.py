#!/usr/bin/env python3
"""
End-to-end demo of the GTM Enrichment Pipeline.

Runs:
  1. Load sample companies
  2. Waterfall enrichment (Clay-style)
  3. Email verification (Million Verifier-style)
  4. Scoring and routing
  5. Smartlead export

Usage:
  python demo/run.py [--input samples/input_companies.csv] [--output samples/output_enriched.csv]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows import enrichment_waterfall, email_verifier, scoring_engine, smartlead_format

SAMPLE_DIR = Path(__file__).parent.parent / "samples"
DEFAULT_INPUT = SAMPLE_DIR / "input_companies.csv"
DEFAULT_OUTPUT = SAMPLE_DIR / "output_enriched.csv"


def main():
    parser = argparse.ArgumentParser(description="Run GTM Enrichment Pipeline Demo")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input CSV path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output CSV path")
    args = parser.parse_args()

    print("=" * 60)
    print("  GTM Enrichment Pipeline — End-to-End Demo")
    print("=" * 60)

    # Step 1: Load companies
    print("\nStep 1: Loading target companies...")
    companies = enrichment_waterfall.load_companies(args.input)
    print(f"  Loaded {len(companies)} companies from {args.input}")

    # Step 2: Waterfall enrichment
    print("\nStep 2: Enrichment Waterfall (Clay-style)...")
    enriched = enrichment_waterfall.run(companies, demo=True)

    # Step 3: Email verification
    print("\nStep 3: Email Verification (Million Verifier pattern)...")
    verified = email_verifier.run(enriched, demo=True)

    # Step 4: Scoring
    print("\nStep 4: Lead Scoring & Routing...")
    scored = scoring_engine.run(verified, enriched, demo=True)

    # Step 5: Smartlead export
    print("\nStep 5: Smartlead Export...")
    exported = smartlead_format.run(scored, output_path=args.output, demo=True)

    print(f"\n{'=' * 60}")
    print(f"  Done! {len(exported)} leads exported to {args.output}")
    print(f"{'=' * 60}")

    summary = {
        "companies_loaded": len(companies),
        "leads_enriched": len(enriched),
        "emails_verified": len(verified),
        "scored": len(scored),
        "exported": len(exported),
    }
    print(f"\nSummary: {json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    import json
    main()
