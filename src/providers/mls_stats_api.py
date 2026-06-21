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
        """Fetch teams from the MLS Stats API standings endpoint.

        A 404 response for a season's standings is treated as a warning rather
        than an error, since future seasons may not have standings yet.

        Args:
            competition_id: The competition identifier.
            seasons: An immutable tuple of (season_id, season_year) tuples.

        Returns:
            A dict mapping team_id to team_name.
        """
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
        competition_id: str | None = None,
        excluded_competition_ids: frozenset[str] = frozenset(),
    ) -> list[dict]:
        """Fetch fixtures from the MLS Stats API matches endpoint.

        Supports two modes:
        - Tournament mode: if competition_id is provided, only include fixtures
          where fixture['competition_id'] == competition_id.
        - League mode: exclude fixtures where fixture['competition_id'] is in
          excluded_competition_ids.

        Args:
            seasons: An immutable tuple of (season_id, season_year) tuples.
            competition_id: If provided, only include fixtures for this competition.
            excluded_competition_ids: Competition IDs to exclude (league mode).

        Returns:
            A flat list of fixture dicts.
        """
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
                    fixture_competition_id = fixture.get("competition_id")
                    if competition_id is not None:
                        # Tournament mode: only include fixtures for this competition
                        if fixture_competition_id == competition_id:
                            all_fixtures.append(fixture)
                    elif fixture_competition_id not in excluded_competition_ids:
                        # League mode: exclude specified competitions
                        all_fixtures.append(fixture)

                count += 1
                if not page_token or len(temp_fixtures) == 0 or count > 10:
                    break
                time.sleep(0.25)

        return all_fixtures
