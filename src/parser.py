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

        # Get unique milestones
        milestones_df = self.df[self.df["wp_type"] == "Milestone"].drop_duplicates(subset=["wp_id"])
        self.logger.debug(f"Found {len(milestones_df)} unique milestones")

        milestones_dict = {}
        for _, row in milestones_df.iterrows():
            milestone_id = int(row["wp_id"])
            milestones_dict[milestone_id] = {
                "id": milestone_id,
                "title": row["wp_subject"],
                "priority": row.get("wp_priority", "normal"),
                "story_points": int(row.get("wp_story_points", 0)) if pd.notna(row.get("wp_story_points")) else 0,
                "status": row.get("wp_status", ""),
                "risks": [],
                "blocks": [],
                "blocked_by": [],
            }

        # Add relations
        for _, row in self.df.iterrows():
            source_id = int(row["wp_id"])
            if source_id not in milestones_dict:
                continue

            rel_type = row.get("rel_type")
            if not pd.notna(rel_type):
                continue

            # Related To relations
            if rel_type.lower() == "related to" and pd.notna(row.get("risk_id")):
                risk_id = int(row["risk_id"])
                probability = row.get("risk_probability", "intermediate")
                # Check if already in list
                if not any(r["id"] == risk_id for r in milestones_dict[source_id]["risks"]):
                    milestones_dict[source_id]["risks"].append({
                        "id": risk_id,
                        "probability": probability
                    })

            # Blocks relation
            elif rel_type.lower() == "blocks" and pd.notna(row.get("risk_id")):
                target_id = int(row["risk_id"])
                if target_id not in milestones_dict[source_id]["blocks"]:
                    milestones_dict[source_id]["blocks"].append(target_id)

            # Blocked by relation
            elif rel_type.lower() == "blocked by" and pd.notna(row.get("risk_id")):
                target_id = int(row["risk_id"])
                if target_id not in milestones_dict[source_id]["blocked_by"]:
                    milestones_dict[source_id]["blocked_by"].append(target_id)

        milestones = list(milestones_dict.values())
        self.logger.debug(f"Extracted {len(milestones)} milestones with relations")
        return milestones

    def extract_risks(self):
        self.logger.info("Extracting risks")

        # Get unique risks
        risks_df = self.df[self.df["risk_type"] == "Risk"].drop_duplicates(subset=["risk_id"])
        self.logger.debug(f"Found {len(risks_df)} unique risks")

        risks_dict = {}
        for _, row in risks_df.iterrows():
            risk_id = int(row["risk_id"])
            risks_dict[risk_id] = {
                "id": risk_id,
                "title": row["risk_subject"],
                "probability": row.get("risk_probability", "intermediate"),
                "status": row.get("risk_status", ""),
                "milestones": [],
            }

        # Add milestone references
        for _, row in self.df.iterrows():
            rel_type = row.get("rel_type")
            if pd.notna(rel_type) and rel_type.lower() == "related to":
                if pd.notna(row.get("risk_id")):
                    risk_id = int(row["risk_id"])
                    if risk_id in risks_dict:
                        milestone_id = int(row["wp_id"])
                        milestone_priority = row.get("wp_priority", "normal")
                        milestone_story_points = int(row.get("wp_story_points", 0)) if pd.notna(row.get("wp_story_points")) else 0
                        # Check if already in list
                        if not any(m["id"] == milestone_id for m in risks_dict[risk_id]["milestones"]):
                            risks_dict[risk_id]["milestones"].append({
                                "id": milestone_id,
                                "story_points": milestone_story_points,
                                "priority": milestone_priority
                            })

        risks = list(risks_dict.values())
        self.logger.debug(f"Extracted {len(risks)} risks with milestone references")
        return risks

    def extract_relations(self):
        self.logger.info("Extracting relations")

        blocks_relations = []
        blocked_by_relations = []

        seen = set()
        for _, row in self.df.iterrows():
            rel_type = row.get("rel_type")
            if not pd.notna(rel_type):
                continue

            source_id = int(row["wp_id"])
            target_id = row.get("risk_id")
            if not pd.notna(target_id):
                continue

            target_id = int(target_id)

            if rel_type.lower() == "blocks":
                relation_key = (source_id, target_id, "blocks")
                if relation_key not in seen:
                    blocks_relations.append({
                        "from_id": source_id,
                        "to_id": target_id
                    })
                    seen.add(relation_key)

            elif rel_type.lower() == "blocked by":
                relation_key = (source_id, target_id, "blocked_by")
                if relation_key not in seen:
                    blocked_by_relations.append({
                        "from_id": source_id,
                        "to_id": target_id
                    })
                    seen.add(relation_key)

        relations = {
            "blocks": blocks_relations,
            "blocked_by": blocked_by_relations,
        }

        self.logger.debug(f"Extracted {len(blocks_relations)} blocks and {len(blocked_by_relations)} blocked_by relations")
        return relations

    # ----------------------------------

    def _parse_id_list(self, value):
        if isinstance(value, str):
            return [int(x.strip()) for x in value.split(",") if x.strip().isdigit()]
        elif isinstance(value, (int, float)) and pd.notna(value):
            return [int(value)]
        return []