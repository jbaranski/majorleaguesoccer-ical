import logging
import os
from collections.abc import Callable

from src.pipeline.context import CompetitionContext, CompetitionType
from src.pipeline.steps.aggregate import aggregate_international_calendars
from src.pipeline.steps.fetch_fixtures import fetch_fixtures
from src.pipeline.steps.fetch_teams import fetch_teams
from src.pipeline.steps.generate import generate_calendars
from src.pipeline.steps.write import write_calendars
from src.providers.mls_stats_api import MLSStatsAPIProvider

# Format: "season_id:season_year,season_id:season_year"
SEASONS_RAW = os.getenv("SEASONS", "")
SEASONS: tuple[tuple[str, str], ...] = tuple(
    tuple(s.split(":"))
    for s in SEASONS_RAW.split(",")
    if s  # type: ignore[misc]
)

LEAGUE = os.getenv("LEAGUE")
OUTPUT_ROOT = os.getenv("OUTPUT_ROOT")
LOG_LEVEL = os.getenv("LOG_LEVEL")
NUM_TEAMS_EXPECTED = int(os.getenv("NUM_TEAMS_EXPECTED", 30))
LEAGUE_COMPETITIONS: frozenset[str] = frozenset(
    os.getenv("LEAGUE_COMPETITIONS", "").split(",")
) - {""}
INTERNATIONAL_COMPETITIONS: frozenset[str] = frozenset(
    os.getenv("INTERNATIONAL_COMPETITIONS", "").split(",")
) - {""}

assert SEASONS, "SEASONS env var is required"
assert all(len(s) == 2 for s in SEASONS), (
    "Each SEASONS entry must be season_id:season_year"
)
assert LEAGUE, "LEAGUE env var is required"
assert OUTPUT_ROOT, "OUTPUT_ROOT env var is required"
assert NUM_TEAMS_EXPECTED, "NUM_TEAMS_EXPECTED must be > 0"

logging.getLogger().setLevel(logging.DEBUG if LOG_LEVEL == "DEBUG" else logging.INFO)

if not LEAGUE_COMPETITIONS:
    logging.warning("LEAGUE_COMPETITIONS is empty — no league fixtures will be fetched")

pipeline = [fetch_teams, fetch_fixtures, generate_calendars, write_calendars]


def run_pipeline(
    ctx: CompetitionContext,
    steps: list[Callable[[CompetitionContext], CompetitionContext]],
) -> CompetitionContext:
    """Thread context through each pipeline step in order."""
    for step in steps:
        ctx = step(ctx)
    return ctx


def main() -> None:
    """Build competition contexts and run the full pipeline for each."""
    provider = MLSStatsAPIProvider()

    competitions: list[CompetitionContext] = [
        CompetitionContext(
            competition_id=LEAGUE,
            competition_type=CompetitionType.LEAGUE,
            seasons=SEASONS,
            included_competition_ids=LEAGUE_COMPETITIONS,
            output_root=OUTPUT_ROOT,
            provider=provider,
            num_teams_expected=NUM_TEAMS_EXPECTED,
        ),
        *[
            CompetitionContext(
                competition_id=t_id,
                competition_type=CompetitionType.INTERNATIONAL,
                seasons=SEASONS,
                included_competition_ids=frozenset(),
                output_root=OUTPUT_ROOT,
                provider=provider,
            )
            for t_id in INTERNATIONAL_COMPETITIONS
        ],
    ]

    final_contexts = [run_pipeline(ctx, pipeline) for ctx in competitions]
    international_contexts = [
        c for c in final_contexts if c.competition_type == CompetitionType.INTERNATIONAL
    ]
    aggregate_international_calendars(international_contexts, OUTPUT_ROOT)


if __name__ == "__main__":
    main()
