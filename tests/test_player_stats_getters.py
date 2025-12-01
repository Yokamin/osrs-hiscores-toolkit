import json
import os
import pytest
from src import player_stats_getters as getters

# --- Test Data ---

@pytest.fixture
def mock_skill_data():
    """Provides a sample skill data dictionary."""
    return {"name": "Attack", "rank": 608632, "level": 93, "xp": 7698321}

@pytest.fixture
def mock_activity_data():
    """Provides a sample activity data dictionary."""
    return {"name": "Clue Scrolls (all)", "rank": 2, "score": 125623}

# --- Tests for Skill Getters ---

def test_get_skill_level(mock_skill_data):
    """Tests the get_skill_level function."""
    assert getters.get_skill_level(mock_skill_data) == 93
    assert getters.get_skill_level({}) is None

def test_get_skill_xp(mock_skill_data):
    """Tests the get_skill_xp function."""
    assert getters.get_skill_xp(mock_skill_data) == 7698321
    assert getters.get_skill_xp({}) is None

def test_get_skill_rank(mock_skill_data):
    """Tests the get_skill_rank function."""
    assert getters.get_skill_rank(mock_skill_data) == 608632
    assert getters.get_skill_rank({}) is None

# --- Tests for Activity Getters ---

def test_get_activity_score(mock_activity_data):
    """Tests the get_activity_score function."""
    assert getters.get_activity_score(mock_activity_data) == 125623
    assert getters.get_activity_score({}) is None

def test_get_activity_rank(mock_activity_data):
    """Tests the get_activity_rank function."""
    assert getters.get_activity_rank(mock_activity_data) == 2
    assert getters.get_activity_rank({}) is None
