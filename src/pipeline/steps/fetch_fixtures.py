import dataclasses
import logging

from src.pipeline.context import CompetitionContext, CompetitionType


def fetch_fixtures(ctx: CompetitionContext) -> CompetitionContext:
    """Fetch fixtures for the competition and return an updated context."""
    if ctx.competition_type == CompetitionType.LEAGUE:
        included = ctx.included_competition_ids
    else:
        included = frozenset({ctx.competition_id})

    fixtures = ctx.provider.get_fixtures(
        seasons=ctx.seasons,
        included_competition_ids=included,
    )

    logging.info(
        f"Fetched {len(fixtures)} fixtures for competition {ctx.competition_id}"
    )
    return dataclasses.replace(ctx, fixtures=fixtures)
