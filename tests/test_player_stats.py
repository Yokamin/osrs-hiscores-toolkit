import json
import os
import player_stats
import math
import pytest

# --- Test Data Loaders ---

def _load_test_data(filename):
    """Helper function to load sample data from the test_data directory."""
    path = os.path.join(os.path.dirname(__file__), "test_data", filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load data once for all tests
mock_player_data = _load_test_data("test_user.json")
combat_level_variants = _load_test_data("combat_level_variants.json")

# --- Tests for Simple Getters ---

def test_get_skill_level():
    """Tests the get_skill_level function."""
    assert player_stats.get_skill_level(mock_player_data, "Attack") == 93
    assert player_stats.get_skill_level(mock_player_data, "Sailing") == 1
    assert player_stats.get_skill_level(mock_player_data, "InvalidSkill") is None

def test_get_skill_xp():
    """Tests the get_skill_xp function."""
    assert player_stats.get_skill_xp(mock_player_data, "Attack") == 7698321
    assert player_stats.get_skill_xp(mock_player_data, "Sailing") == 0
    assert player_stats.get_skill_xp(mock_player_data, "InvalidSkill") is None

def test_get_skill_rank():
    """Tests the get_skill_rank function."""
    assert player_stats.get_skill_rank(mock_player_data, "Attack") == 608632
    assert player_stats.get_skill_rank(mock_player_data, "Sailing") == -1
    assert player_stats.get_skill_rank(mock_player_data, "InvalidSkill") is None

def test_get_overall_stats():
    """Tests the overall getter functions."""
    assert player_stats.get_overall_rank(mock_player_data) == 592599
    assert player_stats.get_total_level(mock_player_data) == 1911
    assert player_stats.get_overall_xp(mock_player_data) == 86845505

def test_get_activity_score():
    """Tests the get_activity_score function."""
    assert player_stats.get_activity_score(mock_player_data, "Clue Scrolls (all)") == 125623
    assert player_stats.get_activity_score(mock_player_data, "Doom of Mokhaiotl") == 0
    assert player_stats.get_activity_score(mock_player_data, "InvalidActivity") is None

def test_get_activity_rank():
    """Tests the get_activity_rank function."""
    assert player_stats.get_activity_rank(mock_player_data, "Clue Scrolls (all)") == 2
    assert player_stats.get_activity_rank(mock_player_data, "Doom of Mokhaiotl") == -1
    assert player_stats.get_activity_rank(mock_player_data, "InvalidActivity") is None

# --- Tests for Complex Calculators ---

def test_calculate_combat_level():
    """Tests the calculate_combat_level function with various player builds."""
    for variant in combat_level_variants:
        # The test data is already in the simplified format needed by the function
        simplified_player_data = {"skills": variant['skills']}
        
        calculated_level = player_stats.calculate_combat_level(simplified_player_data)
        expected_level = variant['expected_combat_level']
        
        assert calculated_level is not None
        assert math.isclose(calculated_level, expected_level, rel_tol=1e-9), \
            f"Failed for {variant['name']}: Expected {expected_level}, Got {calculated_level}"

def test_calculate_combat_level_missing_skills():
    """Tests calculate_combat_level when required skills are missing."""
    player_data_missing = {
        'skills': [{'name': 'Attack', 'level': 99}, {'name': 'Defence', 'level': 99}]
    }
    assert player_stats.calculate_combat_level(player_data_missing) is None

def test_calculate_combat_level_empty_data():
    """Tests calculate_combat_level with empty or malformed data."""
    assert player_stats.calculate_combat_level({"skills": []}) is None
    assert player_stats.calculate_combat_level({}) is None

# --- Tests for XP-based Calculators ---

@pytest.mark.parametrize("xp, expected_level", [
    (0, 1),
    (82, 1),
    (83, 2),
    (13034430, 98),
    (13034431, 99),
    (14000000, 99),
    (188884739, 125),
    (188884740, 126),
    (200000000, 126)
])
def test_get_level_for_xp(xp, expected_level):
    """Tests get_level_for_xp with various XP values."""
    assert player_stats.get_level_for_xp(xp) == expected_level

@pytest.mark.parametrize("current_xp, xp_needed", [
    (0, 83),             # Level 1 -> 2
    (500, 12),             # Level 5 -> 6 (requires 512 xp)
    (13034430, 1),         # 1 xp to level 99
    (12000000, 1034431),   # Level 98 -> 99
    (180000000, 8884740)  # Level 125 -> 126
])
def test_get_xp_for_next_level(current_xp, xp_needed):
    """Tests get_xp_for_next_level with various current XP values."""
    assert player_stats.get_xp_for_next_level(current_xp) == xp_needed

def test_get_xp_for_next_level_at_max():
    """Tests get_xp_for_next_level at the maximum level."""
    assert player_stats.get_xp_for_next_level(188884740) is None # Exactly at 126
    assert player_stats.get_xp_for_next_level(200000000) is None # At 200m cap