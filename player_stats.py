import logging
from typing import Dict, Optional, List
import math
import hiscores_parser
import json
import os

logger = logging.getLogger(__name__)

# --- Constants ---
MAX_TOTAL_LEVEL = 2376  # 24 skills * 99
MAX_SKILL_LEVEL = 99
COMBAT_SKILLS = [
    "Attack", "Strength", "Defence", "Hitpoints", "Ranged", "Prayer", "Magic"
]

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
            logger.error("XP table file not found at %s. Ensure data/xp_table.json exists.", file_path)
            _xp_table = []
        except json.JSONDecodeError:
            logger.error("Failed to decode XP table JSON from %s.", file_path)
            _xp_table = []
    return _xp_table

# --- Tier 1: Simple Getters ---
def get_skill_level(player_data: Dict, skill_name: str) -> Optional[int]:
    """Retrieves the level for a specific skill from player data.

    Args:
        player_data (Dict): The raw player data dictionary from the API.
        skill_name (str): The name of the skill (e.g., "Attack").

    Returns:
        Optional[int]: The skill level as an integer, or None if not found.
    """
    logger.debug("Attempting to get level for skill: '%s'", skill_name)
    skill_data = hiscores_parser.get_skill_data(player_data, skill_name)
    if skill_data and 'level' in skill_data:
        level = int(skill_data['level'])
        logger.debug("Found level %d for skill '%s'", level, skill_name)
        return level
    logger.warning("Could not find level for skill: '%s'", skill_name)
    return None

def get_skill_xp(player_data: Dict, skill_name: str) -> Optional[int]:
    """Retrieves the experience for a specific skill from player data.

    Args:
        player_data (Dict): The raw player data dictionary from the API.
        skill_name (str): The name of the skill (e.g., "Attack").
        
    Returns:
        Optional[int]: The skill XP as an integer, or None if not found.
    """
    logger.debug("Attempting to get XP for skill: '%s'", skill_name)
    skill_data = hiscores_parser.get_skill_data(player_data, skill_name)
    if skill_data and 'xp' in skill_data:
        xp = int(skill_data['xp'])
        logger.debug("Found %d XP for skill '%s'", xp, skill_name)
        return xp
    logger.warning("Could not find XP for skill: '%s'", skill_name)
    return None

def get_skill_rank(player_data: Dict, skill_name: str) -> Optional[int]:
    """Retrieves the rank for a specific skill from player data.

    Args:
        player_data (Dict): The raw player data dictionary from the API.
        skill_name (str): The name of the skill (e.g., "Attack").
        
    Returns:
        Optional[int]: The skill rank as an integer, or None if not found.
    """
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

# --- Tier 2: Status Checks ---

def is_maxed_total(player_data: Dict) -> bool:
    """Checks if a player has the maximum total level.

    Args:
        player_data (Dict): The raw player data dictionary from the API.

    Returns:
        bool: True if the player is maxed, False otherwise.
    """
    logger.info("Checking for max total level...")
    total_level = get_total_level(player_data)
    is_maxed = total_level == MAX_TOTAL_LEVEL
    logger.info("Player max total status: %s", is_maxed)
    return is_maxed

def is_maxed_combat(player_data: Dict) -> bool:
    """Checks if a player has maxed all combat skills (level 99).

    Args:
        player_data (Dict): The raw player data dictionary from the API.

    Returns:
        bool: True if all combat skills are 99, False otherwise.
    """
    logger.info("Checking for max combat...")
    for skill in COMBAT_SKILLS:
        level = get_skill_level(player_data, skill)
        if level is None or level < MAX_SKILL_LEVEL:
            logger.info("Player is not max combat (skill '%s' is level %s).", skill, level)
            return False
    logger.info("Player is max combat.")
    return True

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
    
    levels = {}
    for skill in COMBAT_SKILLS:
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

def get_xp_to_level(current_xp: int, target_level: int) -> Optional[int]:
    """Calculates the XP required to reach a target skill level.

    Args:
        current_xp (int): The player's current total XP for a skill.
        target_level (int): The desired target level.

    Returns:
        Optional[int]: The amount of XP needed to reach the target level.
                       Returns 0 if the player is already at or past the target level.
                       Returns None if the target level is invalid.
    """
    logger.info("Calculating XP from %d to reach level %d...", current_xp, target_level)
    xp_table = _load_xp_table()
    if not xp_table:
        logger.error("XP table not available, cannot perform calculation.")
        return None
    
    # Validate target level
    if not (1 < target_level <= len(xp_table)):
        logger.error("Invalid target level: %d. Must be between 2 and %d.", target_level, len(xp_table))
        return None

    # Get XP required for the target level. Index is level - 1.
    xp_for_target = xp_table[target_level - 1]

    if current_xp >= xp_for_target:
        logger.info("Current XP (%d) is already at or past the XP for level %d (%d).",
                    current_xp, target_level, xp_for_target)
        return 0
    
    xp_needed = xp_for_target - current_xp
    logger.info("XP needed to reach level %d: %d", target_level, xp_needed)
    return xp_needed

def calculate_total_combat_xp(player_data: Dict) -> Optional[int]:
    """Calculates the total experience for all combat-related skills for a player."""
    logger.info("Calculating total combat XP...")
    
    total_combat_xp = 0
    for skill in COMBAT_SKILLS:
        xp = get_skill_xp(player_data, skill)
        if xp is None or xp < 0:
            xp_to_add = 0
        else:
            xp_to_add = xp
        total_combat_xp += xp_to_add
    
    logger.info("Total combat XP calculated: %d", total_combat_xp)
    return total_combat_xp

def calculate_total_non_combat_xp(player_data: Dict) -> Optional[int]:
    """Calculates the total experience for all non-combat skills for a player."""
    logger.info("Calculating total non-combat XP...")
    non_combat_skills = [
        "Farming", "Fishing", "Hunter", "Mining", "Woodcutting", "Cooking", "Crafting",
        "Fletching", "Herblore", "Runecraft", "Smithing", "Agility", "Construction",
        "Firemaking", "Slayer", "Thieving", "Sailing"
    ]

    total_non_combat_xp = 0
    for skill in non_combat_skills:
        xp = get_skill_xp(player_data, skill)
        if xp is None or xp < 0:
            xp_to_add = 0
        else:
            xp_to_add = xp
        total_non_combat_xp += xp_to_add
        
    logger.info("Total non-combat XP calculated: %d", total_non_combat_xp)
    return total_non_combat_xp

def calculate_total_gathering_xp(player_data: Dict) -> Optional[int]:
    """Calculates the total experience for all gathering skills for a player."""
    logger.info("Calculating total gathering XP...")
    gathering_skills = [
        "Farming", "Fishing", "Hunter", "Mining", "Woodcutting"
    ]

    total_gathering_xp = 0
    for skill in gathering_skills:
        xp = get_skill_xp(player_data, skill)
        if xp is None or xp < 0:
            xp_to_add = 0
        else:
            xp_to_add = xp
        total_gathering_xp += xp_to_add
        
    logger.info("Total gathering XP calculated: %d", total_gathering_xp)
    return total_gathering_xp

def calculate_total_production_xp(player_data: Dict) -> Optional[int]:
    """Calculates the total experience for all production skills for a player."""
    logger.info("Calculating total production XP...")
    production_skills = [
        "Cooking", "Crafting", "Fletching", "Herblore", "Runecraft", "Smithing"
    ]

    total_production_xp = 0
    for skill in production_skills:
        xp = get_skill_xp(player_data, skill)
        if xp is None or xp < 0:
            xp_to_add = 0
        else:
            xp_to_add = xp
        total_production_xp += xp_to_add
        
    logger.info("Total production XP calculated: %d", total_production_xp)
    return total_production_xp

def calculate_total_utility_xp(player_data: Dict) -> Optional[int]:
    """Calculates the total experience for all utility skills for a player."""
    logger.info("Calculating total utility XP...")
    utility_skills = [
        "Agility", "Construction", "Firemaking", "Slayer", "Thieving", "Sailing"
    ]

    total_utility_xp = 0
    for skill in utility_skills:
        xp = get_skill_xp(player_data, skill)
        if xp is None or xp < 0:
            xp_to_add = 0
        else:
            xp_to_add = xp
        total_utility_xp += xp_to_add
        
    logger.info("Total utility XP calculated: %d", total_utility_xp)
    return total_utility_xp