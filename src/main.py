import logging
import os
import time
from collections import defaultdict

import requests

from src.football_calendar import FootballCalendar, FootballCalendarEvent
from src.utils import get_correct_team_name

# Format: "season_id:season_year,season_id:season_year"
SEASONS_RAW = os.getenv('SEASONS', '')
SEASONS = [tuple(s.split(':')) for s in SEASONS_RAW.split(',') if s]

LEAGUE = os.getenv('LEAGUE')
OUTPUT_ROOT = os.getenv('OUTPUT_ROOT')
LOG_LEVEL = os.getenv('LOG_LEVEL')
NUM_TEAMS_EXPECTED = int(os.getenv('NUM_TEAMS_EXPECTED', 30))
EXCLUDED_COMPETITIONS = set(os.getenv('EXCLUDED_COMPETITIONS', '').split(','))

assert SEASONS
assert all(len(s) == 2 for s in SEASONS)
assert LEAGUE
assert OUTPUT_ROOT
assert NUM_TEAMS_EXPECTED
assert '' not in EXCLUDED_COMPETITIONS

logging.getLogger().setLevel(logging.DEBUG if LOG_LEVEL == 'DEBUG' else logging.INFO)


def get_data(seasons: list[tuple[str, str]]):
    teams = {}
    fixtures_map = defaultdict(list)
    all_fixtures = {}
    for season_id, season_year in seasons:
        response = requests.get(f'https://stats-api.mlssoccer.com/competitions/{LEAGUE}/seasons/{season_id}/standings')
        # The standings request can 404 for a future season so we can account for that
        # That means we cannot cut over from the old season until the new season standings are available
        if response.status_code != 200:
            logging.warning(f'Standings not available yet: {season_id} ({season_year})')
            continue

        entries = response.json().get('tables')[0].get('entries')
        for team in entries:
            teams[team.get('team_id') or team.get('club_id')] = team.get('team') or team.get('club')

    assert len(teams.keys()) == NUM_TEAMS_EXPECTED

    for season_id, season_year in seasons:
        logging.info(f'Processing season: {season_id} ({season_year})')
        page_token = None
        fixtures_list = []
        count = 0
        while True:
            url = f'https://stats-api.mlssoccer.com/matches/seasons/{season_id}?match_date%5Bgte%5D={season_year}-01-01&match_date%5Blte%5D={season_year}-12-31&per_page=1000&sort=planned_kickoff_time:asc'
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
            all_fixtures[fixture.get('match_id', (home_id or '') + (away_id or ''))] = fixture
    return teams, fixtures_map, all_fixtures


def main() -> None:
    teams, team_fixtures, all_fixtures = get_data(SEASONS)
    season_years_str = ','.join([year for _, year in SEASONS])
    for t_id, f in team_fixtures.items():
        team_name = get_correct_team_name(teams[t_id])
        cal = FootballCalendar.to_football_calendar(
            team_name,
            season_years_str,
            FootballCalendarEvent.to_football_calendar_events(f)
        )
        team_file_name = team_name.replace('.', '').replace(' ', '').replace('\n', '').lower()
        calendar_path = f'{OUTPUT_ROOT}/calendars/{team_file_name}.ics'
        calendar_path_home = f'{OUTPUT_ROOT}/calendars/{team_file_name}_home.ics'
        calendar_path_away = f'{OUTPUT_ROOT}/calendars/{team_file_name}_away.ics'
        with open(calendar_path, 'wb') as cf:
            cf.write(cal.to_bytes())
        with open(calendar_path_home, 'wb') as cf:
            cf.write(cal.to_bytes(home=True))
        with open(calendar_path_away, 'wb') as cf:
            cf.write(cal.to_bytes(away=True))
        logging.info(f'Calendar generated: num_fixtures={len(f)}, team={t_id}|{team_name}, seasons={season_years_str}, path={calendar_path}, home path={calendar_path_home}, away path={calendar_path_away}')

    # Generate unified MLS calendar with all matches deduplicated
    mls_calendar_path = f'{OUTPUT_ROOT}/calendars/mls.ics'
    with open(mls_calendar_path, 'wb') as cf:
        cf.write(FootballCalendar.to_football_calendar(
            'MLS',
            season_years_str,
            FootballCalendarEvent.to_football_calendar_events(list(all_fixtures.values()))
        ).to_bytes())
    logging.info(f'Calendar generated: num_fixtures={len(all_fixtures)}, calendar=MLS, seasons={season_years_str}, path={mls_calendar_path}')


if __name__ == '__main__':
    main()
    # asyncio.run(fetch_data())
