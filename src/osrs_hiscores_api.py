import requests
import logging

logger = logging.getLogger(__name__)

# --- Endpoint definitions
BASE_URLS = {
    "normal":        "https://secure.runescape.com/m=hiscore_oldschool",
    "ironman":       "https://secure.runescape.com/m=hiscore_oldschool_ironman",
    "hardcore":      "https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman",
    "ultimate":      "https://secure.runescape.com/m=hiscore_oldschool_ultimate",
    "deadman":       "https://secure.runescape.com/m=hiscore_oldschool_deadman",
    "seasonal":      "https://secure.runescape.com/m=hiscore_oldschool_seasonal",
    "tournament":    "https://secure.runescape.com/m=hiscore_oldschool_tournament",
    "fresh_start":   "https://secure.runescape.com/m=hiscore_oldschool_fresh_start",
}

# --- Exceptions
class HiscoreError(Exception):
    """Base exception for OSRS Hiscores API errors."""
    pass

class HiscoreHTTPError(HiscoreError):
    """HTTP or connection error."""
    pass

class HiscoreModeError(HiscoreError):
    """Invalid hiscore mode specified."""
    pass

class HiscoreFormatError(HiscoreError):
    """Invalid format specified (must be 'json' or 'csv')."""
    pass

# --- Helper: build URL
def build_url(player: str, mode: str = "normal", format: str = "json") -> str:
    """Constructs the OSRS Hiscores API URL for a given player and mode.

    Args:
        player: The OSRS player name.
        mode: The hiscore game mode (e.g., "normal", "ironman"). 
              Defaults to "normal".
        format: The desired data format ("json" or "csv"). 
                Defaults to "json".

    Returns:
        The full URL to fetch player hiscores.

    Raises:
        HiscoreModeError: If an invalid game mode is specified.
        HiscoreFormatError: If an invalid format is specified.
    """
    if mode not in BASE_URLS:
        logger.error("Invalid mode '%s'. Valid modes: %s", mode, list(BASE_URLS.keys()))
        raise HiscoreModeError(f"Invalid mode '{mode}'. Valid modes: {list(BASE_URLS.keys())}")

    if format not in ("json", "csv"):
        logger.error("Invalid format '%s'. Format must be 'json' or 'csv'", format)
        raise HiscoreFormatError("Format must be 'json' or 'csv'")

    endpoint = BASE_URLS[mode]
    ext = "json" if format == "json" else "ws"
    url = f"{endpoint}/index_lite.{ext}?player={player}"
    logger.debug("Built URL: %s", url)
    return url

# --- Main function: fetch data
def fetch_hiscore(
    player: str,
    mode: str = "normal",
    format: str = "json",
    timeout: float = 5.0
) -> dict | str:
    """Fetches hiscore data for a player from the OSRS API.

    Args:
        player: The OSRS player name.
        mode: The hiscore game mode (e.g., "normal", "ironman"). 
              Defaults to "normal".
        format: The desired data format ("json" or "csv"). 
                Defaults to "json".
        timeout: The request timeout in seconds. Defaults to 5.0.

    Returns:
        A dictionary if the format is "json" and the request is successful,
        otherwise a string (for "csv" format).

    Raises:
        HiscoreHTTPError: For HTTP status or connection-related errors.
    """
    logger.info("Attempting to fetch hiscores for player '%s' in '%s' mode (format: %s).", player, mode, format)
    url = build_url(player, mode, format)

    try:
        response = requests.get(url, timeout=timeout)
        logger.debug("HTTP request to %s completed with status %s.", url, response.status_code)
    except requests.RequestException as e:
        logger.error("HTTP request failed for URL %s: %s", url, e)
        raise HiscoreHTTPError(f"HTTP request failed: {e}") from e

    if not response.ok:
        logger.error("HTTP request to %s returned non-OK status %s.", url, response.status_code)
        raise HiscoreHTTPError(f"HTTP request returned status {response.status_code}")

    if format == "json":
        try:
            data = response.json()
            logger.debug("Successfully parsed JSON response.")
            return data
        except ValueError as e:
            logger.error("Failed to parse JSON response from URL %s: %s", url, e)
            raise HiscoreHTTPError(f"Failed to parse JSON response: {e}") from e
    else:
        logger.debug("Returning raw text response.")
        return response.text