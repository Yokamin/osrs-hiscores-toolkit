import logging
from typing import Dict, Optional, List
import math
import hiscores_parser
import json
import os

logger = logging.getLogger(__name__)

# --- XP Table Loading (Cached) ---
_xp_table: Optional[List[int]] = None

def _load_xp_table() -> List[int]:
    """Loads and caches the XP table from data/xp_table.json."""
    global _xp_table
    if _xp_table is None:
        try:
            file_path = os.path.join('data', 'xp_table.json')
            with open(file_path, 'r') as f:
                _xp_table = json.load(f)
            logger.info("XP table loaded successfully from %s.", file_path)
        except FileNotFoundError:
            logger.error("XP table file not found at %s.", file_path)
            _xp_table = []
        except json.JSONDecodeError:
            logger.error("Failed to decode XP table JSON from %s.", file_path)
            _xp_table = []
    return _xp_table

# --- Tier 1: Simple Getters ---
def get_skill_level(player_data: Dict, skill_name: str) -> Optional[int]:
    """Retrieves the level for a specific skill from player data."""
    logger.debug("Attempting to get level for skill: '%s'", skill_name)
    skill_data = hiscores_parser.get_skill_data(player_data, skill_name)
    if skill_data and 'level' in skill_data:
        level = int(skill_data['level'])
        logger.debug("Found level %d for skill '%s'", level, skill_name)
        return level
    logger.warning("Could not find level for skill: '%s'", skill_name)
    return None

def get_skill_xp(player_data: Dict, skill_name: str) -> Optional[int]:
    """Retrieves the experience for a specific skill from player data."""
    logger.debug("Attempting to get XP for skill: '%s'", skill_name)
    skill_data = hiscores_parser.get_skill_data(player_data, skill_name)
    if skill_data and 'xp' in skill_data:
        xp = int(skill_data['xp'])
        logger.debug("Found %d XP for skill '%s'", xp, skill_name)
        return xp
    logger.warning("Could not find XP for skill: '%s'", skill_name)
    return None

def get_skill_rank(player_data: Dict, skill_name: str) -> Optional[int]:
    """Retrieves the rank for a specific skill from player data."""
    logger.debug("Attempting to get rank for skill: '%s'", skill_name)
    skill_data = hiscores_parser.get_skill_data(player_data, skill_name)
    if skill_data and 'rank' in skill_data:
        rank = int(skill_data['rank'])
        logger.debug("Found rank %d for skill '%s'", rank, skill_name)
        return rank
    logger.warning("Could not find rank for skill: '%s'", skill_name)
    return None

def get_overall_rank(player_data: Dict) -> Optional[int]:
    """Retrieves the overall rank of the player."""
    return get_skill_rank(player_data, "Overall")

def get_total_level(player_data: Dict) -> Optional[int]:
    """Retrieves the total level of the player."""
    return get_skill_level(player_data, "Overall")

def get_overall_xp(player_data: Dict) -> Optional[int]:
    """Retrieves the overall experience of the player."""
    return get_skill_xp(player_data, "Overall")

def get_activity_score(player_data: Dict, activity_name: str) -> Optional[int]:
    """Retrieves the score for a specific activity from player data."""
    logger.debug("Attempting to get score for activity: '%s'", activity_name)
    activity_data = hiscores_parser.get_activity_data(player_data, activity_name)
    if activity_data and 'score' in activity_data:
        score = int(activity_data['score'])
        logger.debug("Found score %d for activity '%s'", score, activity_name)
        return score
    logger.warning("Could not find score for activity: '%s'", activity_name)
    return None

def get_activity_rank(player_data: Dict, activity_name: str) -> Optional[int]:
    """Retrieves the rank for a specific activity from player data."""
    logger.debug("Attempting to get rank for activity: '%s'", activity_name)
    activity_data = hiscores_parser.get_activity_data(player_data, activity_name)
    if activity_data and 'rank' in activity_data:
        rank = int(activity_data['rank'])
        logger.debug("Found rank %d for activity '%s'", rank, activity_name)
        return rank
    logger.warning("Could not find rank for activity: '%s'", activity_name)
    return None

# --- Tier 3: Complex Calculators ---

def get_level_for_xp(xp: int) -> int:
    """Determines the OSRS skill level for a given amount of experience.

    Args:
        xp (int): The total experience points for a skill.

    Returns:
        int: The corresponding skill level (1-126).
    """
    xp_table = _load_xp_table()
    if not xp_table:
        logger.error("XP table not loaded, cannot determine level.")
        return 1
    
    # Iterate backwards through the level table. The XP for level `L` is at index `L-1`.
    for level in range(len(xp_table), 0, -1):
        xp_for_level = xp_table[level - 1]
        if xp >= xp_for_level:
            return level
    return 1 # Should only be returned if xp is negative

def calculate_combat_level(player_data: Dict) -> Optional[float]:
    """Calculates a player's exact combat level based on the OSRS Wiki formula."""
    logger.info("Calculating combat level...")
    required_skills = [
        "Attack", "Strength", "Defence", "Hitpoints", "Ranged", "Prayer", "Magic"
    ]

    levels = {}
    for skill in required_skills:
        level = get_skill_level(player_data, skill)
        if level is None:
            logger.error("Cannot calculate combat level: missing required skill '%s'.", skill)
            return None
        levels[skill] = level
    
    logger.debug("All required combat skill levels found: %s", levels)
    
    attack = levels["Attack"]
    strength = levels["Strength"]
    defence = levels["Defence"]
    hitpoints = levels["Hitpoints"]
    ranged = levels["Ranged"]
    prayer = levels["Prayer"]
    magic = levels["Magic"]

    base = 0.25 * (defence + hitpoints + math.floor(prayer * 0.5))
    melee_contribution = 0.325 * (attack + strength)
    range_contribution = 0.325 * math.floor(ranged * 1.5)
    magic_contribution = 0.325 * math.floor(magic * 1.5)
    
    max_attack_contribution = max(melee_contribution, range_contribution, magic_contribution)
    
    combat_level = base + max_attack_contribution
    logger.info("Calculated combat level: %f", combat_level)
    return combat_level

def get_xp_for_next_level(current_xp: int) -> Optional[int]:
    """Calculates the XP required to reach the next skill level.

    Args:
        current_xp (int): The player's current total XP for a skill.

    Returns:
        Optional[int]: The XP needed for the next level, or None if at max level.
    """
    logger.info("Calculating XP needed for next level from current XP: %d", current_xp)
    xp_table = _load_xp_table()
    if not xp_table:
        logger.error("XP table not available, cannot calculate XP for next level.")
        return None

    current_level = get_level_for_xp(current_xp)
    logger.debug("Current level determined to be: %d", current_level)

    max_level = len(xp_table)
    if current_level >= max_level:
        logger.info("Player is at max level (%d).", max_level)
        return None
    
    # The XP for the NEXT level (e.g., level 2) is at index `current_level` (e.g., index 1)
    xp_for_next_level = xp_table[current_level]
    xp_needed = xp_for_next_level - current_xp
    
    logger.info("XP needed from %d to reach level %d: %d", current_xp, current_level + 1, xp_needed)
    return xp_needed