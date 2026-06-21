import dataclasses
import logging

from src.pipeline.context import CompetitionContext


def fetch_teams(ctx: CompetitionContext) -> CompetitionContext:
    """Fetch teams for the competition and return an updated context.

    Calls the provider's get_teams method and optionally validates the team count
    against ctx.num_teams_expected.

    Args:
        ctx: The current pipeline context.

    Returns:
        A new context with the teams field populated.

    Raises:
        ValueError: If the number of fetched teams doesn't match num_teams_expected.
    """
    teams = ctx.provider.get_teams(
        competition_id=ctx.competition_id,
        seasons=ctx.seasons,
    )
    if ctx.num_teams_expected is not None and len(teams) != ctx.num_teams_expected:
        raise ValueError(f"Expected {ctx.num_teams_expected} teams, got {len(teams)}")
    logging.info(f"Fetched {len(teams)} teams for competition {ctx.competition_id}")
    return dataclasses.replace(ctx, teams=teams)
