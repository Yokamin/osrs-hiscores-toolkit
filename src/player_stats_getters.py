import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# --- Getters for Skill Data Objects ---

def get_skill_level(skill_data: Dict) -> Optional[int]:
    """
    Extracts the level from a specific skill data dictionary.

    Args:
        skill_data (Dict): A dictionary containing data for a single skill.
                           Expected keys: 'level', 'rank', 'xp', 'name'.

    Returns:
        Optional[int]: The skill's level, or None if not found.

    Example:
        >>> attack_data = {"name": "Attack", "rank": 100, "level": 99, "xp": 13034431}
        >>> get_skill_level(attack_data)
        99
        >>> overall_data = {"name": "Overall", "level": 1911, "rank": 1, "xp": 86845505}
        >>> get_skill_level(overall_data)
        1911
        >>> invalid_data = {"name": "Invalid"}
        >>> get_skill_level(invalid_data) is None
        True
    """
    if 'level' in skill_data:
        return int(skill_data['level'])
    logger.warning("Could not find 'level' in skill data: %s", skill_data)
    return None

def get_skill_xp(skill_data: Dict) -> Optional[int]:
    """
    Extracts the experience from a specific skill data dictionary.

    Args:
        skill_data (Dict): A dictionary containing data for a single skill.
                           Expected keys: 'level', 'rank', 'xp', 'name'.

    Returns:
        Optional[int]: The skill's experience, or None if not found.

    Example:
        >>> attack_data = {"name": "Attack", "rank": 100, "level": 99, "xp": 13034431}
        >>> get_skill_xp(attack_data)
        13034431
        >>> overall_data = {"name": "Overall", "level": 1911, "rank": 1, "xp": 86845505}
        >>> get_skill_xp(overall_data)
        86845505
        >>> invalid_data = {"name": "Invalid"}
        >>> get_skill_xp(invalid_data) is None
        True
    """
    if 'xp' in skill_data:
        return int(skill_data['xp'])
    logger.warning("Could not find 'xp' in skill data: %s", skill_data)
    return None

def get_skill_rank(skill_data: Dict) -> Optional[int]:
    """
    Extracts the rank from a specific skill data dictionary.

    Args:
        skill_data (Dict): A dictionary containing data for a single skill.
                           Expected keys: 'level', 'rank', 'xp', 'name'.

    Returns:
        Optional[int]: The skill's rank, or None if not found.

    Example:
        >>> attack_data = {"name": "Attack", "rank": 100, "level": 99, "xp": 13034431}
        >>> get_skill_rank(attack_data)
        100
        >>> overall_data = {"name": "Overall", "level": 1911, "rank": 1, "xp": 86845505}
        >>> get_skill_rank(overall_data)
        1
        >>> invalid_data = {"name": "Invalid"}
        >>> get_skill_rank(invalid_data) is None
        True
    """
    if 'rank' in skill_data:
        return int(skill_data['rank'])
    logger.warning("Could not find 'rank' in skill data: %s", skill_data)
    return None

# --- Getters for Activity Data Objects ---

def get_activity_score(activity_data: Dict) -> Optional[int]:
    """
    Extracts the score from a specific activity data dictionary.

    Args:
        activity_data (Dict): A dictionary containing data for a single activity.
                              Expected keys: 'rank', 'score', 'name'.

    Returns:
        Optional[int]: The activity's score, or None if not found.

    Example:
        >>> zulrah_data = {"name": "Zulrah", "rank": 500, "score": 2500}
        >>> get_activity_score(zulrah_data)
        2500
        >>> invalid_data = {"name": "Invalid"}
        >>> get_activity_score(invalid_data) is None
        True
    """
    if 'score' in activity_data:
        return int(activity_data['score'])
    logger.warning("Could not find 'score' in activity data: %s", activity_data)
    return None

def get_activity_rank(activity_data: Dict) -> Optional[int]:
    """
    Extracts the rank from a specific activity data dictionary.

    Args:
        activity_data (Dict): A dictionary containing data for a single activity.
                              Expected keys: 'rank', 'score', 'name'.

    Returns:
        Optional[int]: The activity's rank, or None if not found.

    Example:
        >>> zulrah_data = {"name": "Zulrah", "rank": 500, "score": 2500}
        >>> get_activity_rank(zulrah_data)
        500
        >>> invalid_data = {"name": "Invalid"}
        >>> get_activity_rank(invalid_data) is None
        True
    """
    if 'rank' in activity_data:
        return int(activity_data['rank'])
    logger.warning("Could not find 'rank' in activity data: %s", activity_data)
    return None
