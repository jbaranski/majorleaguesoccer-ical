from typing import Protocol


class DataProvider(Protocol):
    """Protocol defining the interface for data providers."""

    def get_teams(
        self,
        competition_id: str,
        seasons: tuple[tuple[str, str], ...],
    ) -> dict[str, str]: ...

    def get_fixtures(
        self,
        seasons: tuple[tuple[str, str], ...],
        competition_id: str | None = None,
        excluded_competition_ids: frozenset[str] = frozenset(),
    ) -> list[dict]: ...
