import logging
import math
from typing import Dict, Optional, List

from src import osrs_data

logger = logging.getLogger(__name__)

# --- Status Checks ---

def is_maxed_total(total_level: Optional[int]) -> bool:
    """
    Checks if a player has the maximum total level.

    Args:
        total_level (Optional[int]): The player's total level.

    Returns:
        bool: True if the player is maxed, False otherwise.

    Example:
        >>> is_maxed_total(osrs_data.MAX_TOTAL_LEVEL)
        True
        >>> is_maxed_total(2300)
        False
        >>> is_maxed_total(None)
        False
    """
    logger.info("Checking for max total level...")
    if total_level is None:
        logger.info("Player max total status: False (total_level is None).")
        return False
    is_maxed = total_level == osrs_data.MAX_TOTAL_LEVEL
    logger.info("Player max total status: %s", is_maxed)
    return is_maxed

def is_maxed_combat(combat_levels: Dict[str, int]) -> bool:
    """
    Checks if a player has maxed all combat skills (level 99).

    Args:
        combat_levels (Dict[str, int]): A dictionary mapping combat skill names to their levels.
                                       Expected to contain "Attack", "Strength", "Defence",
                                       "Hitpoints", "Ranged", "Prayer", "Magic".

    Returns:
        bool: True if all combat skills are maxed, False otherwise.

    Example:
        >>> maxed_combat_levels = {
        ...     "Attack": 99, "Strength": 99, "Defence": 99, "Hitpoints": 99,
        ...     "Ranged": 99, "Prayer": 99, "Magic": 99
        ... }
        >>> is_maxed_combat(maxed_combat_levels)
        True
        >>> non_maxed_combat_levels = {
        ...     "Attack": 99, "Strength": 99, "Defence": 99, "Hitpoints": 99,
        ...     "Ranged": 98, "Prayer": 99, "Magic": 99
        ... }
        >>> is_maxed_combat(non_maxed_combat_levels)
        False
    """
    logger.info("Checking for max combat...")
    for skill in osrs_data.COMBAT_SKILLS:
        level = combat_levels.get(skill)
        if level is None or level < osrs_data.MAX_SKILL_LEVEL:
            logger.info("Player is not max combat (skill '%s' is level %s).", skill, level)
            return False
    logger.info("Player is max combat.")
    return True

# --- Complex Calculators ---

def get_level_for_xp(xp: int) -> int:
    """
    Determines the OSRS skill level for a given amount of experience.

    Args:
        xp (int): The total experience points for a skill.

    Returns:
        int: The corresponding skill level (1-126).

    Example:
        >>> get_level_for_xp(0)
        1
        >>> get_level_for_xp(83)
        2
        >>> get_level_for_xp(13034431)
        99
        >>> get_level_for_xp(osrs_data.MAX_XP)
        126
    """
    xp_table = osrs_data.get_xp_table()
    if not xp_table:
        logger.error("XP table not loaded, cannot determine level.")
        return 1
    
    # Iterate backwards through the level table. The XP for level `L` is at index `L-1`.
    for level in range(len(xp_table), 0, -1):
        xp_for_level = xp_table[level - 1]
        if xp >= xp_for_level:
            return level
    return 1  # Should only be returned if xp is negative

def get_xp_for_level(level: int) -> Optional[int]:
    """
    Determines the total experience points required to reach a specific OSRS skill level.

    Args:
        level (int): The target skill level (1-126).

    Returns:
        Optional[int]: The total experience points needed for that level, or None if level is invalid.

    Example:
        >>> get_xp_for_level(1)
        0
        >>> get_xp_for_level(2)
        83
        >>> get_xp_for_level(99)
        13034431
        >>> get_xp_for_level(127) is None
        True
    """
    xp_table = osrs_data.get_xp_table()
    if not xp_table:
        logger.error("XP table not available, cannot determine XP for level %d.", level)
        return None
    
    if not (1 <= level <= osrs_data.MAX_VIRTUAL_LEVEL):
        logger.error("Invalid level: %d. Must be between 1 and %d.", level, osrs_data.MAX_VIRTUAL_LEVEL)
        return None
    
    return xp_table[level - 1]

def calculate_xp_difference(start_xp: int, target_xp: int) -> int:
    """
    Calculates the difference in XP between a starting XP value and a target XP value.

    Args:
        start_xp (int): The starting experience points.
        target_xp (int): The target experience points.

    Returns:
        int: The XP difference (target_xp - start_xp). Can be negative if start_xp > target_xp.

    Example:
        >>> calculate_xp_difference(0, 83)
        83
        >>> calculate_xp_difference(100, 50)
        -50
    """
    return target_xp - start_xp

def calculate_combat_level(levels: Dict[str, int]) -> float:
    """
    Calculates a player's exact combat level based on the OSRS Wiki formula.

    Args:
        levels (Dict[str, int]): A dictionary containing the player's levels for all required
                                combat skills ("Attack", "Strength", "Defence", "Hitpoints",
                                "Ranged", "Prayer", "Magic").

    Returns:
        float: The exact combat level.

    Example:
        >>> example_levels = {
        ...     "Attack": 99, "Strength": 99, "Defence": 99, "Hitpoints": 99,
        ...     "Ranged": 99, "Prayer": 99, "Magic": 99
        ... }
        >>> calculate_combat_level(example_levels)
        126.0
        >>> example_levels_2 = {
        ...     "Attack": 75, "Strength": 75, "Defence": 75, "Hitpoints": 75,
        ...     "Ranged": 1, "Prayer": 1, "Magic": 1
        ... }
        >>> calculate_combat_level(example_levels_2)
        97.5
    """
    logger.info("Calculating combat level...")
    
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
    """
    Calculates the XP required to reach the next skill level from the current XP.

    Args:
        current_xp (int): The player's current experience points for a skill.

    Returns:
        Optional[int]: The XP needed to reach the next level, or None if already at max virtual level.

    Example:
        >>> get_xp_to_next_level(0) # XP for level 1
        83
        >>> get_xp_to_next_level(13034430) # XP just before level 99
        1
        >>> get_xp_to_next_level(osrs_data.MAX_XP) is None # At max virtual level
        True
    """
    logger.info("Calculating XP needed for next level from current XP: %d", current_xp)
    
    current_level = get_level_for_xp(current_xp)
    logger.debug("Current level determined to be: %d", current_level)

    if current_level >= osrs_data.MAX_VIRTUAL_LEVEL:
        logger.info("Player is at max virtual level (%d).", osrs_data.MAX_VIRTUAL_LEVEL)
        return None
    
    xp_for_next_level = get_xp_for_level(current_level + 1)
    
    if xp_for_next_level is None: # Should not happen if XP table is loaded and level is valid
        logger.error("Could not determine XP for next level (%d).", current_level + 1)
        return None

    xp_needed = calculate_xp_difference(current_xp, xp_for_next_level)
    
    logger.info("XP needed from %d to reach level %d: %d", current_xp, current_level + 1, xp_needed)
    return xp_needed



# --- XP Aggregators ---

def calculate_total_xp(xp_values: List[int]) -> int:
    """
    Calculates the total experience from a list of XP values.

    Args:
        xp_values (List[int]): A list of experience points. Non-positive values will be ignored.

    Returns:
        int: The sum of all valid experience points in the list.

    Example:
        >>> calculate_total_xp([100, 200, 300])
        600
        >>> calculate_total_xp([100, None, 200, -50])
        300
        >>> calculate_total_xp([])
        0
    """
    logger.info("Calculating total XP from list of %d values...", len(xp_values))
    total_xp = sum(xp for xp in xp_values if xp is not None and xp > 0)
    logger.info("Total XP calculated: %d", total_xp)
    return total_xp