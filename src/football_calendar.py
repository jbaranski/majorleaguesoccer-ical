from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from icalendar import Calendar, Event

from src.utils import get_datetime_from_str, get_competition_txt, get_correct_team_name, get_correct_venue_name, get_end_datetime


@dataclass(frozen=True)
class FootballCalendarEvent:
    summary: str
    location: str
    start_date: datetime
    end_date: datetime
    competition: str
    description: str

    @staticmethod
    def to_football_calendar_events(api_response: list[dict]):
        return [FootballCalendarEvent.to_football_calendar_event(x) for x in api_response]

    @staticmethod
    def to_football_calendar_event(fixture: dict):
        start_date = get_datetime_from_str(fixture['matchDate'])
        competition = get_competition_txt(fixture['competition']['name'])
        summary = f"{get_correct_team_name(fixture.get('home', {}).get('fullName'))} vs. {get_correct_team_name(fixture.get('away', {}).get('fullName'))}"
        venue = get_correct_venue_name(fixture['venue']['name'], fixture['venue']['city'])
        return FootballCalendarEvent(
            summary=summary,
            location=venue,
            start_date=start_date,
            end_date=get_end_datetime(start_date, 2),
            competition=competition,
            description=f'{competition} - {summary}'
        )

    def to_event(self) -> Event:
        event = Event()
        event.add('summary', self.summary)
        if self.location:
            event.add('location', self.location)
        event.add('dtstart', self.start_date)
        event.add('dtend', self.end_date)
        event.add('competition', self.competition)
        event.add('description', self.description)
        return event


@dataclass()
class FootballCalendar:
    team_name: str
    season: int
    events: List[FootballCalendarEvent]
    cal: Calendar | None = field(init=False)
    cal_bytes: bytes | None = field(init=False)
    cal_sha256_str: str | None = field(init=False)

    def __post_init__(self):
        self.cal = None
        self.cal_bytes = None
        self.cal_sha256_str = None

    @staticmethod
    def to_football_calendar(team_name: str, season: int, events: List[FootballCalendarEvent]):
        return FootballCalendar(
            team_name=team_name,
            season=season,
            events=events
        )

    def to_calendar(self) -> Calendar:
        if self.cal is None:
            team_name_modified = self.team_name.replace('.', '').replace(' ', '').replace('\n', '').lower()
            cal = Calendar()
            # https://en.wikipedia.org/wiki/ICalendar
            cal.add('X-WR-CALNAME', self.team_name)
            cal.add('X-WR-CALDESC', f'All {self.team_name} fixtures for {self.season} season')
            cal.add('X-WR-RELCALID', f'{team_name_modified}-{self.season}'.replace(' ', ''))
            cal.add('X-PUBLISHED-TTL', 'PT6H')
            cal.add('URL', f'https://raw.githubusercontent.com/jbaranski/majorleaguesoccer-ical/refs/heads/main/calendars/{team_name_modified}.ics')
            cal.add('METHOD', 'PUBLISH')
            cal.add('VERSION', '2.0')
            cal.add('PRODID', 'mlscalendar.jeffsoftware.com')
            cal.add('CALSCALE', 'GREGORIAN')
            cal.add('X-MICROSOFT-CALSCALE', 'GREGORIAN')
            for x in self.events:
                cal.add_component(x.to_event())
            self.cal = cal
        return self.cal

    def to_bytes(self) -> bytes:
        if self.cal_bytes is None:
            self.cal_bytes = self.to_calendar().to_ical(sorted=True)
        return self.cal_bytes
