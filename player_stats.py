from typing import Dict, Optional
import math
import hiscores_parser

# --- Tier 1: Simple Getters ---

def get_skill_level(player_data: Dict, skill_name: str) -> Optional[int]:
    """
    Retrieves the level for a specific skill from player data.
    
    Args:
        player_data: The raw player data dictionary from the API.
        skill_name: The name of the skill.

    Returns:
        The skill level as an integer, or None if not found.
    """
    skill_data = hiscores_parser.get_skill_data(player_data, skill_name)
    if skill_data and 'level' in skill_data:
        # The API returns level as a string, so we convert it
        return int(skill_data['level'])
    return None

def get_skill_xp(player_data: Dict, skill_name: str) -> Optional[int]:
    """
    Retrieves the experience points for a specific skill from player data.
    
    Args:
        player_data: The raw player data dictionary from the API.
        skill_name: The name of the skill.
        
    Returns:
        The skill XP as an integer (can be -1 for unranked), or None if not found.
    """
    skill_data = hiscores_parser.get_skill_data(player_data, skill_name)
    if skill_data and 'xp' in skill_data:
        # API returns XP as a string, so we convert it
        return int(skill_data['xp'])
    return None

def get_skill_rank(player_data: Dict, skill_name: str) -> Optional[int]:
    """
    Retrieves the rank for a specific skill from player data.
    
    Args:
        player_data: The raw player data dictionary from the API.
        skill_name: The name of the skill.
        
    Returns:
        The skill rank as an integer (can be -1 for unranked), or None if not found.
    """
    skill_data = hiscores_parser.get_skill_data(player_data, skill_name)
    if skill_data and 'rank' in skill_data:
        return int(skill_data['rank'])
    return None

def get_overall_rank(player_data: Dict) -> Optional[int]:
    """
    Retrieves the overall rank of the player.
    
    Args:
        player_data: The raw player data dictionary from the API.
        
    Returns:
        The overall rank as an integer (can be -1 for unranked), or None if not found.
    """
    overall_data = hiscores_parser.get_skill_data(player_data, "Overall")
    if overall_data and 'rank' in overall_data:
        return int(overall_data['rank'])
    return None

def get_total_level(player_data: Dict) -> Optional[int]:
    """
    Retrieves the total level of the player.
    
    Args:
        player_data: The raw player data dictionary from the API.
        
    Returns:
        The total level as an integer, or None if not found.
    """
    overall_data = hiscores_parser.get_skill_data(player_data, "Overall")
    if overall_data and 'level' in overall_data:
        return int(overall_data['level'])
    return None

def get_overall_xp(player_data: Dict) -> Optional[int]:
    """
    Retrieves the overall experience points of the player.
    
    Args:
        player_data: The raw player data dictionary from the API.
        
    Returns:
        The overall XP as an integer (can be -1 for unranked), or None if not found.
    """
    overall_data = hiscores_parser.get_skill_data(player_data, "Overall")
    if overall_data and 'xp' in overall_data:
        return int(overall_data['xp'])
    return None

def get_activity_score(player_data: Dict, activity_name: str) -> Optional[int]:
    """
    Retrieves the score for a specific activity from player data.
    
    Args:
        player_data: The raw player data dictionary from the API.
        activity_name: The name of the activity.
        
    Returns:
        The activity score as an integer (can be -1 for unranked), or None if not found.
    """
    activity_data = hiscores_parser.get_activity_data(player_data, activity_name)
    if activity_data and 'score' in activity_data:
        return int(activity_data['score'])
    return None

def get_activity_rank(player_data: Dict, activity_name: str) -> Optional[int]:
    """
    Retrieves the rank for a specific activity from player data.
    
    Args:
        player_data: The raw player data dictionary from the API.
        activity_name: The name of the activity.
        
    Returns:
        The activity rank as an integer (can be -1 for unranked), or None if not found.
    """
    activity_data = hiscores_parser.get_activity_data(player_data, activity_name)
    if activity_data and 'rank' in activity_data:
        return int(activity_data['rank'])
    return None

# --- Tier 3: Complex Calculators (to be implemented) ---

def calculate_combat_level(player_data: Dict) -> Optional[float]:
    """
    Calculates the player's exact combat level based on the OSRS Wiki formula.
    Returns None if any required skill level is missing.
    """
    # Required skills for combat level calculation
    required_skills = [
        "Attack", "Strength", "Defence", "Hitpoints", "Ranged", "Prayer", "Magic"
    ]

    # Retrieve all required skill levels
    levels = {}
    for skill in required_skills:
        level = get_skill_level(player_data, skill)
        if level is None:
            # If any required skill level is missing, we cannot calculate combat level
            return None
        levels[skill] = level
    
    attack = levels["Attack"]
    strength = levels["Strength"]
    defence = levels["Defence"]
    hitpoints = levels["Hitpoints"]
    ranged = levels["Ranged"]
    prayer = levels["Prayer"]
    magic = levels["Magic"]

    # Calculate base contribution
    base = 0.25 * (defence + hitpoints + math.floor(prayer * 0.5))

    # Calculate attack style contributions
    melee_contribution = 0.325 * (attack + strength)
    range_contribution = 0.325 * math.floor(ranged * 1.5)
    magic_contribution = 0.325 * math.floor(magic * 1.5)

    max_attack_contribution = max(melee_contribution, range_contribution, magic_contribution)

    # Sum contributions for the final combat level, applying floor at the very end
    combat_level = base + max_attack_contribution

    return combat_level
