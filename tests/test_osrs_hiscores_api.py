import pytest
import requests
from src.osrs_hiscores_api import build_url, fetch_hiscore, HiscoreModeError, HiscoreFormatError, HiscoreHTTPError

# --- Fixtures ---

@pytest.fixture
def mock_requests_get(monkeypatch):
    """Fixture to mock requests.get with a configurable response."""
    def _mock_factory(status_code=200, json_data=None, text_data=None, raise_exception=None, json_error=False):
        if raise_exception:
            def mock_get_raises(*args, **kwargs):
                raise raise_exception
            monkeypatch.setattr(requests, "get", mock_get_raises)
            return

        class MockResponse:
            def __init__(self):
                self.ok = status_code == 200
                self.status_code = status_code
                self.text = text_data

            def json(self):
                if json_error:
                    raise ValueError("Failed to decode JSON")
                return json_data

        def mock_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr(requests, "get", mock_get)

    return _mock_factory

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

def test_fetch_hiscore_success_json(mock_requests_get):
    """Tests a successful fetch_hiscore call returning JSON."""
    fake_data = {"name": "TestUser", "skills": [{"name": "Attack", "level": 99}]}
    mock_requests_get(json_data=fake_data)
    
    result = fetch_hiscore("TestUser", format="json")
    assert result == fake_data

def test_fetch_hiscore_success_csv(mock_requests_get):
    """Tests a successful fetch_hiscore call returning CSV."""
    fake_data = "280,1466,27957906\n"
    mock_requests_get(text_data=fake_data)
    
    result = fetch_hiscore("TestUser", format="csv")
    assert result == fake_data

def test_fetch_hiscore_http_error(mock_requests_get):
    """Tests that fetch_hiscore raises HiscoreHTTPError on a request exception."""
    mock_requests_get(raise_exception=requests.RequestException("Test network error"))
    
    with pytest.raises(HiscoreHTTPError, match="Test network error"):
        fetch_hiscore("TestUser")

def test_fetch_hiscore_bad_status_code(mock_requests_get):
    """Tests that fetch_hiscore raises HiscoreHTTPError on a bad status code."""
    mock_requests_get(status_code=404)
    
    with pytest.raises(HiscoreHTTPError, match="status 404"):
        fetch_hiscore("TestUser")

def test_fetch_hiscore_bad_json(mock_requests_get):
    """Tests that fetch_hiscore raises HiscoreHTTPError on invalid JSON."""
    mock_requests_get(json_error=True)
    
    with pytest.raises(HiscoreHTTPError, match="Failed to parse JSON"):
        fetch_hiscore("TestUser", format="json")