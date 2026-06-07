"""Composite deal health scoring engine. Weighs 6 factors into 0-100 score."""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

DEAL_HEALTH_WEIGHTS = {
    "meddic_completeness": 0.40,
    "account_icp_score": 0.20,
    "stage_velocity": 0.15,
    "engagement_recency": 0.10,
    "acv_fit": 0.10,
    "competitive_risk": 0.05,
}

STAGE_BENCHMARK_DAYS = {
    "discovery": 30,
    "qualification": 45,
    "demo": 30,
    "evaluation": 45,
    "proposal": 30,
    "negotiation": 30,
    "closed_won": 0,
    "closed_lost": 0,
}

STAGE_ORDER = ["discovery", "qualification", "demo", "evaluation", "proposal", "negotiation", "closed_won"]


def score_deal_health(
    meddic_completeness: int = 50,
    account_icp_score: int = 50,
    stage: str = "discovery",
    stage_created_days_ago: int = 30,
    last_call_days_ago: int = 14,
    acv: float = 100000,
    has_competitor: bool = False,
) -> dict:
    """Compute composite deal health score (0-100).

    Args:
        meddic_completeness: MEDDIC completeness 0-100 (from meddic_scorer)
        account_icp_score: Account ICP fit 0-100 (from Agent 1)
        stage: Current deal stage
        stage_created_days_ago: Days since this stage was entered
        last_call_days_ago: Days since last prospect call
        acv: Deal ACV in dollars
        has_competitor: Whether a competitor is actively engaged

    Returns:
        Dict with total_score, breakdown per factor, health_label, and warnings.
    """
    factors = {}
    warnings = []

    # 1. MEDDIC completeness (40%)
    meddic_score = meddic_completeness
    factors["meddic_completeness"] = {"raw": meddic_completeness, "weighted": round(meddic_score * DEAL_HEALTH_WEIGHTS["meddic_completeness"], 1), "weight": DEAL_HEALTH_WEIGHTS["meddic_completeness"]}
    if meddic_completeness < 50:
        warnings.append("MEDDIC completeness below 50% — qualification gaps need attention")

    # 2. Account ICP score (20%)
    icp_score = account_icp_score
    factors["account_icp_score"] = {"raw": account_icp_score, "weighted": round(icp_score * DEAL_HEALTH_WEIGHTS["account_icp_score"], 1), "weight": DEAL_HEALTH_WEIGHTS["account_icp_score"]}

    # 3. Stage velocity (15%)
    benchmark = STAGE_BENCHMARK_DAYS.get(stage, 45)
    if benchmark > 0:
        velocity_ratio = stage_created_days_ago / benchmark
        if velocity_ratio <= 0.5:
            velocity_score = 100
        elif velocity_ratio <= 1.0:
            velocity_score = 80
        elif velocity_ratio <= 1.5:
            velocity_score = 50
        elif velocity_ratio <= 2.0:
            velocity_score = 30
        else:
            velocity_score = 10
            warnings.append(f"Deal has been in '{stage}' for {stage_created_days_ago}d (benchmark: {benchmark}d)")
    else:
        velocity_score = 100

    factors["stage_velocity"] = {"raw": velocity_score, "days_in_stage": stage_created_days_ago, "benchmark_days": benchmark, "weighted": round(velocity_score * DEAL_HEALTH_WEIGHTS["stage_velocity"], 1), "weight": DEAL_HEALTH_WEIGHTS["stage_velocity"]}

    # 4. Engagement recency (10%)
    if last_call_days_ago <= 3:
        recency_score = 100
    elif last_call_days_ago <= 7:
        recency_score = 80
    elif last_call_days_ago <= 14:
        recency_score = 60
    elif last_call_days_ago <= 21:
        recency_score = 40
    elif last_call_days_ago <= 30:
        recency_score = 20
    else:
        recency_score = 10
        warnings.append(f"No contact in {last_call_days_ago}d — deal may be stalling")

    factors["engagement_recency"] = {"raw": recency_score, "days_since_last_call": last_call_days_ago, "weighted": round(recency_score * DEAL_HEALTH_WEIGHTS["engagement_recency"], 1), "weight": DEAL_HEALTH_WEIGHTS["engagement_recency"]}

    # 5. ACV fit (10%)
    # Deals in $500K-$5M range score highest for enterprise GTM
    if acv >= 500000 and acv <= 5000000:
        acv_score = 90
    elif acv >= 200000 and acv < 500000:
        acv_score = 70
    elif acv > 5000000:
        acv_score = 60
    elif acv >= 50000 and acv < 200000:
        acv_score = 50
    else:
        acv_score = 30

    factors["acv_fit"] = {"raw": acv_score, "acv": acv, "weighted": round(acv_score * DEAL_HEALTH_WEIGHTS["acv_fit"], 1), "weight": DEAL_HEALTH_WEIGHTS["acv_fit"]}

    # 6. Competitive risk (5%)
    comp_score = 50 if has_competitor else 100
    if has_competitor:
        warnings.append("Competitor actively engaged — differentiate or risk displacement")

    factors["competitive_risk"] = {"raw": comp_score, "has_competitor": has_competitor, "weighted": round(comp_score * DEAL_HEALTH_WEIGHTS["competitive_risk"], 1), "weight": DEAL_HEALTH_WEIGHTS["competitive_risk"]}

    total = sum(f["weighted"] for f in factors.values())
    total = max(0, min(100, int(total)))

    if total >= 80:
        label = "healthy"
    elif total >= 50:
        label = "at_risk"
    else:
        label = "critical"

    return {
        "total_score": total,
        "health_label": label,
        "factors": factors,
        "warnings": warnings,
        "warning_count": len(warnings),
    }
