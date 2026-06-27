import logging
from pathlib import Path

from src.football_calendar import FootballCalendar
from src.pipeline.context import CompetitionContext, CompetitionType
from src.utils import team_filename


def _write_league_calendars(
    calendars: list[FootballCalendar],
    output_dir: Path,
) -> None:
    for cal in calendars:
        if cal.is_competition_calendar:
            url_path = f"calendars/{cal.team_name}"
            master_path = output_dir / f"{cal.team_name}.ics"
            master_path.write_bytes(cal.to_bytes(url_path))
            logging.info(f"Written master calendar: {master_path}")
        else:
            stem = team_filename(cal.team_name)
            url_path = f"calendars/{stem}"
            team_path = output_dir / f"{stem}.ics"
            team_path.write_bytes(cal.to_bytes(url_path))
            team_path_home = output_dir / f"{stem}_home.ics"
            team_path_away = output_dir / f"{stem}_away.ics"
            team_path_home.write_bytes(cal.to_bytes(url_path, home=True))
            team_path_away.write_bytes(cal.to_bytes(url_path, away=True))
            logging.info(
                f"Written calendars: path={team_path}, "
                f"home path={team_path_home}, away path={team_path_away}"
            )


def _write_international_master(
    calendars: list[FootballCalendar],
    output_dir: Path,
) -> None:
    for cal in calendars:
        if cal.is_competition_calendar:
            url_path = f"calendars/international/{cal.team_name}"
            master_path = output_dir / f"{cal.team_name}.ics"
            master_path.write_bytes(cal.to_bytes(url_path))
            logging.info(f"Written international master calendar: {master_path}")


def write_calendars(ctx: CompetitionContext) -> CompetitionContext:
    """Write calendar files to disk."""
    if ctx.competition_type == CompetitionType.LEAGUE:
        output_dir = Path(ctx.output_root) / "calendars"
        output_dir.mkdir(parents=True, exist_ok=True)
        _write_league_calendars(ctx.calendars, output_dir)
    else:
        output_dir = Path(ctx.output_root) / "calendars" / "international"
        output_dir.mkdir(parents=True, exist_ok=True)
        _write_international_master(ctx.calendars, output_dir)

    return ctx
