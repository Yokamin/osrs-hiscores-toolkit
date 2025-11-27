import requests

# -----------------------------
# Endpoint definitions
# -----------------------------
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

# -----------------------------
# Exceptions
# -----------------------------
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

# -----------------------------
# Helper: build URL
# -----------------------------
def build_url(player: str, mode: str = "normal", format: str = "json") -> str:
    if mode not in BASE_URLS:
        raise HiscoreModeError(f"Invalid mode '{mode}'. Valid modes: {list(BASE_URLS.keys())}")

    if format not in ("json", "csv"):
        raise HiscoreFormatError("Format must be 'json' or 'csv'")

    endpoint = BASE_URLS[mode]
    ext = "json" if format == "json" else "ws"
    return f"{endpoint}/index_lite.{ext}?player={player}"

# -----------------------------
# Main function: fetch data
# -----------------------------
def fetch_hiscore(
    player: str,
    mode: str = "normal",
    format: str = "json",
    timeout: float = 5.0
) -> dict | str:
    url = build_url(player, mode, format)

    try:
        response = requests.get(url, timeout=timeout)
    except requests.RequestException as e:
        raise HiscoreHTTPError(f"HTTP request failed: {e}") from e

    if not response.ok:
        raise HiscoreHTTPError(f"HTTP request returned status {response.status_code}")

    if format == "json":
        try:
            return response.json()
        except ValueError as e:
            raise HiscoreHTTPError(f"Failed to parse JSON response: {e}") from e
    else:
        # CSV/raw WS text
        return response.text

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # Example of "hey jase"
    player = "hey_jase"
    try:
        data = fetch_hiscore(player, mode="normal", format="json")
        print(data)
    except HiscoreError as e:
        print(f"Error fetching hiscores for {player}: {e}")