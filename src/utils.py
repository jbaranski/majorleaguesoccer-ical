from datetime import datetime, timedelta
from functools import cache

COMPETITION_TRANSLATE = {}

TEAMS_FIX = {
    "Los Angeles Football Club": "Los Angeles FC",
    "CF Montréal": "CF Montreal",
    "St. Louis CITY SC": "St. Louis City SC",
    "Minnesota United FC": "Minnesota United",
    "San Diego Football Club": "San Diego FC",
    "New York City Football Club": "New York City FC",
}

COMPETITION_FILENAME_MAP = {
    "MLS-COM-000035": "worldcup",
    "MLS-COM-000030": "goldcup",
    "MLS-COM-00002Z": "concacafnationsleague",
    "MLS-COM-00002W": "copamerica",
}


def get_competition_filename(competition_id: str) -> str:
    """Return the output filename stem for a competition.

    Args:
        competition_id: The competition ID (e.g. "MLS-COM-000035") to look up.

    Returns:
        A mapped friendly filename stem, or a lowercased, hyphen-stripped version
        of the competition ID as a fallback.
    """
    return COMPETITION_FILENAME_MAP.get(
        competition_id, competition_id.replace("-", "").lower()
    )


@cache
def get_datetime_from_str(input_str: str) -> datetime:
    """Parse an ISO-format datetime string into a datetime object.

    Results are cached so repeated calls with the same string are free.

    Args:
        input_str: An ISO-8601 datetime string (e.g. "2026-03-07T20:00:00").

    Returns:
        The corresponding datetime object.
    """
    return datetime.fromisoformat(input_str)


@cache
def get_end_datetime(start_time: datetime, delta_hours: int) -> datetime:
    """Compute an end datetime by adding a fixed number of hours to a start time.

    Results are cached so repeated calls with the same arguments are free.

    Args:
        start_time: The event start datetime.
        delta_hours: Number of hours to add.

    Returns:
        The computed end datetime.
    """
    return start_time + timedelta(hours=delta_hours)


@cache
def get_competition_txt(input_str: str) -> str:
    """Return a display-friendly competition name.

    Applies the COMPETITION_TRANSLATE mapping (if present) and shortens
    "Major League Soccer" to "MLS". Results are cached.

    Args:
        input_str: A raw competition name or identifier from the API.

    Returns:
        The translated and abbreviated competition name.
    """
    competition = (
        COMPETITION_TRANSLATE[input_str]
        if input_str in COMPETITION_TRANSLATE
        else input_str
    )
    competition = competition.replace("Major League Soccer", "MLS")
    return competition


@cache
def get_correct_team_name(input_team_name: str) -> str:
    """Return the canonical team name, applying any known corrections.

    Some teams have names in the API that differ from the preferred display name
    (e.g. "Los Angeles Football Club" → "Los Angeles FC"). Falls back to
    ``"???"`` when the input is empty. Results are cached.

    Args:
        input_team_name: The raw team name from the API.

    Returns:
        The corrected team name, or "???" if the name is empty.
    """
    correct_name = (
        TEAMS_FIX[input_team_name]
        if input_team_name in TEAMS_FIX
        else (input_team_name or "")
    )
    return correct_name or "???"


@cache
def get_correct_venue_name(name: str | None, city: str | None) -> str | None:
    """Build a formatted venue string from name and city components.

    Returns ``"name, city"`` when both are available, just the name or city
    when only one is present, and ``"???"`` when neither is provided.
    Results are cached.

    Args:
        name: The venue name, or None if unknown.
        city: The venue city, or None if unknown.

    Returns:
        A formatted venue string, or "???" if both inputs are absent.
    """
    if city and name:
        return f"{name}, {city}"
    if name and not city:
        return name
    if city and not name:
        return city
    return "???"
