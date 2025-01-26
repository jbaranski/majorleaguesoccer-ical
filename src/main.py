import logging
import os
from collections import defaultdict

import requests

from src.football_calendar import FootballCalendar, FootballCalendarEvent
from src.utils import get_correct_team_name

SEASON = int(os.getenv('SEASON', 0))
LEAGUE = int(os.getenv('LEAGUE'))
OUTPUT_ROOT = os.getenv('OUTPUT_ROOT')
LOG_LEVEL = os.getenv('LOG_LEVEL')

assert SEASON
assert LEAGUE
assert OUTPUT_ROOT

logging.getLogger().setLevel(logging.DEBUG if LOG_LEVEL == 'DEBUG' else logging.INFO)


def get_data():
    teams = {}
    fixtures = defaultdict(list)
    response = requests.get(f'https://stats-api.mlssoccer.com/v1/clubs?&competition_opta_id={LEAGUE}&season_opta_id={SEASON}&order_by=club_name').json()
    for team in response:
        teams[team['opta_id']] = team['name']
    response = requests.get(f'https://sportapi.mlssoccer.com/api/matches?culture=en-us&dateFrom={SEASON}-01-01&dateTo={SEASON + 1}-12-31').json()
    for fixture in response:
        # NOTE: For some reason the schedule may be incomplete and a team not available for a fixture
        home_id = fixture.get('home', {}).get('optaId')
        away_id = fixture.get('away', {}).get('optaId')
        if home_id in teams:
            fixtures[home_id].append(fixture)
        if away_id in teams:
            fixtures[away_id].append(fixture)
    return teams, fixtures


def main() -> None:
    teams, team_fixtures = get_data()
    for t_id, f in team_fixtures.items():
        team_name = get_correct_team_name(teams[t_id])
        cal = FootballCalendar.to_football_calendar(
            team_name,
            SEASON,
            FootballCalendarEvent.to_football_calendar_events(f)
        )
        calendar_path = f'{OUTPUT_ROOT}/calendars/{team_name.replace(".", "").replace(" ", "").replace("\n", "").lower()}.ics'
        with open(calendar_path, 'wb') as cf:
            cf.write(cal.to_bytes())
        logging.info(f'Calendar generated: num_fixtures={len(f)}, team={t_id}|{team_name}, season={SEASON}, path={calendar_path}')


if __name__ == '__main__':
    main()
    # asyncio.run(fetch_data())
