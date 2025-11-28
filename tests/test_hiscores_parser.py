import pytest
from hiscores_parser import get_skill_data, get_activity_data
import logging

# Set up a test logger for manual inspection if needed
test_logger = logging.getLogger(__name__)
test_logger.setLevel(logging.DEBUG)

# Mock player data for testing
mock_player_data = {
    "name": "TestPlayer",
    "skills": [
        {"id": 0, "name": "Overall", "rank": 1, "level": 2000, "xp": 1000000000},
        {"id": 1, "name": "Attack", "rank": 100, "level": 99, "xp": 13034431},
        {"id": 2, "name": "Defence", "rank": 200, "level": 90, "xp": 6000000},
        {"id": 3, "name": "Magic", "rank": 50, "level": 95, "xp": 9000000},
    ],
    "activities": [
        {"id": 0, "name": "Clue Scrolls (all)", "rank": 10, "score": 5000},
        {"id": 1, "name": "Zulrah", "rank": 500, "score": 2500},
        {"id": 2, "name": "Vorkath", "rank": 300, "score": 3000},
    ]
}

def test_get_skill_data_found():
    """Tests get_skill_data for an existing skill."""
    skill = get_skill_data(mock_player_data, "Attack")
    assert skill is not None
    assert skill['name'] == "Attack"
    assert skill['level'] == 99

def test_get_skill_data_not_found():
    """Tests get_skill_data for a non-existent skill."""
    skill = get_skill_data(mock_player_data, "Woodcutting")
    assert skill is None

def test_get_skill_data_empty_player_data():
    """Tests get_skill_data with empty player data."""
    empty_data = {"name": "EmptyPlayer", "skills": [], "activities": []}
    skill = get_skill_data(empty_data, "Attack")
    assert skill is None

def test_get_skill_data_no_skills_key():
    """Tests get_skill_data with player data missing 'skills' key."""
    no_skills_data = {"name": "NoSkillsPlayer", "activities": []}
    skill = get_skill_data(no_skills_data, "Attack")
    assert skill is None

def test_get_activity_data_found():
    """Tests get_activity_data for an existing activity."""
    activity = get_activity_data(mock_player_data, "Zulrah")
    assert activity is not None
    assert activity['name'] == "Zulrah"
    assert activity['score'] == 2500

def test_get_activity_data_not_found():
    """Tests get_activity_data for a non-existent activity."""
    activity = get_activity_data(mock_player_data, "The Gauntlet")
    assert activity is None

def test_get_activity_data_empty_player_data():
    """Tests get_activity_data with empty player data."""
    empty_data = {"name": "EmptyPlayer", "skills": [], "activities": []}
    activity = get_activity_data(empty_data, "Zulrah")
    assert activity is None

def test_get_activity_data_no_activities_key():
    """Tests get_activity_data with player data missing 'activities' key."""
    no_activities_data = {"name": "NoActivitiesPlayer", "skills": []}
    activity = get_activity_data(no_activities_data, "Zulrah")
    assert activity is None
