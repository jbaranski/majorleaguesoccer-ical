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
    "MLS-COM-000001": "mls",  # Major League Soccer
    "MLS-COM-000002": "mls",  # MLS Cup Playoffs
    "MLS-COM-000005": "mls",  # MLS All-Star Game
    "MLS-COM-000006": "mls",  # Leagues Cup
    "MLS-COM-000007": "mls",  # Campeones Cup
    "MLS-COM-00000K": "mls",  # CONCACAF Champions Cup
    "MLS-COM-00002S": "mls",  # Club Friendly Matches
    "MLS-COM-00002U": "mls",  # U.S. Open Cup
    "MLS-COM-00002V": "mls",  # Canadian Championship
    "MLS-COM-00002W": "copamerica",  # Copa América
    "MLS-COM-00002Y": "fifaclubworldcup",  # FIFA Club World Cup
    "MLS-COM-00002Z": "concacafnationsleague",  # CONCACAF Nations League
    "MLS-COM-000030": "goldcup",  # Gold Cup
    "MLS-COM-000032": "internationalfriendlies",  # International Friendlies
    "MLS-COM-000034": "mls",  # Preseason Friendlies
    "MLS-COM-000035": "worldcup",  # FIFA World Cup
}


COMPETITION_DISPLAY_NAMES: dict[str, str] = {
    "mls": "Major League Soccer",
    "copamerica": "Copa América",
    "fifaclubworldcup": "FIFA Club World Cup",
    "concacafnationsleague": "CONCACAF Nations League",
    "goldcup": "Gold Cup",
    "internationalfriendlies": "International Friendlies",
    "worldcup": "FIFA World Cup",
}


def get_competition_display_name(slug: str) -> str:
    """Return a human-readable competition name for a filename slug."""
    return COMPETITION_DISPLAY_NAMES.get(slug, slug)


def team_filename(team_name: str) -> str:
    """Return a filesystem-safe slug for a team name."""
    return team_name.replace(".", "").replace(" ", "").replace("\n", "").lower()


def competition_filename(competition_id: str) -> str:
    """Return the output filename stem for a competition."""
    if competition_id not in COMPETITION_FILENAME_MAP:
        raise ValueError(f"Unknown competition_id: {competition_id!r}")
    return COMPETITION_FILENAME_MAP[competition_id]


@cache
def get_datetime_from_str(input_str: str) -> datetime:
    """Parse an ISO-format datetime string into a datetime object."""
    return datetime.fromisoformat(input_str)


@cache
def get_end_datetime(start_time: datetime, delta_hours: int) -> datetime:
    """Add a fixed number of hours to a start time to get an end datetime."""
    return start_time + timedelta(hours=delta_hours)


@cache
def get_competition_txt(input_str: str) -> str:
    """Return a display-friendly competition name, abbreviating Major League Soccer to MLS."""
    competition = (
        COMPETITION_TRANSLATE[input_str]
        if input_str in COMPETITION_TRANSLATE
        else input_str
    )
    competition = competition.replace("Major League Soccer", "MLS")
    return competition


@cache
def get_correct_team_name(input_team_name: str) -> str:
    """Return the canonical team name, applying known corrections."""
    correct_name = (
        TEAMS_FIX[input_team_name]
        if input_team_name in TEAMS_FIX
        else (input_team_name or "")
    )
    return correct_name or "???"


@cache
def get_correct_venue_name(name: str | None, city: str | None) -> str | None:
    """Build a formatted venue string from name and city components."""
    if city and name:
        return f"{name}, {city}"
    if name and not city:
        return name
    if city and not name:
        return city
    return "???"
