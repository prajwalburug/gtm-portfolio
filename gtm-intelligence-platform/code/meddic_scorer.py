"""MEDDIC scoring engine. Scores 6 dimensions 0-10, detects gaps, ranks by risk, generates NBA."""

from __future__ import annotations
from typing import Any

MEDDIC_DIMENSIONS = [
    {"key": "metrics", "label": "M - Metrics", "description": "Quantified ROI established"},
    {"key": "economic_buyer", "label": "E - Economic buyer", "description": "Budget approver identified and engaged"},
    {"key": "decision_criteria", "label": "D1 - Decision criteria", "description": "Must-haves defined by prospect"},
    {"key": "decision_process", "label": "D2 - Decision process", "description": "Procurement steps mapped"},
    {"key": "identified_pain", "label": "I - Identified pain", "description": "Specific pain with business impact"},
    {"key": "champion", "label": "C - Champion", "description": "Internal advocate confirmed"},
]

GAP_RISK_WEIGHTS = {
    "economic_buyer": 1.5,
    "champion": 1.3,
    "decision_process": 1.2,
    "identified_pain": 1.3,
    "metrics": 1.0,
    "decision_criteria": 1.0,
}

GAP_THRESHOLD = 5

NBA_MAP = {
    "economic_buyer": {"action": "Arrange economic buyer intro call", "template": "Ask {champion} to arrange a 20-min {eb_name} intro call this week. Missing economic buyer is the #1 deal killer at this stage."},
    "champion": {"action": "Develop champion", "template": "Identify and develop a champion within {company}. No internal advocate means no path to close."},
    "decision_process": {"action": "Map procurement process", "template": "Ask {champion} to walk through the procurement process step by step. Write down names, stages, and approval thresholds."},
    "identified_pain": {"action": "Quantify pain in dollars", "template": "Quantify the business impact of {pain_area} in dollar terms. 'Significant time savings' is not enough — calculate hourly cost."},
    "metrics": {"action": "Build ROI model", "template": "Deliver a structured ROI document showing payback period, hours saved, and dollar impact. Use {metrics_source} data to build the case."},
    "decision_criteria": {"action": "Define must-haves", "template": "Ask {champion} to write down the top 3 evaluation criteria. Without defined criteria, you're solving for the wrong problem."},
}


def score_dimensions(scores: dict[str, int]) -> dict:
    """Score MEDDIC dimensions and detect gaps.

    Args:
        scores: Dict mapping dimension key to score 0-10
            e.g. {"metrics": 3, "economic_buyer": 2, "decision_criteria": 6,
                   "decision_process": 2, "identified_pain": 8, "champion": 7}

    Returns:
        Dict with dimension_scores[], gaps[], gap_count, top_gap, meddic_completeness (0-100)
    """
    result = {"dimension_scores": [], "gaps": [], "gap_count": 0, "top_gap": None, "meddic_completeness": 0}

    raw_total = 0.0
    gaps = []

    for dim in MEDDIC_DIMENSIONS:
        key = dim["key"]
        score = max(0, min(10, scores.get(key, 0)))
        is_gap = score < GAP_THRESHOLD
        risk_weight = GAP_RISK_WEIGHTS.get(key, 1.0)
        gap_status = "gap_detected" if is_gap else "covered"

        entry = {
            "key": key,
            "label": dim["label"],
            "description": dim["description"],
            "score": score,
            "is_gap": is_gap,
            "risk_weight": risk_weight,
            "status": gap_status,
            "risk_label": "critical" if is_gap and key == "economic_buyer" else ("high" if is_gap and risk_weight >= 1.2 else "medium") if is_gap else "none",
        }

        if is_gap:
            entry["nba"] = NBA_MAP.get(key, {}).get("template", "")
            gaps.append(entry)

        raw_total += score
        result["dimension_scores"].append(entry)

    # MEDDIC completeness: average of 6 dimensions, scaled to 0-100
    result["meddic_completeness"] = int((raw_total / 60.0) * 100)

    # Rank gaps by risk weight (highest first)
    gaps.sort(key=lambda g: g["risk_weight"], reverse=True)
    result["gaps"] = gaps
    result["gap_count"] = len(gaps)
    result["top_gap"] = gaps[0]["key"] if gaps else None

    return result


def generate_nba(scored: dict, deal_context: dict | None = None) -> dict:
    """Generate a single next best action from the top gap."""
    ctx = deal_context or {}
    top_gap_key = scored.get("top_gap")
    if not top_gap_key:
        return {"nba_text": "No gaps detected. Continue progressing the deal.", "top_gap": None, "action": None}

    gap_entry = next((g for g in scored["gaps"] if g["key"] == top_gap_key), None)
    nba_info = NBA_MAP.get(top_gap_key, {})

    template = nba_info.get("template", "")
    nba_text = template.format(
        champion=ctx.get("champion_name", "the champion"),
        company=ctx.get("company", "the company"),
        eb_name=ctx.get("eb_name", "the economic buyer"),
        pain_area=ctx.get("pain_area", "the identified pain"),
        metrics_source=ctx.get("metrics_source", "transcript"),
    )

    return {
        "nba_text": nba_text,
        "top_gap": top_gap_key,
        "top_gap_score": gap_entry["score"] if gap_entry else None,
        "top_gap_risk": gap_entry["risk_label"] if gap_entry else None,
        "action": nba_info.get("action", ""),
        "gap_count": scored["gap_count"],
    }


def score_from_transcript(transcript_text: str) -> dict:
    """Score MEDDIC dimensions from transcript text using keyword heuristics.

    In production, this would call an LLM. In demo mode, uses rule-based
    keyword scoring to extract dimension signals from call text.
    """
    text_lower = transcript_text.lower()

    scores = {}

    # Metrics — look for numbers, ROI language, quantification
    metric_keywords = ["hours", "dollars", "percent", "%", "roi", "payback", "saving", "cost", "budget"]
    metrics_count = sum(1 for kw in metric_keywords if kw in text_lower)
    scores["metrics"] = min(10, metrics_count + 2)

    # Economic buyer — look for CFO/CEO/VP mentions as decision makers
    eb_keywords = ["cfo", "ceo", "sign", "approve", "budget holder", "economic buyer", "signs the check"]
    eb_count = sum(1 for kw in eb_keywords if kw in text_lower)
    has_eb_present = any(p in text_lower for p in ["sarah chen", "mark chen"])
    scores["economic_buyer"] = min(10, eb_count + (4 if has_eb_present else 1))

    # Decision criteria — look for requirements, must-haves
    dc_keywords = ["requirement", "must have", "need", "criteria", "integration", "api"]
    dc_count = sum(1 for kw in dc_keywords if kw in text_lower)
    scores["decision_criteria"] = min(10, dc_count + 1)

    # Decision process — look for procurement steps, timeline
    dp_keywords = ["process", "timeline", "board", "quarter", "procurement", "evaluation", "stage"]
    dp_count = sum(1 for kw in dp_keywords if kw in text_lower)
    red_flags = ["figure out the process", "we'll figure it out", "not sure yet", "tbd"]
    has_red_flag = any(rf in text_lower for rf in red_flags)
    scores["decision_process"] = max(1, min(10, dp_count - (3 if has_red_flag else 0)))

    # Identified pain — look for pain language
    pain_keywords = ["pain", "frustrat", "slow", "manual", "broken", "not scaling", "delay", "risk", "problem"]
    pain_count = sum(1 for kw in pain_keywords if kw in text_lower)
    scores["identified_pain"] = min(10, pain_count + 3)

    # Champion — look for advocacy language
    champ_keywords = ["we need this", "exactly what we need", "champion", "advocate", "org chart", "internal"]
    champ_count = sum(1 for kw in champ_keywords if kw in text_lower)
    scores["champion"] = min(10, champ_count + 3)

    return scores
