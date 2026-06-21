import logging
from pathlib import Path

from src.football_calendar import FootballCalendar
from src.pipeline.context import CompetitionContext, CompetitionType
from src.utils import get_competition_filename


def _team_filename(team_name: str) -> str:
    """Return the output filename stem for a team.

    Args:
        team_name: The team name to convert.

    Returns:
        A lowercased, punctuation-stripped filename stem.
    """
    return team_name.replace(".", "").replace(" ", "").replace("\n", "").lower()


def write_calendars(ctx: CompetitionContext) -> CompetitionContext:
    """Write calendar files to disk.

    For LEAGUE competitions, writes per-team all/home/away .ics files plus a
    master mls.ics. For TOURNAMENT competitions, writes per-team .ics files
    (no home/away split) plus a master {competition_filename}.ics.

    Args:
        ctx: The current pipeline context (calendars must be populated).

    Returns:
        The unchanged context (write is a terminal step).
    """
    output_dir = Path(ctx.output_root) / "calendars"
    output_dir.mkdir(parents=True, exist_ok=True)

    if ctx.competition_type == CompetitionType.LEAGUE:
        _write_league_calendars(ctx.calendars, output_dir)
    else:
        _write_tournament_calendars(ctx.calendars, output_dir, ctx.competition_id)

    return ctx


def _write_league_calendars(
    calendars: list[FootballCalendar], output_dir: Path
) -> None:
    """Write league calendar files: per-team all/home/away plus master mls.ics.

    Args:
        calendars: List of FootballCalendar objects (last one is the master).
        output_dir: Directory to write files into.
    """
    for cal in calendars:
        if cal.team_name == "MLS":
            # Master calendar
            master_path = output_dir / "mls.ics"
            master_path.write_bytes(cal.to_bytes())
            logging.info(f"Written master calendar: {master_path}")
        else:
            stem = _team_filename(cal.team_name)
            team_path = output_dir / f"{stem}.ics"
            team_path_home = output_dir / f"{stem}_home.ics"
            team_path_away = output_dir / f"{stem}_away.ics"
            team_path.write_bytes(cal.to_bytes())
            team_path_home.write_bytes(cal.to_bytes(home=True))
            team_path_away.write_bytes(cal.to_bytes(away=True))
            logging.info(
                f"Written calendars: path={team_path}, "
                f"home path={team_path_home}, away path={team_path_away}"
            )


def _write_tournament_calendars(
    calendars: list[FootballCalendar],
    output_dir: Path,
    competition_id: str,
) -> None:
    """Write tournament calendar files: per-team .ics plus master competition .ics.

    Args:
        calendars: List of FootballCalendar objects (last one is the master).
        output_dir: Directory to write files into.
        competition_id: The competition ID (used to identify the master calendar).
    """
    for cal in calendars:
        if cal.team_name == competition_id:
            # Master tournament calendar — look up a friendly filename
            comp_filename = get_competition_filename(cal.team_name)
            master_path = output_dir / f"{comp_filename}.ics"
            master_path.write_bytes(cal.to_bytes())
            logging.info(f"Written tournament master calendar: {master_path}")
        else:
            stem = _team_filename(cal.team_name)
            team_path = output_dir / f"{stem}.ics"
            team_path.write_bytes(cal.to_bytes())
            logging.info(f"Written tournament calendar: {team_path}")
