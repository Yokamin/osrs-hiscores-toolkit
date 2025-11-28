import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def _find_item_by_name(items_list: List[Dict], item_name: str) -> Optional[Dict]:
    """
    Internal helper to find an item in a list of dictionaries by its 'name'.

    Args:
        items_list (List[Dict]): A list of dictionaries (e.g., skills, activities).
        item_name (str): The name of the item to find.

    Returns:
        Optional[Dict]: The dictionary for the found item, or None.
    """
    logger.debug("Searching list for item: '%s'", item_name)
    for item in items_list:
        if item.get('name') == item_name:
            logger.debug("Found item: '%s'", item_name)
            return item
    logger.debug("Item not found: '%s'", item_name)
    return None

def get_skill_data(player_data: Dict, skill_name: str) -> Optional[Dict]:
    """
    Retrieves the full data dictionary for a specific skill from raw player data.

    Args:
        player_data (Dict): The raw player data from the OSRS API.
        skill_name (str): The name of the skill to retrieve (e.g., "Attack").

    Returns:
        Optional[Dict]: A dictionary containing the skill's data (id, name, 
                        rank, level, xp), or None if not found.
    """
    logger.info("Attempting to get data for skill: '%s'", skill_name)
    skills = player_data.get('skills', [])
    return _find_item_by_name(skills, skill_name)

def get_activity_data(player_data: Dict, activity_name: str) -> Optional[Dict]:
    """
    Retrieves the full data dictionary for an activity/boss from raw player data.

    Args:
        player_data (Dict): The raw player data from the OSRS API.
        activity_name (str): The name of the activity/boss to retrieve 
                             (e.g., "Zulrah").

    Returns:
        Optional[Dict]: A dictionary containing the activity's data (id, name, 
                        rank, score), or None if not found.
    """
    logger.info("Attempting to get data for activity: '%s'", activity_name)
    activities = player_data.get('activities', [])
    return _find_item_by_name(activities, activity_name)
