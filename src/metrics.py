import logging

logger = logging.getLogger("openproject_parser")

PROBABILITY_WEIGHTS = {
    "Very Low": 1,
    "Low": 2,
    "Intermediate": 3,
    "High": 4,
    "Very High": 5
}

MAX_RISK_WEIGHT = max(PROBABILITY_WEIGHTS.values())


def compute_milestone_metrics(data):
    results = []

    for m in data["milestones"]:
        mid = m["id"]
        title = m["title"]
        story_points = m.get("story_points", 0)

        # --- Risk weights sammeln ---
        risk_weights = []
        for r in m.get("risks", []):
            prob = r.get("probability", "Low")
            weight = PROBABILITY_WEIGHTS.get(prob, 0)
            risk_weights.append(weight)

        risk_exposure = sum(risk_weights)
        risk_count = len(risk_weights)

        # --- Neue Metriken ---
        max_possible = risk_count * MAX_RISK_WEIGHT if risk_count > 0 else 1

        normalized_risk = risk_exposure / max_possible
        avg_risk = risk_exposure / risk_count if risk_count > 0 else 0
        risk_density = risk_exposure / story_points if story_points > 0 else 0

        # --- Combined Score ---
        combined_score = story_points * risk_exposure

        result = {
            "id": mid,
            "title": title,
            "story_points": story_points,
            "risk_exposure": risk_exposure,
            "risk_count": risk_count,
            "normalized_risk": round(normalized_risk, 3),
            "avg_risk": round(avg_risk, 3),
            "risk_density": round(risk_density, 3),
            "combined_score": combined_score
        }

        logger.debug(f"Milestone {mid}: {result}")
        results.append(result)

    return results