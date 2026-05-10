import pandas as pd
from logger import setup_logger


class OpenProjectParser:
    def __init__(self, file_path: str, debug: bool = True):
        self.file_path = file_path
        self.logger = setup_logger(debug=debug)
        self.df = None

    def load(self):
        self.logger.info(f"Loading file: {self.file_path}")

        try:
            self.df = pd.read_excel(self.file_path, engine="openpyxl", header=1)
            self.df.columns = [
                "wp_empty",
                "wp_id",
                "wp_subject",
                "wp_type",
                "wp_status",
                "wp_assignee",
                "wp_priority",
                "wp_story_points",
                "wp_description",
                "rel_empty",
                "rel_type",
                "rel_lag",
                "rel_description",
                "risk_id",
                "risk_subject",
                "risk_type",
                "risk_status",
                "risk_assignee",
                "risk_probability",
            ]
            self.df.columns = [col.strip() for col in self.df.columns]

            self.logger.debug(f"Columns detected: {list(self.df.columns)}")
            self.logger.info(f"Loaded {len(self.df)} rows")

        except Exception as e:
            self.logger.exception("Failed to load XLS file")
            raise e

    def parse(self):
        self.logger.info("Starting parsing process")

        self.load()

        milestones = self.extract_milestones()
        risks = self.extract_risks()
        relations = self.extract_relations()

        self.logger.info("Parsing completed")

        return {
            "milestones": milestones,
            "risks": risks,
            "relations": relations,
        }

    # ----------------------------------

    def extract_milestones(self):
        self.logger.info("Extracting milestones")

        milestones_df = self.df[self.df["wp_type"] == "Milestone"]
        self.logger.debug(f"Found {len(milestones_df)} milestones")

        milestones = []
        for _, row in milestones_df.iterrows():
            milestones.append({
                "id": row["wp_id"],
                "title": row["wp_subject"],
                "priority": row.get("wp_priority", "normal"),
                "story_points": row.get("wp_story_points", 0),
                "status": row.get("wp_status", ""),
            })

        return milestones

    def extract_risks(self):
        self.logger.info("Extracting risks")

        risks_df = self.df[self.df["risk_type"] == "Risk"]
        self.logger.debug(f"Found {len(risks_df)} risks")

        risks = []
        for _, row in risks_df.iterrows():
            risks.append({
                "id": row["risk_id"],
                "title": row["risk_subject"],
                "priority": row.get("risk_type", "normal"),
                "probability": row.get("risk_probability", "intermediate"),
                "status": row.get("risk_status", ""),
            })

        return risks

    def extract_relations(self):
        self.logger.info("Extracting relations")

        relations = []

        for _, row in self.df.iterrows():
            source_id = row["wp_id"]

            rel_type = row.get("rel_type")
            if pd.notna(rel_type) and pd.notna(row.get("risk_id")):
                # Normalize relation type
                if rel_type.lower() == "related to":
                    relation_type = "related_to"
                elif rel_type.lower() == "blocks":
                    relation_type = "blocks"
                elif rel_type.lower() == "blocked by":
                    relation_type = "blocked_by"
                else:
                    continue  # Skip unknown types

                relations.append({
                    "from_id": source_id,
                    "to_id": int(row["risk_id"]),
                    "type": relation_type
                })

        self.logger.debug(f"Extracted {len(relations)} relations")

        return relations

    # ----------------------------------

    def _parse_id_list(self, value):
        if isinstance(value, str):
            return [int(x.strip()) for x in value.split(",") if x.strip().isdigit()]
        elif isinstance(value, (int, float)) and pd.notna(value):
            return [int(value)]
        return []