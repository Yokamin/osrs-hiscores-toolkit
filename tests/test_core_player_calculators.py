import json
import os
from src import core_player_calculators as calc
from src import osrs_data
import math
import pytest
from unittest.mock import patch # Added import for mocking
import logging # Added import for logging

# --- Test Data Loaders ---

def _load_test_data(filename):
    """Helper function to load sample data from the test_data directory."""
    path = os.path.join(os.path.dirname(__file__), "test_data", filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Test Fixtures ---

@pytest.fixture
def mock_player_data():
    """Provides mock player data for tests."""
    return _load_test_data("test_user.json")

@pytest.fixture
def combat_level_variants():
    """Provides different player builds for combat level testing."""
    return _load_test_data("combat_level_variants.json")

# Mock the logger to capture messages
@pytest.fixture(autouse=True)
def caplog_fixture(caplog):
    caplog.set_level(logging.INFO) # Set to INFO to capture error messages
    return caplog

# --- Tests for Status Checks ---

def test_is_maxed_total():
    """Tests the is_maxed_total function."""
    assert calc.is_maxed_total(osrs_data.MAX_TOTAL_LEVEL) is True
    assert calc.is_maxed_total(2375) is False
    assert calc.is_maxed_total(None) is False

def test_is_maxed_combat():
    """Tests the is_maxed_combat function."""
    maxed_levels = {"Attack": 99, "Strength": 99, "Defence": 99, "Hitpoints": 99, "Ranged": 99, "Prayer": 99, "Magic": 99}
    not_maxed_levels = {"Attack": 99, "Strength": 99, "Defence": 99, "Hitpoints": 99, "Ranged": 98, "Prayer": 99, "Magic": 99}
    missing_levels = {"Attack": 99, "Strength": 99}
    
    assert calc.is_maxed_combat(maxed_levels) is True
    assert calc.is_maxed_combat(not_maxed_levels) is False
    assert calc.is_maxed_combat(missing_levels) is False

# --- Tests for Complex Calculators ---

def test_calculate_combat_level(combat_level_variants):
    """Tests the calculate_combat_level function with various player builds."""
    for variant in combat_level_variants:
        # Prepare the levels dict for the pure function
        levels_dict = {skill['name']: skill['level'] for skill in variant['skills']}
        calculated_level = calc.calculate_combat_level(levels_dict)
        expected_level = variant['expected_combat_level']
        assert calculated_level is not None
        assert math.isclose(calculated_level, expected_level, rel_tol=1e-9), \
            f"Failed for {variant['name']}: Expected {expected_level}, Got {calculated_level}"

# --- Tests for XP-based Calculators ---

@pytest.mark.parametrize("xp, expected_level", [
    (0, 1), (82, 1), (83, 2), (13034430, 98), (13034431, 99),
    (14000000, 99), (188884739, 125), (188884740, 126), (osrs_data.MAX_XP, 126)
])
def test_get_level_for_xp(xp, expected_level):
    """Tests get_level_for_xp with various XP values."""
    assert calc.get_level_for_xp(xp) == expected_level

@patch('src.osrs_data.get_xp_table', return_value=[])
def test_get_level_for_xp_xp_table_not_loaded(mock_get_xp_table, caplog_fixture):
    """Tests get_level_for_xp when the XP table is not loaded."""
    assert calc.get_level_for_xp(100) == 1
    assert "XP table not loaded" in caplog_fixture.text
    assert caplog_fixture.records[0].levelname == 'ERROR'

def test_get_level_for_xp_negative_xp():
    """Tests get_level_for_xp with a negative XP value."""
    assert calc.get_level_for_xp(-1) == 1

@pytest.mark.parametrize("level, expected_xp", [
    (1, 0), (2, 83), (99, 13034431), (126, 188884740)
])
def test_get_xp_for_level(level, expected_xp):
    """Tests get_xp_for_level with various level values."""
    assert calc.get_xp_for_level(level) == expected_xp

def test_get_xp_for_level_invalid():
    """Tests get_xp_for_level with invalid levels."""
    assert calc.get_xp_for_level(0) is None
    assert calc.get_xp_for_level(127) is None

@patch('src.osrs_data.get_xp_table', return_value=[])
def test_get_xp_for_level_xp_table_not_loaded(mock_get_xp_table, caplog_fixture):
    """Tests get_xp_for_level when the XP table is not loaded."""
    assert calc.get_xp_for_level(50) is None
    assert "XP table not available" in caplog_fixture.text
    assert caplog_fixture.records[0].levelname == 'ERROR'

@pytest.mark.parametrize("start_xp, target_xp, diff", [
    (0, 100, 100), (1000, 10000, 9000), (1000, 500, -500)
])
def test_calculate_xp_difference(start_xp, target_xp, diff):
    """Tests the calculate_xp_difference function."""
    assert calc.calculate_xp_difference(start_xp, target_xp) == diff

@pytest.mark.parametrize("current_xp, xp_needed", [
    (0, 83), (500, 12), (13034430, 1),
    (12000000, 1034431)
])
def test_get_xp_to_next_level(current_xp, xp_needed):
    """Tests get_xp_for_next_level with various current XP values."""
    assert calc.get_xp_for_next_level(current_xp) == xp_needed

def test_get_xp_to_next_level_at_max():
    """Tests get_xp_for_next_level at the maximum level."""
    assert calc.get_xp_for_next_level(osrs_data.MAX_XP) is None

@patch('src.core_player_calculators.get_xp_for_level', return_value=None)
def test_get_xp_to_next_level_xp_for_level_none(mock_get_xp_for_level, caplog_fixture):
    """Tests get_xp_for_next_level when get_xp_for_level returns None for the next level."""
    assert calc.get_xp_for_next_level(100) is None
    assert "Could not determine XP for next level" in caplog_fixture.text
    assert caplog_fixture.records[1].levelname == 'ERROR'

# --- Tests for XP Aggregators ---

def test_calculate_total_xp():
    """Tests calculate_total_xp with various data."""
    assert calc.calculate_total_xp([100, 200, 300]) == 600
    assert calc.calculate_total_xp([100, 0, 200, -50]) == 300
    assert calc.calculate_total_xp([]) == 0
    # A test with None values
    assert calc.calculate_total_xp([100, None, 200]) == 300