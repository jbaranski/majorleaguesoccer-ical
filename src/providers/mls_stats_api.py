import logging
import time

import requests


class MLSStatsAPIProvider:
    """Data provider that fetches data from the MLS Stats API."""

    def get_teams(
        self,
        competition_id: str,
        seasons: tuple[tuple[str, str], ...],
    ) -> dict[str, str]:
        """Fetch teams from the MLS Stats API standings endpoint."""
        teams: dict[str, str] = {}
        for season_id, season_year in seasons:
            url = (
                f"https://stats-api.mlssoccer.com/competitions/{competition_id}"
                f"/seasons/{season_id}/standings"
            )
            response = requests.get(url)
            if response.status_code != 200:
                logging.warning(
                    f"Standings not available yet: {season_id} ({season_year})"
                )
                continue
            entries = response.json().get("tables")[0].get("entries")
            for team in entries:
                teams[team.get("team_id") or team.get("club_id")] = team.get(
                    "team"
                ) or team.get("club")

        return teams

    def get_fixtures(
        self,
        seasons: tuple[tuple[str, str], ...],
        included_competition_ids: frozenset[str],
    ) -> list[dict]:
        """Fetch fixtures from the MLS Stats API matches endpoint."""
        all_fixtures: list[dict] = []
        for season_id, season_year in seasons:
            logging.info(f"Processing season: {season_id} ({season_year})")
            page_token = None
            count = 0
            while True:
                url = (
                    f"https://stats-api.mlssoccer.com/matches/seasons/{season_id}"
                    f"?match_date%5Bgte%5D={season_year}-01-01"
                    f"&match_date%5Blte%5D={season_year}-12-31"
                    f"&per_page=1000&sort=planned_kickoff_time:asc"
                )
                if page_token is not None:
                    url += f"&page_token={page_token}"
                response = requests.get(url, headers={"User-Agent": "JEFF-bot"}).json()
                page_token = response.get("next_page_token")
                temp_fixtures = response.get("schedule", [])

                for fixture in temp_fixtures:
                    if fixture.get("competition_id") in included_competition_ids:
                        all_fixtures.append(fixture)

                count += 1
                if not page_token or len(temp_fixtures) == 0 or count > 10:
                    break
                time.sleep(0.25)

        return all_fixtures
