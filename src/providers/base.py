from typing import Protocol


class DataProvider(Protocol):
    """Protocol defining the interface for data providers."""

    def get_teams(
        self,
        competition_id: str,
        seasons: tuple[tuple[str, str], ...],
    ) -> dict[str, str]:
        """Fetch teams for the given competition and seasons.

        Args:
            competition_id: The competition identifier.
            seasons: An immutable tuple of (season_id, season_year) tuples.

        Returns:
            A dict mapping team_id to team_name.
        """
        ...

    def get_fixtures(
        self,
        seasons: tuple[tuple[str, str], ...],
        competition_id: str | None = None,
        excluded_competition_ids: frozenset[str] = frozenset(),
    ) -> list[dict]:
        """Fetch fixtures for the given seasons.

        Args:
            seasons: An immutable tuple of (season_id, season_year) tuples.
            competition_id: If provided, only include fixtures for this competition (tournament mode).
            excluded_competition_ids: Competition IDs to exclude from results (league mode).

        Returns:
            A flat list of fixture dicts.
        """
        ...
