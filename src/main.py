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
MLS_SEASONS_RAW = os.getenv("MLS_SEASONS", "")
MLS_SEASONS: tuple[tuple[str, str], ...] = tuple(
    tuple(s.split(":"))
    for s in MLS_SEASONS_RAW.split(",")
    if s  # type: ignore[misc]
)

MLS_LEAGUE = os.getenv("MLS_LEAGUE")
OUTPUT_ROOT = os.getenv("OUTPUT_ROOT")
LOG_LEVEL = os.getenv("LOG_LEVEL")
MLS_NUM_TEAMS_EXPECTED = int(os.getenv("MLS_NUM_TEAMS_EXPECTED", 30))
MLS_LEAGUE_COMPETITIONS: frozenset[str] = frozenset(
    os.getenv("MLS_LEAGUE_COMPETITIONS", "").split(",")
) - {""}
MLS_INTERNATIONAL_COMPETITIONS: frozenset[str] = frozenset(
    os.getenv("MLS_INTERNATIONAL_COMPETITIONS", "").split(",")
) - {""}

assert MLS_SEASONS, "MLS_SEASONS env var is required"
assert all(len(s) == 2 for s in MLS_SEASONS), (
    "Each MLS_SEASONS entry must be season_id:season_year"
)
assert MLS_LEAGUE, "MLS_LEAGUE env var is required"
assert OUTPUT_ROOT, "OUTPUT_ROOT env var is required"
assert MLS_NUM_TEAMS_EXPECTED, "MLS_NUM_TEAMS_EXPECTED must be > 0"

logging.getLogger().setLevel(logging.DEBUG if LOG_LEVEL == "DEBUG" else logging.INFO)

if not MLS_LEAGUE_COMPETITIONS:
    logging.warning(
        "MLS_LEAGUE_COMPETITIONS is empty — no league fixtures will be fetched"
    )

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
            competition_id=MLS_LEAGUE,
            competition_type=CompetitionType.LEAGUE,
            seasons=MLS_SEASONS,
            included_competition_ids=MLS_LEAGUE_COMPETITIONS,
            output_root=OUTPUT_ROOT,
            provider=provider,
            num_teams_expected=MLS_NUM_TEAMS_EXPECTED,
        ),
        *[
            CompetitionContext(
                competition_id=t_id,
                competition_type=CompetitionType.INTERNATIONAL,
                seasons=MLS_SEASONS,
                included_competition_ids=frozenset(),
                output_root=OUTPUT_ROOT,
                provider=provider,
            )
            for t_id in MLS_INTERNATIONAL_COMPETITIONS
        ],
    ]

    final_contexts = [run_pipeline(ctx, pipeline) for ctx in competitions]
    international_contexts = [
        c for c in final_contexts if c.competition_type == CompetitionType.INTERNATIONAL
    ]
    aggregate_international_calendars(international_contexts, OUTPUT_ROOT)


if __name__ == "__main__":
    main()
