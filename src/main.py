import logging
import os
import time

import requests

from src.football_calendar import FootballCalendar, FootballCalendarEvent

# Format: "season_id:season_year,season_id:season_year"
SEASONS_RAW = os.getenv('SEASONS', '')
SEASONS = [tuple(s.split(':')) for s in SEASONS_RAW.split(',') if s]

LEAGUE = os.getenv('LEAGUE')
OUTPUT_ROOT = os.getenv('OUTPUT_ROOT')
LOG_LEVEL = os.getenv('LOG_LEVEL')
EXCLUDED_COMPETITIONS = set(os.getenv('EXCLUDED_COMPETITIONS', '').split(','))

assert SEASONS
assert all(len(s) == 2 for s in SEASONS)
assert LEAGUE
assert OUTPUT_ROOT
assert '' not in EXCLUDED_COMPETITIONS

logging.getLogger().setLevel(logging.DEBUG if LOG_LEVEL == 'DEBUG' else logging.INFO)


def get_data(seasons: list[tuple[str, str]]) -> list[dict]:
    fixtures_by_id: dict[str, dict] = {}
    seasons_with_standings: list[tuple[str, str]] = []
    for season_id, season_year in seasons:
        response = requests.get(f'https://stats-api.mlssoccer.com/competitions/{LEAGUE}/seasons/{season_id}/standings')
        # The standings request can 404 for a future season so we can account for that
        # That means we cannot cut over from the old season until the new season standings are available
        if response.status_code != 200:
            logging.warning(f'Standings not available yet: {season_id} ({season_year})')
            continue
        seasons_with_standings.append((season_id, season_year))

    for season_id, season_year in seasons_with_standings:
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
            match_id = fixture.get('match_id')
            if not match_id:
                logging.warning('Skipping fixture without match_id')
                continue
            fixtures_by_id[str(match_id)] = fixture
    return list(fixtures_by_id.values())


def main() -> None:
    fixtures = get_data(SEASONS)
    season_years_str = ','.join([year for _, year in SEASONS])
    calendars_dir = f'{OUTPUT_ROOT}/calendars'
    os.makedirs(calendars_dir, exist_ok=True)
    cal = FootballCalendar.to_football_calendar(
        'MLS',
        season_years_str,
        FootballCalendarEvent.to_football_calendar_events(fixtures)
    )
    calendar_path = f'{calendars_dir}/mls.ics'
    with open(calendar_path, 'wb') as cf:
        cf.write(cal.to_bytes())
    logging.info(f'Calendar generated: num_fixtures={len(fixtures)}, seasons={season_years_str}, path={calendar_path}')


if __name__ == '__main__':
    main()
    # asyncio.run(fetch_data())
