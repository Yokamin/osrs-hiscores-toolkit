import pytest
import json
import os
import logging
from unittest.mock import mock_open, patch

from src import osrs_data

# Mock the logger to capture messages
@pytest.fixture(autouse=True)
def caplog_fixture(caplog):
    caplog.set_level(logging.INFO)
    return caplog

# --- Tests for get_xp_table ---

@patch('src.osrs_data.os.path.join', return_value='mock/path/xp_table.json')
@patch('builtins.open', new_callable=mock_open, read_data=json.dumps([0, 83, 174]))
def test_get_xp_table_loads_successfully(mock_open_func, mock_join_func, caplog_fixture):
    """Tests that the XP table loads successfully and is cached."""
    # Clear cache for this test
    osrs_data._xp_table = None
    
    xp_table = osrs_data.get_xp_table()
    assert xp_table == [0, 83, 174]
    mock_join_func.assert_any_call('data', 'xp_table.json')
    mock_open_func.assert_called_once_with('mock/path/xp_table.json', 'r')
    assert "XP table loaded successfully" in caplog_fixture.text

    # Test caching: call again, open should not be called
    mock_open_func.reset_mock()
    xp_table_cached = osrs_data.get_xp_table()
    assert xp_table_cached == [0, 83, 174]
    mock_open_func.assert_not_called()

@patch('src.osrs_data.os.path.join', return_value='mock/path/xp_table.json')
@patch('builtins.open', side_effect=FileNotFoundError)
def test_get_xp_table_file_not_found(mock_open_func, mock_join_func, caplog_fixture):
    """Tests handling of FileNotFoundError when loading XP table."""
    # Clear cache for this test
    osrs_data._xp_table = None
    
    xp_table = osrs_data.get_xp_table()
    assert xp_table == []
    assert "XP table file not found" in caplog_fixture.text
    assert caplog_fixture.records[0].levelname == 'ERROR'

@patch('src.osrs_data.os.path.join', return_value='mock/path/xp_table.json')
@patch('builtins.open', new_callable=mock_open, read_data='invalid json')
@patch('json.load', side_effect=json.JSONDecodeError("Expecting value", "", 0))
def test_get_xp_table_json_decode_error(mock_json_load, mock_open_func, mock_join_func, caplog_fixture):
    """Tests handling of JSONDecodeError when loading XP table."""
    # Clear cache for this test
    osrs_data._xp_table = None
    
    xp_table = osrs_data.get_xp_table()
    assert xp_table == []
    assert "Failed to decode XP table JSON" in caplog_fixture.text
    assert caplog_fixture.records[0].levelname == 'ERROR'

# --- Tests for Skill Grouping Constants ---

def test_skill_constants_exist_and_are_lists():
    """Tests that skill grouping constants exist and are non-empty lists."""
    assert isinstance(osrs_data.COMBAT_SKILLS, list) and len(osrs_data.COMBAT_SKILLS) > 0
    assert isinstance(osrs_data.NON_COMBAT_SKILLS, list) and len(osrs_data.NON_COMBAT_SKILLS) > 0
    assert isinstance(osrs_data.GATHERING_SKILLS, list) and len(osrs_data.GATHERING_SKILLS) > 0
    assert isinstance(osrs_data.PRODUCTION_SKILLS, list) and len(osrs_data.PRODUCTION_SKILLS) > 0
    assert isinstance(osrs_data.UTILITY_SKILLS, list) and len(osrs_data.UTILITY_SKILLS) > 0

# --- Tests for General OSRS Game Constants ---

def test_general_constants_exist_and_are_correct():
    """Tests that general OSRS game constants exist and have correct types."""
    assert isinstance(osrs_data.MAX_TOTAL_LEVEL, int) and osrs_data.MAX_TOTAL_LEVEL > 0
    assert isinstance(osrs_data.MAX_SKILL_LEVEL, int) and osrs_data.MAX_SKILL_LEVEL > 0
    assert isinstance(osrs_data.MAX_XP, int) and osrs_data.MAX_XP > 0
    assert isinstance(osrs_data.MAX_VIRTUAL_LEVEL, int) and osrs_data.MAX_VIRTUAL_LEVEL > 0