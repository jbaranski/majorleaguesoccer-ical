import logging
from pathlib import Path

from src.football_calendar import FootballCalendar, FootballCalendarEvent
from src.pipeline.context import CompetitionContext
from src.utils import team_filename


def aggregate_international_calendars(
    contexts: list[CompetitionContext], output_root: str
) -> None:
    """Write combined per-country and master tournament calendars across all international competitions."""
    if not contexts:
        return

    seasons_str = ",".join(
        dict.fromkeys(year for ctx in contexts for _, year in ctx.seasons)
    )

    all_events: dict[str, FootballCalendarEvent] = {}
    events_by_country: dict[str, dict[str, FootballCalendarEvent]] = {}

    for ctx in contexts:
        for cal in ctx.calendars:
            if cal.is_competition_calendar:
                continue
            for event in cal.events:
                all_events.setdefault(event.match_id, event)
                events_by_country.setdefault(cal.team_name, {}).setdefault(
                    event.match_id, event
                )

    output_dir = Path(output_root) / "calendars" / "international"
    countries_dir = output_dir / "countries"
    countries_dir.mkdir(parents=True, exist_ok=True)

    for country_name, events_map in events_by_country.items():
        slug = team_filename(country_name)
        url_path = f"calendars/international/countries/{slug}"
        cal = FootballCalendar.to_football_calendar(
            country_name, seasons_str, list(events_map.values())
        )
        country_path = countries_dir / f"{slug}.ics"
        country_path.write_bytes(cal.to_bytes(url_path))
        logging.info(f"Written aggregate country calendar: {country_path}")
