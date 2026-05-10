# OpenProject Metrics Analysis

This repository contains the Python-based data pipeline for extracting, transforming, and analyzing project management data exported from OpenProject.

## Goals

- Parse OpenProject exports (XLS)
- Extract milestones, risks, relations, and story points
- Generate structured datasets for visualization
- Enable reproducible analytics workflows

## Features

- Risk–Milestone mapping
- Story point aggregation
- Dependency analysis
- Export to JSON/CSV for visualization (D3.js)

## Tech Stack

- Python (pandas, openpyxl)
- Optional: matplotlib / plotly for prototyping

## Structure

- /data # raw exports
- /src # parsing + processing logic
- /output # processed datasets
- /notebooks # optional exploration

## Future Work

- Automated export pipeline
- Integration with GitHub data
- Advanced risk scoring models