import logging
from pathlib import Path

from src.football_calendar import FootballCalendar
from src.pipeline.context import CompetitionContext, CompetitionType
from src.utils import get_competition_filename


def _team_filename(team_name: str) -> str:
    """Return the output filename stem for a team."""
    return team_name.replace(".", "").replace(" ", "").replace("\n", "").lower()


def _write_competition_calendars(
    calendars: list[FootballCalendar],
    output_dir: Path,
    competition_id: str,
    include_home_away: bool,
) -> None:
    """Write calendar files: per-team .ics plus a master competition .ics."""
    for cal in calendars:
        if cal.team_name == competition_id:
            # Master calendar — use a friendly filename
            comp_filename = get_competition_filename(cal.team_name)
            master_path = output_dir / f"{comp_filename}.ics"
            master_path.write_bytes(cal.to_bytes())
            logging.info(f"Written master calendar: {master_path}")
        else:
            stem = _team_filename(cal.team_name)
            team_path = output_dir / f"{stem}.ics"
            team_path.write_bytes(cal.to_bytes())
            if include_home_away:
                team_path_home = output_dir / f"{stem}_home.ics"
                team_path_away = output_dir / f"{stem}_away.ics"
                team_path_home.write_bytes(cal.to_bytes(home=True))
                team_path_away.write_bytes(cal.to_bytes(away=True))
                logging.info(
                    f"Written calendars: path={team_path}, "
                    f"home path={team_path_home}, away path={team_path_away}"
                )
            else:
                logging.info(f"Written calendar: {team_path}")


def write_calendars(ctx: CompetitionContext) -> CompetitionContext:
    """Write calendar files to disk."""
    if ctx.competition_type == CompetitionType.LEAGUE:
        output_dir = Path(ctx.output_root) / "calendars"
    else:
        output_dir = Path(ctx.output_root) / "calendars" / "international"
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_competition_calendars(
        ctx.calendars,
        output_dir,
        ctx.competition_id,
        include_home_away=(ctx.competition_type == CompetitionType.LEAGUE),
    )

    return ctx
