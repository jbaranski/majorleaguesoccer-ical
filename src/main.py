import asyncio
import json
import logging
import os
import time
from collections import deque

import aiohttp

from src.api_sports import APISports
from src.football_calendar import FootballCalendar, FootballCalendarEvent

SEASON = int(os.getenv('SEASON', 0))
TEAMS = deque(json.loads(os.getenv('TEAMS')))
OUTPUT_ROOT = os.getenv('OUTPUT_ROOT')
LOG_LEVEL = os.getenv('LOG_LEVEL')

assert SEASON
assert OUTPUT_ROOT

logging.getLogger().setLevel(logging.DEBUG if LOG_LEVEL == 'DEBUG' else logging.INFO)

api_sports_client = APISports()


async def fetch_data() -> list[tuple[str, str, list[dict]]]:
    conn = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=conn) as client:
        teams_fixtures = []
        while len(TEAMS) > 0:
            time.sleep(1)
            futures = deque([])
            async with asyncio.TaskGroup() as tg:
                for t in TEAMS:
                    team_id, team_name = t['id'], t['name']
                    future = tg.create_task(api_sports_client.get_fixtures(client, team_id, SEASON))
                    futures.append((team_id, team_name, future))
            for _ in range(len(TEAMS)):
                team_id, team_name, future = futures[0]
                fixtures = future.result()
                if len(fixtures) > 0:
                    teams_fixtures.append((team_id, team_name, fixtures))
                    TEAMS.popleft()
                else:
                    TEAMS.rotate(-1)
                futures.popleft()
        return teams_fixtures
    raise Exception('Unable to fetch fixtures from API provider')


def main() -> None:
    teams_fixtures = asyncio.run(fetch_data())
    for team_id, team_name, fixtures in teams_fixtures:
        cal = FootballCalendar.to_football_calendar(
            team_name,
            SEASON,
            FootballCalendarEvent.to_football_calendar_events(fixtures)
        )
        calendar_path = f'{OUTPUT_ROOT}/calendars/{team_name.replace(".", "").replace(" ", "").lower()}.ics'
        with open(calendar_path, 'wb') as f:
            f.write(cal.to_bytes())
        logging.info(f'Calendar generated: num_fixtures={len(fixtures)}, team={team_id}|{team_name}, season={SEASON}, path={calendar_path}')


if __name__ == '__main__':
    main()
    # asyncio.run(fetch_data())
