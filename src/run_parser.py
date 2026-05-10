from metrics import compute_milestone_metrics
import json
from logger import setup_logger
from parser import OpenProjectParser

INPUT_FILE = "data/export.xlsx"
OUTPUT_FILE = "output/parsed.json"

def main():
    # Setup logger
    logger = setup_logger("openproject_parser", debug=True)

    parser = OpenProjectParser(INPUT_FILE, debug=True)
    data = parser.parse()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Parsed data written to {OUTPUT_FILE}")

    metrics = compute_milestone_metrics(data)

    logger.info("Computed milestone metrics")

    # optional speichern
    with open("output/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    main()