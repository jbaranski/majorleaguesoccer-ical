import dataclasses
import logging

from src.pipeline.context import CompetitionContext, CompetitionType


def fetch_fixtures(ctx: CompetitionContext) -> CompetitionContext:
    """Fetch fixtures for the competition and return an updated context.

    For LEAGUE competitions, fetches all fixtures excluding the configured
    excluded_competition_ids. For TOURNAMENT competitions, fetches only fixtures
    belonging to the specific competition_id.

    Args:
        ctx: The current pipeline context.

    Returns:
        A new context with the fixtures field populated.
    """
    if ctx.competition_type == CompetitionType.LEAGUE:
        fixtures = ctx.provider.get_fixtures(
            seasons=ctx.seasons,
            competition_id=None,
            excluded_competition_ids=ctx.excluded_competition_ids,
        )
    else:
        fixtures = ctx.provider.get_fixtures(
            seasons=ctx.seasons,
            competition_id=ctx.competition_id,
            excluded_competition_ids=frozenset(),
        )

    logging.info(
        f"Fetched {len(fixtures)} fixtures for competition {ctx.competition_id}"
    )
    return dataclasses.replace(ctx, fixtures=fixtures)
