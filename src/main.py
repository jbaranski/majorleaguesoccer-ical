import logging
import os

from src.pipeline.context import CompetitionContext, CompetitionType
from src.pipeline.steps.fetch_fixtures import fetch_fixtures
from src.pipeline.steps.fetch_teams import fetch_teams
from src.pipeline.steps.generate import generate_calendars
from src.pipeline.steps.write import write_calendars
from src.providers.mls_stats_api import MLSStatsAPIProvider

# Format: "season_id:season_year,season_id:season_year"
SEASONS_RAW = os.getenv("SEASONS", "")
SEASONS: list[tuple[str, str]] = [
    tuple(s.split(":"))
    for s in SEASONS_RAW.split(",")
    if s  # type: ignore[misc]
]

LEAGUE = os.getenv("LEAGUE")
OUTPUT_ROOT = os.getenv("OUTPUT_ROOT")
LOG_LEVEL = os.getenv("LOG_LEVEL")
NUM_TEAMS_EXPECTED = int(os.getenv("NUM_TEAMS_EXPECTED", 30))
MLS_EXCLUDED_COMPETITIONS: frozenset[str] = frozenset(
    os.getenv("MLS_EXCLUDED_COMPETITIONS", "").split(",")
) - {""}
TOURNAMENT_COMPETITIONS: frozenset[str] = frozenset(
    os.getenv("TOURNAMENT_COMPETITIONS", "").split(",")
) - {""}

assert SEASONS, "SEASONS env var is required"
assert all(len(s) == 2 for s in SEASONS), (
    "Each SEASONS entry must be season_id:season_year"
)
assert LEAGUE, "LEAGUE env var is required"
assert OUTPUT_ROOT, "OUTPUT_ROOT env var is required"
assert NUM_TEAMS_EXPECTED, "NUM_TEAMS_EXPECTED must be > 0"

logging.getLogger().setLevel(logging.DEBUG if LOG_LEVEL == "DEBUG" else logging.INFO)

pipeline = [fetch_teams, fetch_fixtures, generate_calendars, write_calendars]


def run_pipeline(
    ctx: CompetitionContext,
    steps: list,
) -> CompetitionContext:
    """Run a sequence of pipeline steps, threading context through each.

    Args:
        ctx: The initial competition context.
        steps: Ordered list of step callables, each (ctx) -> ctx.

    Returns:
        The final context after all steps have run.
    """
    for step in steps:
        ctx = step(ctx)
    return ctx


def main() -> None:
    """Entry point: build competition contexts and run the full pipeline for each."""
    provider = MLSStatsAPIProvider()
    # For the league, exclude both explicit exclusions and tournament competitions
    all_excluded = MLS_EXCLUDED_COMPETITIONS | TOURNAMENT_COMPETITIONS

    competitions: list[CompetitionContext] = [
        CompetitionContext(
            competition_id=LEAGUE,
            competition_type=CompetitionType.LEAGUE,
            seasons=SEASONS,
            excluded_competition_ids=all_excluded,
            output_root=OUTPUT_ROOT,
            provider=provider,
            num_teams_expected=NUM_TEAMS_EXPECTED,
        ),
        *[
            CompetitionContext(
                competition_id=t_id,
                competition_type=CompetitionType.TOURNAMENT,
                seasons=SEASONS,
                excluded_competition_ids=frozenset(),
                output_root=OUTPUT_ROOT,
                provider=provider,
            )
            for t_id in TOURNAMENT_COMPETITIONS
        ],
    ]

    for ctx in competitions:
        run_pipeline(ctx, pipeline)


if __name__ == "__main__":
    main()
