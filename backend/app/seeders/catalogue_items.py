"""Catalogue items seeder data.

This file imports catalogue items from JSON file.
Data is sourced from docs/plans/global-catalogue-items.md
"""

import json
from pathlib import Path

# Load catalogue items from JSON file
_json_path = Path(__file__).parent / "catalogue_items.json"

with open(_json_path, "r", encoding="utf-8") as f:
    CATALOGUE_ITEMS = json.load(f)
