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

# --- Tests for Status Checks ---

def test_is_maxed_total():
    """Tests the is_maxed_total function."""
    # Test a non-maxed player
    assert player_stats.is_maxed_total(mock_player_data) is False

    # Test a maxed player (manually create mock data)
    maxed_skills = [
        {"name": "Overall", "level": 2376},
        # ... other skills could be here but are not needed for this test
    ]
    maxed_player = {"skills": maxed_skills}
    assert player_stats.is_maxed_total(maxed_player) is True
    
    # Test a player just under max
    almost_maxed_player = {"skills": [{"name": "Overall", "level": 2375}]}
    assert player_stats.is_maxed_total(almost_maxed_player) is False

def test_is_maxed_combat():
    """Tests the is_maxed_combat function."""
    # Test a non-maxed player
    assert player_stats.is_maxed_combat(mock_player_data) is False

    # Test a maxed combat player
    maxed_combat_skills = [
        {'name': 'Attack', 'level': 99},
        {'name': 'Strength', 'level': 99},
        {'name': 'Defence', 'level': 99},
        {'name': 'Hitpoints', 'level': 99},
        {'name': 'Ranged', 'level': 99},
        {'name': 'Prayer', 'level': 99},
        {'name': 'Magic', 'level': 99},
    ]
    maxed_player = {"skills": maxed_combat_skills}
    assert player_stats.is_maxed_combat(maxed_player) is True

    # Test a player with one combat skill not maxed
    one_skill_short = maxed_combat_skills[:-1] + [{'name': 'Magic', 'level': 98}]
    almost_maxed_player = {"skills": one_skill_short}
    assert player_stats.is_maxed_combat(almost_maxed_player) is False

    # Test a player missing a combat skill
    missing_skill_player = {"skills": maxed_combat_skills[:-1]}
    assert player_stats.is_maxed_combat(missing_skill_player) is False

# --- Tests for Complex Calculators ---

def test_calculate_combat_level():
    """Tests the calculate_combat_level function with various player builds."""
    for variant in combat_level_variants:
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

# --- Tests for XP-based Calculators ---

@pytest.mark.parametrize("xp, expected_level", [
    (0, 1), (82, 1), (83, 2), (13034430, 98), (13034431, 99),
    (14000000, 99), (188884739, 125), (188884740, 126), (200000000, 126)
])
def test_get_level_for_xp(xp, expected_level):
    """Tests get_level_for_xp with various XP values."""
    assert player_stats.get_level_for_xp(xp) == expected_level

@pytest.mark.parametrize("current_xp, xp_needed", [
    (0, 83), (500, 12), (13034430, 1),
    (12000000, 1034431), (180000000, 8884740)
])
def test_get_xp_for_next_level(current_xp, xp_needed):
    """Tests get_xp_for_next_level with various current XP values."""
    assert player_stats.get_xp_for_next_level(current_xp) == xp_needed

def test_get_xp_for_next_level_at_max():
    """Tests get_xp_for_next_level at the maximum level."""
    assert player_stats.get_xp_for_next_level(188884740) is None
    assert player_stats.get_xp_for_next_level(200000000) is None

@pytest.mark.parametrize("current_xp, target_level, xp_needed", [
    (0, 50, 101333),
    (1000000, 99, 12034431),
    (14000000, 99, 0), # Already past target
    (100000, 90, 5246332),
])
def test_get_xp_to_level(current_xp, target_level, xp_needed):
    """Tests the get_xp_to_level function."""
    assert player_stats.get_xp_to_level(current_xp, target_level) == xp_needed

def test_get_xp_to_level_invalid_target():
    """Tests get_xp_to_level with invalid target levels."""
    assert player_stats.get_xp_to_level(100, 1) is None # Target too low
    assert player_stats.get_xp_to_level(100, 127) is None # Target too high
    assert player_stats.get_xp_to_level(100, 0) is None # Target invalid

# --- Tests for XP Aggregators ---

def test_calculate_total_combat_xp():
    """Tests calculate_total_combat_xp with various player data."""
    expected_total_xp = (7698321 + 3640585 + 10477001 + 9482722 + 6027678 + 1476073 + 1928021)
    assert player_stats.calculate_total_combat_xp(mock_player_data) == expected_total_xp

def test_calculate_total_non_combat_xp():
    """Tests calculate_total_non_combat_xp with various player data."""
    expected_total_xp = (
        2393815 + 3020755 + 746053 + 1843083 + 2034713 + 5976802 + 1433327 +
        770020 + 737929 + 1434537 + 5942281 + 5528984 + 1921727 + 7517550 +
        2330781 + 2482747 + 0
    )
    assert player_stats.calculate_total_non_combat_xp(mock_player_data) == expected_total_xp

def test_calculate_total_gathering_xp():
    """Tests calculate_total_gathering_xp with various player data."""
    expected_total_xp = (2393815 + 3020755 + 746053 + 1843083 + 2034713)
    assert player_stats.calculate_total_gathering_xp(mock_player_data) == expected_total_xp

def test_calculate_total_production_xp():
    """Tests calculate_total_production_xp with various player data."""
    expected_total_xp = (5976802 + 1433327 + 770020 + 737929 + 1434537 + 5942281)
    assert player_stats.calculate_total_production_xp(mock_player_data) == expected_total_xp

def test_calculate_total_utility_xp():
    """Tests calculate_total_utility_xp with various player data."""
    expected_total_xp = (5528984 + 1921727 + 7517550 + 2330781 + 2482747 + 0)
    assert player_stats.calculate_total_utility_xp(mock_player_data) == expected_total_xp