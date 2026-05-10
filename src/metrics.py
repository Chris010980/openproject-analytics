import logging

logger = logging.getLogger("openproject_parser")

PROBABILITY_WEIGHTS = {
    "Very Low": 1,
    "Low": 2,
    "Intermediate": 3,
    "High": 4,
    "Very High": 5
}


def compute_milestone_metrics(data):
    results = []

    for m in data["milestones"]:
        mid = m["id"]
        title = m["title"]
        story_points = m.get("story_points", 0)

        # --- Risk Exposure ---
        risk_weights = []
        for r in m.get("risks", []):
            prob = r.get("probability", "Low")
            weight = PROBABILITY_WEIGHTS.get(prob, 0)
            risk_weights.append(weight)

        risk_exposure = sum(risk_weights)
        risk_count = len(risk_weights)

        # --- Combined Score (einfacher Ansatz) ---
        # Idee: Aufwand * Risiko
        combined_score = story_points * risk_exposure

        result = {
            "id": mid,
            "title": title,
            "story_points": story_points,
            "risk_exposure": risk_exposure,
            "risk_count": risk_count,
            "combined_score": combined_score
        }

        logger.debug(f"Milestone {mid}: {result}")
        results.append(result)

    return results