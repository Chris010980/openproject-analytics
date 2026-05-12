import argparse
import logging
from datetime import datetime

from parser import OpenProjectParser
from metrics import compute_milestone_metrics
from exporter import (
    export_metrics_json,
    export_metrics_csv,
    export_graph
)


def setup_logging():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"logs/pipeline_{timestamp}.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger("openproject_parser")
    logger.debug(f"Logger initialized. Log file: {log_file}")
    return logger


def main():
    parser = argparse.ArgumentParser(description="OpenProject Analytics Pipeline")

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to OpenProject export file (xlsx/csv)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output/",
        help="Output directory"
    )

    args = parser.parse_args()

    logger = setup_logging()

    logger.info("Starting pipeline")

    # --- Parsing ---
    op_parser = OpenProjectParser(args.input)
    data = op_parser.parse()

    # --- Metrics ---
    metrics = compute_milestone_metrics(data)

    # --- Export ---
    export_metrics_json(metrics, f"{args.output}/metrics.json")
    export_metrics_csv(metrics, f"{args.output}/metrics.csv")
    export_graph(data, f"{args.output}/graph.json")

    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()