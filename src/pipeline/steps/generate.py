import dataclasses
import logging
from collections import defaultdict

from src.football_calendar import FootballCalendar, FootballCalendarEvent
from src.pipeline.context import CompetitionContext, CompetitionType
from src.utils import get_correct_team_name


def generate_calendars(ctx: CompetitionContext) -> CompetitionContext:
    """Generate calendar objects for each team and a master calendar.

    For LEAGUE competitions, builds per-team calendars from fixtures filtered
    to that team's matches. For TOURNAMENT competitions, builds per-team calendars
    from all tournament fixtures. Also generates a master calendar with all fixtures.

    Args:
        ctx: The current pipeline context (teams and fixtures must be populated).

    Returns:
        A new context with the calendars field populated as a list of FootballCalendar.
    """
    season_years_str = ",".join([year for _, year in ctx.seasons])
    calendars: list[FootballCalendar] = []

    if ctx.competition_type == CompetitionType.LEAGUE:
        # Build per-team fixture maps and deduplicated all_fixtures dict
        fixtures_map: dict[str, list[dict]] = defaultdict(list)
        all_fixtures: dict[str, dict] = {}

        for fixture in ctx.fixtures:
            home_id = fixture.get("home_team_id")
            away_id = fixture.get("away_team_id")
            if home_id in ctx.teams:
                fixtures_map[home_id].append(fixture)
            if away_id in ctx.teams:
                fixtures_map[away_id].append(fixture)
            all_fixtures[fixture.get("match_id", (home_id or "") + (away_id or ""))] = (
                fixture
            )

        for t_id, team_fixtures in fixtures_map.items():
            team_name = get_correct_team_name(ctx.teams[t_id])
            cal = FootballCalendar.to_football_calendar(
                team_name,
                season_years_str,
                FootballCalendarEvent.to_football_calendar_events(team_fixtures),
            )
            calendars.append(cal)
            logging.info(
                f"Calendar generated: num_fixtures={len(team_fixtures)}, "
                f"team={t_id}|{team_name}, seasons={season_years_str}"
            )

        # Master calendar with all deduplicated fixtures
        master_cal = FootballCalendar.to_football_calendar(
            "MLS",
            season_years_str,
            FootballCalendarEvent.to_football_calendar_events(
                list(all_fixtures.values())
            ),
        )
        calendars.append(master_cal)
        logging.info(
            f"Calendar generated: num_fixtures={len(all_fixtures)}, "
            f"calendar=MLS, seasons={season_years_str}"
        )

    else:
        # Tournament mode: per-team calendars from all tournament fixtures
        fixtures_map = defaultdict(list)
        all_fixture_ids: set[str] = set()

        for fixture in ctx.fixtures:
            home_id = fixture.get("home_team_id")
            away_id = fixture.get("away_team_id")
            if home_id in ctx.teams:
                fixtures_map[home_id].append(fixture)
            if away_id in ctx.teams:
                fixtures_map[away_id].append(fixture)
            all_fixture_ids.add(
                fixture.get("match_id", (home_id or "") + (away_id or ""))
            )

        for t_id, team_fixtures in fixtures_map.items():
            team_name = get_correct_team_name(ctx.teams[t_id])
            cal = FootballCalendar.to_football_calendar(
                team_name,
                season_years_str,
                FootballCalendarEvent.to_football_calendar_events(team_fixtures),
            )
            calendars.append(cal)
            logging.info(
                f"Tournament calendar generated: num_fixtures={len(team_fixtures)}, "
                f"team={t_id}|{team_name}, seasons={season_years_str}, "
                f"competition={ctx.competition_id}"
            )

        # Master tournament calendar
        master_cal = FootballCalendar.to_football_calendar(
            ctx.competition_id,
            season_years_str,
            FootballCalendarEvent.to_football_calendar_events(ctx.fixtures),
        )
        calendars.append(master_cal)
        logging.info(
            f"Tournament master calendar generated: num_fixtures={len(ctx.fixtures)}, "
            f"competition={ctx.competition_id}, seasons={season_years_str}"
        )

    return dataclasses.replace(ctx, calendars=calendars)
