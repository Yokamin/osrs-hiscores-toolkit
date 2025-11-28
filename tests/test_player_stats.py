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

# --- Tests for XP Aggregators ---

def test_calculate_total_combat_xp():
    """Tests calculate_total_combat_xp with various player data."""
    # Test with mock_player_data (all combat skills ranked)
    # Attack: 7698321, Defence: 3640585, Strength: 10477001, Hitpoints: 9482722
    # Ranged: 6027678, Prayer: 1476073, Magic: 1928021
    expected_total_xp = (
        7698321 + 3640585 + 10477001 + 9482722 + 6027678 + 1476073 + 1928021
    )
    assert player_stats.calculate_total_combat_xp(mock_player_data) == expected_total_xp

    # Test with a player having some unranked combat skills (xp = -1)
    player_data_unranked_combat = {
        'name': 'unranked_combat_player',
        'skills': [
            {'name': 'Attack', 'level': 10, 'xp': 1000, 'rank': 10000},
            {'name': 'Strength', 'level': 1, 'xp': -1, 'rank': -1}, # Unranked strength
            {'name': 'Defence', 'level': 20, 'xp': 5000, 'rank': 5000},
            {'name': 'Hitpoints', 'level': 15, 'xp': 2000, 'rank': 8000},
            {'name': 'Ranged', 'level': 1, 'xp': -1, 'rank': -1}, # Unranked ranged
            {'name': 'Prayer', 'level': 5, 'xp': 500, 'rank': 12000},
            {'name': 'Magic', 'level': 1, 'xp': -1, 'rank': -1}, # Unranked magic
        ],
        'activities': []
    }
    # Expected: 1000 (Atk) + 0 (Str) + 5000 (Def) + 2000 (HP) + 0 (Rng) + 500 (Pray) + 0 (Mag) = 8500
    assert player_stats.calculate_total_combat_xp(player_data_unranked_combat) == 8500

    # Test with player data missing some combat skills
    player_data_missing_skills = {
        'name': 'missing_skills_player',
        'skills': [
            {'name': 'Attack', 'level': 10, 'xp': 1000},
            {'name': 'Defence', 'level': 20, 'xp': 5000},
        ],
        'activities': []
    }
    # Expected: 1000 (Atk) + 0 (Str) + 5000 (Def) + 0 (HP) + 0 (Rng) + 0 (Pray) + 0 (Mag) = 6000
    assert player_stats.calculate_total_combat_xp(player_data_missing_skills) == 6000

    # Test with empty player data
    empty_player_data = {'name': 'empty_player', 'skills': [], 'activities': []}
    assert player_stats.calculate_total_combat_xp(empty_player_data) == 0

def test_calculate_total_non_combat_xp():
    """Tests calculate_total_non_combat_xp with various player data."""
    # Test with mock_player_data (all non-combat skills ranked)
    # Farming: 2393815, Fishing: 3020755, Hunter: 746053, Mining: 1843083, Woodcutting: 2034713
    # Cooking: 5976802, Crafting: 1433327, Fletching: 770020, Herblore: 737929, Runecraft: 1434537
    # Smithing: 5942281, Agility: 5528984, Construction: 1921727, Firemaking: 7517550, Slayer: 2330781
    # Thieving: 2482747, Sailing: 0
    expected_total_xp = (
        2393815 + 3020755 + 746053 + 1843083 + 2034713 +
        5976802 + 1433327 + 770020 + 737929 + 1434537 +
        5942281 + 5528984 + 1921727 + 7517550 + 2330781 +
        2482747 + 0
    )
    assert player_stats.calculate_total_non_combat_xp(mock_player_data) == expected_total_xp

    # Test with a player having some unranked non-combat skills (xp = -1)
    player_data_unranked_non_combat = {
        'name': 'unranked_non_combat_player',
        'skills': [
            {'name': 'Farming', 'level': 10, 'xp': 1000},
            {'name': 'Fishing', 'level': 1, 'xp': -1}, # Unranked
            {'name': 'Hunter', 'level': 5, 'xp': 500},
            {'name': 'Mining', 'level': 1, 'xp': -1}, # Unranked
            {'name': 'Woodcutting', 'level': 20, 'xp': 2000},
            {'name': 'Cooking', 'level': 15, 'xp': 1500},
            {'name': 'Crafting', 'level': 1, 'xp': -1}, # Unranked
            {'name': 'Fletching', 'level': 5, 'xp': 500},
            {'name': 'Herblore', 'level': 10, 'xp': 1000},
            {'name': 'Runecraft', 'level': 1, 'xp': -1}, # Unranked
            {'name': 'Smithing', 'level': 20, 'xp': 2000},
            {'name': 'Agility', 'level': 15, 'xp': 1500},
            {'name': 'Construction', 'level': 1, 'xp': -1}, # Unranked
            {'name': 'Firemaking', 'level': 5, 'xp': 500},
            {'name': 'Slayer', 'level': 10, 'xp': 1000},
            {'name': 'Thieving', 'level': 1, 'xp': -1}, # Unranked
            {'name': 'Sailing', 'level': 1, 'xp': 0},
        ],
        'activities': []
    }
    expected_xp = (
        1000 + 0 + 500 + 0 + 2000 +
        1500 + 0 + 500 + 1000 + 0 +
        2000 + 1500 + 0 + 500 + 1000 +
        0 + 0
    )
    assert player_stats.calculate_total_non_combat_xp(player_data_unranked_non_combat) == expected_xp

    # Test with player data missing some non-combat skills
    player_data_missing_non_combat = {
        'name': 'missing_non_combat_player',
        'skills': [
            {'name': 'Farming', 'level': 10, 'xp': 1000},
            {'name': 'Woodcutting', 'level': 20, 'xp': 2000},
            {'name': 'Cooking', 'level': 15, 'xp': 1500},
            {'name': 'Firemaking', 'level': 5, 'xp': 500},
        ],
        'activities': []
    }
    expected_xp = 1000 + 2000 + 1500 + 500 # Only existing skills contribute
    assert player_stats.calculate_total_non_combat_xp(player_data_missing_non_combat) == expected_xp

    # Test with empty player data
    empty_player_data = {'name': 'empty_player', 'skills': [], 'activities': []}
    assert player_stats.calculate_total_non_combat_xp(empty_player_data) == 0

def test_calculate_total_gathering_xp():
    """Tests calculate_total_gathering_xp with various player data."""
    # Test with mock_player_data (all gathering skills ranked)
    # Farming: 2393815, Fishing: 3020755, Hunter: 746053, Mining: 1843083, Woodcutting: 2034713
    expected_total_xp = (
        2393815 + 3020755 + 746053 + 1843083 + 2034713
    )
    assert player_stats.calculate_total_gathering_xp(mock_player_data) == expected_total_xp

    # Test with some unranked gathering skills
    player_data_unranked_gathering = {
        'name': 'unranked_gathering_player',
        'skills': [
            {'name': 'Farming', 'level': 10, 'xp': 1000},
            {'name': 'Fishing', 'level': 1, 'xp': -1}, # Unranked
            {'name': 'Hunter', 'level': 5, 'xp': 500},
            {'name': 'Mining', 'level': 1, 'xp': -1}, # Unranked
            {'name': 'Woodcutting', 'level': 20, 'xp': 2000},
        ],
        'activities': []
    }
    expected_xp = 1000 + 0 + 500 + 0 + 2000
    assert player_stats.calculate_total_gathering_xp(player_data_unranked_gathering) == expected_xp

    # Test with missing gathering skills
    player_data_missing_gathering = {
        'name': 'missing_gathering_player',
        'skills': [
            {'name': 'Farming', 'level': 10, 'xp': 1000},
            {'name': 'Woodcutting', 'level': 20, 'xp': 2000},
        ],
        'activities': []
    }
    expected_xp = 1000 + 2000
    assert player_stats.calculate_total_gathering_xp(player_data_missing_gathering) == expected_xp

    # Test with empty player data
    empty_player_data = {'name': 'empty_player', 'skills': [], 'activities': []}
    assert player_stats.calculate_total_gathering_xp(empty_player_data) == 0

def test_calculate_total_production_xp():
    """Tests calculate_total_production_xp with various player data."""
    # Production skills: Cooking, Crafting, Fletching, Herblore, Runecraft, Smithing
    # Test with mock_player_data (all production skills ranked)
    expected_total_xp = (
        player_stats.get_skill_xp(mock_player_data, "Cooking") +
        player_stats.get_skill_xp(mock_player_data, "Crafting") +
        player_stats.get_skill_xp(mock_player_data, "Fletching") +
        player_stats.get_skill_xp(mock_player_data, "Herblore") +
        player_stats.get_skill_xp(mock_player_data, "Runecraft") +
        player_stats.get_skill_xp(mock_player_data, "Smithing")
    )
    assert player_stats.calculate_total_production_xp(mock_player_data) == expected_total_xp

    # Test with some unranked production skills
    player_data_unranked = {
        'name': 'unranked_production_player',
        'skills': [
            {'name': 'Cooking', 'xp': 100},
            {'name': 'Crafting', 'xp': -1},
            {'name': 'Fletching', 'xp': 200},
            {'name': 'Herblore', 'xp': -1},
            {'name': 'Runecraft', 'xp': 300},
            {'name': 'Smithing', 'xp': 400},
        ],
        'activities': []
    }
    expected_xp = 100 + 0 + 200 + 0 + 300 + 400
    assert player_stats.calculate_total_production_xp(player_data_unranked) == expected_xp

    # Test with missing production skills
    player_data_missing = {
        'name': 'missing_production_player',
        'skills': [
            {'name': 'Cooking', 'xp': 100},
            {'name': 'Herblore', 'xp': 200},
        ],
        'activities': []
    }
    expected_xp = 100 + 200
    assert player_stats.calculate_total_production_xp(player_data_missing) == expected_xp

    # Test with empty player data
    empty_player_data = {'name': 'empty_player', 'skills': [], 'activities': []}
    assert player_stats.calculate_total_production_xp(empty_player_data) == 0

def test_calculate_total_utility_xp():
    """Tests calculate_total_utility_xp with various player data."""
    # Utility skills: Agility, Construction, Firemaking, Slayer, Thieving, Sailing
    # Test with mock_player_data (all utility skills ranked)
    expected_total_xp = (
        player_stats.get_skill_xp(mock_player_data, "Agility") +
        player_stats.get_skill_xp(mock_player_data, "Construction") +
        player_stats.get_skill_xp(mock_player_data, "Firemaking") +
        player_stats.get_skill_xp(mock_player_data, "Slayer") +
        player_stats.get_skill_xp(mock_player_data, "Thieving") +
        player_stats.get_skill_xp(mock_player_data, "Sailing")
    )
    assert player_stats.calculate_total_utility_xp(mock_player_data) == expected_total_xp

    # Test with some unranked utility skills
    player_data_unranked = {
        'name': 'unranked_utility_player',
        'skills': [
            {'name': 'Agility', 'xp': 100},
            {'name': 'Construction', 'xp': -1},
            {'name': 'Firemaking', 'xp': 200},
            {'name': 'Slayer', 'xp': -1},
            {'name': 'Thieving', 'xp': 300},
            {'name': 'Sailing', 'xp': 0},
        ],
        'activities': []
    }
    expected_xp = 100 + 0 + 200 + 0 + 300 + 0
    assert player_stats.calculate_total_utility_xp(player_data_unranked) == expected_xp

    # Test with missing utility skills
    player_data_missing = {
        'name': 'missing_utility_player',
        'skills': [
            {'name': 'Agility', 'xp': 100},
            {'name': 'Slayer', 'xp': 200},
        ],
        'activities': []
    }
    expected_xp = 100 + 200
    assert player_stats.calculate_total_utility_xp(player_data_missing) == expected_xp

    # Test with empty player data
    empty_player_data = {'name': 'empty_player', 'skills': [], 'activities': []}
    assert player_stats.calculate_total_utility_xp(empty_player_data) == 0
