from typing import List, Dict, Optional

def _find_item_by_name(items_list: List[Dict], item_name: str) -> Optional[Dict]:
    """
    Helper function to find an item (skill, activity, or boss) by its 'name'
    within a list of dictionaries.

    Args:
        items_list (List[Dict]): A list of dictionaries, typically skills or activities.
        item_name (str): The name of the item to retrieve (e.g., "Sailing", "Zulrah").

    Returns:
        Optional[Dict]: A dictionary containing the item's data or None if not found.
    """
    for item in items_list:
        if item.get('name') == item_name:
            return item
    return None

def get_skill_data(player_data: Dict, skill_name: str) -> Optional[Dict]:
    """
    Retrieves the full data dictionary for a specific skill from a player's
    raw data.

    Args:
        player_data (Dict): The raw player data dictionary from the OSRS API.
        skill_name (str): The name of the skill to retrieve (e.g., "Sailing", "Attack").

    Returns:
        Optional[Dict]: A dictionary containing the skill's data (id, name, rank, level, xp)
                        or None if the skill is not found.
    """
    skills = player_data.get('skills', [])
    return _find_item_by_name(skills, skill_name)

def get_activity_data(player_data: Dict, activity_name: str) -> Optional[Dict]:
    """
    Retrieves the full data dictionary for a specific activity or boss from
    a player's raw data.

    Args:
        player_data (Dict): The raw player data dictionary from the OSRS API.
        activity_name (str): The name of the activity or boss to retrieve
                             (e.g., "Clue Scrolls (all)", "Zulrah").

    Returns:
        Optional[Dict]: A dictionary containing the activity/boss's data (id, name, rank, score)
                        or None if the activity/boss is not found.
    """
    activities = player_data.get('activities', [])
    return _find_item_by_name(activities, activity_name)