from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.providers.base import DataProvider


class CompetitionType(Enum):
    """Enum representing the type of competition."""

    LEAGUE = "league"
    TOURNAMENT = "tournament"


@dataclass(frozen=True)
class CompetitionContext:
    """Immutable context object passed through the pipeline steps.

    Attributes:
        competition_id: The competition identifier.
        competition_type: Whether this is a league or tournament.
        seasons: An immutable tuple of (season_id, season_year) tuples.
        excluded_competition_ids: Competition IDs to exclude from fixtures.
        output_root: Root directory for output files.
        provider: The data provider instance.
        num_teams_expected: Expected number of teams (for validation).
        teams: Populated by fetch_teams step; maps team_id to team_name.
        fixtures: Populated by fetch_fixtures step; list of fixture dicts.
        calendars: Populated by generate step; list of FootballCalendar objects.
    """

    competition_id: str
    competition_type: CompetitionType
    seasons: tuple[tuple[str, str], ...]
    excluded_competition_ids: frozenset[str]
    output_root: str
    provider: DataProvider
    num_teams_expected: int | None = None
    # populated by steps:
    teams: dict[str, str] = field(default_factory=dict)
    fixtures: list[dict] = field(default_factory=list)
    calendars: list = field(default_factory=list)
