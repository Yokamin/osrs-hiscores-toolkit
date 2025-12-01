import logging
import json
import os
from typing import List, Optional

logger = logging.getLogger(__name__)

# --- Skill Groupings ---

COMBAT_SKILLS = [
    "Attack", "Strength", "Defence", "Hitpoints", "Ranged", "Prayer", "Magic"
]

NON_COMBAT_SKILLS = [
    "Farming", "Fishing", "Hunter", "Mining", "Woodcutting", "Cooking", "Crafting",
    "Fletching", "Herblore", "Runecraft", "Smithing", "Agility", "Construction",
    "Firemaking", "Slayer", "Thieving", "Sailing"
]

GATHERING_SKILLS = [
    "Farming", "Fishing", "Hunter", "Mining", "Woodcutting"
]

PRODUCTION_SKILLS = [
    "Cooking", "Crafting", "Fletching", "Herblore", "Runecraft", "Smithing"
]

UTILITY_SKILLS = [
    "Agility", "Construction", "Firemaking", "Slayer", "Thieving", "Sailing"
]

# --- General OSRS Game Constants ---

MAX_TOTAL_LEVEL = 2376  # With 24 skills at 99
MAX_SKILL_LEVEL = 99
MAX_XP = 200000000
MAX_VIRTUAL_LEVEL = 126 # Theoretical max level based on XP curve


# --- XP Table Loading (Cached) ---

_xp_table: Optional[List[int]] = None

def get_xp_table() -> List[int]:
    """
    Loads and caches the XP table from data/xp_table.json.

    This function is designed to be called by other modules to get access to the
    OSRS XP-to-level table. It caches the data in memory after the first read.

    Returns:
        A list of integers representing the XP required for each level, or an
        empty list if the data file cannot be loaded.
    """
    global _xp_table
    if _xp_table is None:
        try:
            # Assuming the script is run from the project root
            file_path = os.path.join('data', 'xp_table.json')
            with open(file_path, 'r') as f:
                _xp_table = json.load(f)
            logger.info("XP table loaded successfully from %s.", file_path)
        except FileNotFoundError:
            logger.error("XP table file not found at %s. Ensure data/xp_table.json exists.", file_path)
            _xp_table = []
        except json.JSONDecodeError:
            logger.error("Failed to decode XP table JSON from %s.", file_path)
            _xp_table = []
    return _xp_table
