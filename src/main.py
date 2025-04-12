import logging
import os
import time
from collections import defaultdict

import requests

from src.football_calendar import FootballCalendar, FootballCalendarEvent
from src.utils import get_correct_team_name

SEASON = os.getenv('SEASON')
SEASON_YEAR = int(os.getenv('SEASON_YEAR', 0))
LEAGUE = os.getenv('LEAGUE')
OUTPUT_ROOT = os.getenv('OUTPUT_ROOT')
LOG_LEVEL = os.getenv('LOG_LEVEL')
NUM_TEAMS_EXPECTED = int(os.getenv('NUM_TEAMS_EXPECTED', 30))
EXCLUDED_COMPETITIONS = set(os.getenv('EXCLUDED_COMPETITIONS', '').split(','))

assert SEASON
assert SEASON_YEAR > 0
assert LEAGUE
assert OUTPUT_ROOT
assert NUM_TEAMS_EXPECTED
assert '' not in EXCLUDED_COMPETITIONS

logging.getLogger().setLevel(logging.DEBUG if LOG_LEVEL == 'DEBUG' else logging.INFO)


def get_data():
    teams = {}
    fixtures_map = defaultdict(list)
    response = requests.get(f'https://stats-api.mlssoccer.com/competitions/{LEAGUE}/seasons/{SEASON}/standings') \
                       .json() \
                       .get('tables')[0] \
                       .get('entries')
    for team in response:
        teams[team.get('team_id') or team.get('club_id')] = team.get('team') or team.get('club')

    assert len(teams.keys()) == NUM_TEAMS_EXPECTED

    page_token = None
    fixtures_list = []
    count = 0
    while True:
        url = f'https://stats-api.mlssoccer.com/matches/seasons/{SEASON}?match_date%5Bgte%5D=2025-01-01&match_date%5Blte%5D=2025-12-31&per_page=1000&sort=planned_kickoff_time:asc'
        if page_token is not None:
            url += f'&page_token={page_token}'
        response = requests.get(url, headers={'User-Agent': 'JEFF-bot'}).json()
        page_token = response.get('next_page_token')
        temp_fixtures = response.get('schedule')
        fixtures_list += temp_fixtures
        count += 1
        if not page_token or len(temp_fixtures) == 0 or count > 10:
            break
        time.sleep(.25)

    for fixture in fixtures_list:
        if fixture.get('competition_id') in EXCLUDED_COMPETITIONS:
            continue
        # NOTE: For some reason the schedule may be incomplete and a team not available for a fixture
        home_id = fixture.get('home_team_id')
        away_id = fixture.get('away_team_id')
        if home_id in teams:
            fixtures_map[home_id].append(fixture)
        if away_id in teams:
            fixtures_map[away_id].append(fixture)
    return teams, fixtures_map


def main() -> None:
    teams, team_fixtures = get_data()
    for t_id, f in team_fixtures.items():
        team_name = get_correct_team_name(teams[t_id])
        cal = FootballCalendar.to_football_calendar(
            team_name,
            SEASON_YEAR,
            FootballCalendarEvent.to_football_calendar_events(f)
        )
        calendar_path = f'{OUTPUT_ROOT}/calendars/{team_name.replace(".", "").replace(" ", "").replace("\n", "").lower()}.ics'
        with open(calendar_path, 'wb') as cf:
            cf.write(cal.to_bytes())
        logging.info(f'Calendar generated: num_fixtures={len(f)}, team={t_id}|{team_name}, season={SEASON} ({SEASON_YEAR}), path={calendar_path}')


if __name__ == '__main__':
    main()
    # asyncio.run(fetch_data())
