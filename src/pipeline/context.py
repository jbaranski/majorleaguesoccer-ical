from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.providers.base import DataProvider


class CompetitionType(Enum):
    """Enum representing the type of competition."""

    LEAGUE = "league"
    INTERNATIONAL = "international"


@dataclass(frozen=True)
class CompetitionContext:
    """Immutable context object passed through the pipeline steps."""

    competition_id: str
    competition_type: CompetitionType
    seasons: tuple[tuple[str, str], ...]
    included_competition_ids: frozenset[str]
    output_root: str
    provider: DataProvider
    num_teams_expected: int | None = None
    # populated by steps:
    teams: dict[str, str] = field(default_factory=dict)
    fixtures: list[dict] = field(default_factory=list)
    calendars: list = field(default_factory=list)
