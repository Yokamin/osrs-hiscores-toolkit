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
def main():
    """Main function to run the script from the command line."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Fetches player data from the OSRS Hiscores API."
    )
    parser.add_argument("player", help="The OSRS player name to look up.")
    parser.add_argument(
        "--mode",
        default="normal",
        choices=list(BASE_URLS.keys()),
        help="The game mode to query. Defaults to 'normal'."
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "csv"],
        help="The output format. Defaults to 'json'."
    )
    args = parser.parse_args()

    try:
        print(f"Fetching hiscores for '{args.player}' in '{args.mode}' mode...")
        data = fetch_hiscore(args.player, mode=args.mode, format=args.format)
        
        # The 'fetch_hiscore' function returns a raw dictionary for json.
        # Pretty-prints JSON for readability when run as a script.
        if args.format == "json":
            print(json.dumps(data, indent=2))
        else:
            print(data)

    except HiscoreError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()