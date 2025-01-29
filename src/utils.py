from datetime import datetime, timedelta
from functools import cache

COMPETITION_TRANSLATE = {
}

TEAMS_FIX = {
    'Los Angeles Football Club': 'Los Angeles FC',
    'CF Montréal': 'CF Montreal',
    'St. Louis CITY SC': 'St. Louis City SC',
    'Minnesota United FC': 'Minnesota United'
}


@cache
def get_datetime_from_str(input_str: str) -> datetime:
    return datetime.fromisoformat(input_str)


@cache
def get_end_datetime(start_time: datetime, delta_hours: int) -> datetime:
    return start_time + timedelta(hours=delta_hours)


@cache
def get_competition_txt(input_str: str) -> str:
    return COMPETITION_TRANSLATE[input_str] if input_str in COMPETITION_TRANSLATE else input_str


@cache
def get_correct_team_name(input_team_name: str) -> str:
    correct_name = TEAMS_FIX[input_team_name] if input_team_name in TEAMS_FIX else (input_team_name or '')
    return correct_name.replace('\n', '') or '???'


@cache
def get_correct_venue_name(name: str, city: str) -> str | None:
    venue = f"{name}, {city}" if name and city else ''
    return venue.replace('\\', '').replace('\n', '')
