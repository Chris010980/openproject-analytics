import json
import pandas as pd
import logging

logger = logging.getLogger("openproject_parser")


def export_metrics_json(metrics, path="output/metrics_flat.json"):
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Exported metrics JSON to {path}")


def export_metrics_csv(metrics, path="output/metrics.csv"):
    df = pd.DataFrame(metrics)
    df.to_csv(path, index=False)
    logger.info(f"Exported metrics CSV to {path}")

def export_graph(data, path="output/graph.json"):
    nodes = []
    links = []

    # --- Milestones ---
    for m in data["milestones"]:
        nodes.append({
            "id": m["id"],
            "type": "milestone",
            "label": m["title"]
        })

        for r in m.get("risks", []):
            links.append({
                "source": m["id"],
                "target": r["id"],
                "type": "risk"
            })

    # --- Risks ---
    for r in data["risks"]:
        nodes.append({
            "id": r["id"],
            "type": "risk",
            "label": r["title"]
        })

    # --- Dependencies ---
    for rel in data["relations"]["blocks"]:
        links.append({
            "source": rel["from_id"],
            "target": rel["to_id"],
            "type": "blocks"
        })

    graph = {
        "nodes": nodes,
        "links": links
    }

    with open(path, "w") as f:
        json.dump(graph, f, indent=2)

    logger.info(f"Exported graph JSON to {path}")