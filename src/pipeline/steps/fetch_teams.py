import dataclasses
import logging

from src.pipeline.context import CompetitionContext


def fetch_teams(ctx: CompetitionContext) -> CompetitionContext:
    """Fetch teams for the competition and return an updated context."""
    teams = ctx.provider.get_teams(
        competition_id=ctx.competition_id,
        seasons=ctx.seasons,
    )
    # num_teams_expected is None for international competitions where count isn't fixed
    if ctx.num_teams_expected is not None and len(teams) != ctx.num_teams_expected:
        raise ValueError(f"Expected {ctx.num_teams_expected} teams, got {len(teams)}")
    logging.info(f"Fetched {len(teams)} teams for competition {ctx.competition_id}")
    return dataclasses.replace(ctx, teams=teams)
