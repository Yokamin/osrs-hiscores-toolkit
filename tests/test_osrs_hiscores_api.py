import pytest
import requests
from osrs_hiscores_api import build_url, fetch_hiscore, HiscoreModeError, HiscoreFormatError, HiscoreHTTPError
import logging

# Set up a test logger (optional, but good for seeing logs during test runs)
# Test loggers usually capture output, not write to files, but for manual inspection it's okay
test_logger = logging.getLogger(__name__)
test_logger.setLevel(logging.DEBUG) # Ensure all levels are captured by the test environment

# --- Tests for build_url ---

def test_build_url_default():
    """Tests build_url with default parameters."""
    expected = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.json?player=Zezima"
    assert build_url("Zezima") == expected

def test_build_url_ironman_csv():
    """Tests build_url with non-default parameters (ironman, csv)."""
    expected = "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?player=Iron_Man"
    assert build_url("Iron_Man", mode="ironman", format="csv") == expected

def test_build_url_invalid_mode():
    """Tests that build_url raises HiscoreModeError for an invalid mode."""
    with pytest.raises(HiscoreModeError):
        build_url("Test", mode="invalid_mode")

def test_build_url_invalid_format():
    """Tests that build_url raises HiscoreFormatError for an invalid format."""
    with pytest.raises(HiscoreFormatError):
        build_url("Test", format="xml")

# --- Tests for fetch_hiscore ---

def test_fetch_hiscore_success_json(monkeypatch):
    """Tests a successful fetch_hiscore call returning JSON."""
    fake_data = {"name": "TestUser", "skills": [{"name": "Attack", "level": 99}]}
    
    class MockResponse:
        ok = True
        status_code = 200
        def json(self):
            return fake_data

    def mock_get(*args, **kwargs):
        test_logger.debug("Mocking requests.get for JSON success.")
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    
    result = fetch_hiscore("TestUser", format="json")
    assert result == fake_data

def test_fetch_hiscore_success_csv(monkeypatch):
    """Tests a successful fetch_hiscore call returning CSV."""
    fake_data = "280,1466,27957906\n"
    
    class MockResponse:
        ok = True
        status_code = 200
        text = fake_data

    def mock_get(*args, **kwargs):
        test_logger.debug("Mocking requests.get for CSV success.")
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    
    result = fetch_hiscore("TestUser", format="csv")
    assert result == fake_data

def test_fetch_hiscore_http_error(monkeypatch):
    """Tests that fetch_hiscore raises HiscoreHTTPError on a request exception."""
    def mock_get_raises(*args, **kwargs):
        test_logger.debug("Mocking requests.get to raise RequestException.")
        raise requests.RequestException("Test network error")

    monkeypatch.setattr(requests, "get", mock_get_raises)
    
    with pytest.raises(HiscoreHTTPError, match="Test network error"):
        fetch_hiscore("TestUser")

def test_fetch_hiscore_bad_status_code(monkeypatch):
    """Tests that fetch_hiscore raises HiscoreHTTPError on a bad status code."""
    class MockResponse:
        ok = False
        status_code = 404

    def mock_get(*args, **kwargs):
        test_logger.debug("Mocking requests.get for bad status code (404).")
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    
    with pytest.raises(HiscoreHTTPError, match="status 404"):
        fetch_hiscore("TestUser")

def test_fetch_hiscore_bad_json(monkeypatch):
    """Tests that fetch_hiscore raises HiscoreHTTPError on invalid JSON."""
    class MockResponse:
        ok = True
        status_code = 200
        def json(self):
            test_logger.debug("Mocking requests.get to raise ValueError for bad JSON.")
            raise ValueError("Failed to decode JSON")

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    
    with pytest.raises(HiscoreHTTPError, match="Failed to parse JSON"):
        fetch_hiscore("TestUser", format="json")