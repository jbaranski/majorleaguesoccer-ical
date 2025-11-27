from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List
from icalendar import Calendar, Event
from src.utils import get_datetime_from_str, get_competition_txt, get_correct_team_name, get_correct_venue_name, get_end_datetime


@dataclass(frozen=True)
class FootballCalendarEvent:
    match_id: str
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
        start_date = get_datetime_from_str(fixture['planned_kickoff_time'])
        competition = get_competition_txt(fixture['competition_name'])
        home_team_name = get_correct_team_name(fixture.get('home_team_name'))
        away_team_name = get_correct_team_name(fixture.get('away_team_name'))
        summary = f'{home_team_name} vs. {away_team_name}'
        result = None
        if start_date + timedelta(days=1) < datetime.now(timezone.utc):
            if fixture.get('match_status') == 'finalWhistle' and fixture.get('result'):
                home_team_goals = fixture.get('home_team_goals', 0)
                away_team_goals = fixture.get('away_team_goals', 0)
                home_team_penalty_goals = fixture.get('home_team_penalty_goals', 0)
                away_team_penalty_goals = fixture.get('away_team_penalty_goals', 0)
                if home_team_penalty_goals > 0 or away_team_penalty_goals > 0 and home_team_goals == away_team_goals:
                    if home_team_penalty_goals > away_team_penalty_goals:
                        summary = summary.replace(home_team_name, f'{home_team_name}*')
                    else:
                        summary = summary.replace(away_team_name, f'{away_team_name}*')
                    result = f'{home_team_name} {home_team_goals} (penalties: {home_team_penalty_goals}) - {away_team_name} {away_team_goals} (penalties: {away_team_penalty_goals})'
                else:
                    if home_team_goals > away_team_goals:
                        summary = summary.replace(home_team_name, f'{home_team_name}*')
                    elif away_team_goals > home_team_goals:
                        summary = summary.replace(away_team_name, f'{away_team_name}*')
                    else:
                        summary = f'{home_team_name}* vs. {away_team_name}*'
                    result = f'{home_team_name} {home_team_goals} - {away_team_name} {away_team_goals}'
            else:
                summary += ' (result unknown)'
                result = f'{home_team_name} ??? - {away_team_name} ???'

        venue = get_correct_venue_name(fixture.get('stadium_name'), fixture.get('stadium_city'))
        description = f'{competition}\n\n{result}' if result else f'{competition}\n\n{summary}'
        return FootballCalendarEvent(
            match_id=fixture['match_id'],  # NOTE: want KeyError to be thrown if this doesn't exist
            summary=summary,
            location=venue,
            start_date=start_date,
            end_date=get_end_datetime(start_date, 2),
            competition=competition,
            description=description
        )

    def to_event(self) -> Event:
        # https://icalendar.org/iCalendar-RFC-5545/3-6-1-event-component.html
        event = Event()
        # Part of spec
        event.add('uid', self.match_id)
        event.add('dtstamp', self.start_date)
        event.add('dtstart', self.start_date)
        event.add('dtend', self.end_date)
        event.add('summary', self.summary)
        event.add('description', self.description)
        if self.location:
            event.add('location', self.location)
        # Custom fields example (if want to add in future)
        # event.add('x-jeffsoftware-competition', self.competition)
        return event


@dataclass()
class FootballCalendar:
    team_name: str
    seasons: str
    events: List[FootballCalendarEvent]
    cal: Calendar | None = field(init=False)
    cal_bytes: bytes | None = field(init=False)

    def __post_init__(self):
        self.cal = None
        self.cal_bytes = None

    @staticmethod
    def to_football_calendar(team_name: str, seasons: str, events: List[FootballCalendarEvent]):
        return FootballCalendar(
            team_name=team_name,
            seasons=seasons,
            events=events
        )

    def to_calendar(self) -> Calendar:
        if self.cal is None:
            team_name_modified = self.team_name.replace('.', '').replace(' ', '').replace('\n', '').lower()
            cal = Calendar()
            # https://en.wikipedia.org/wiki/ICalendar
            cal.add('X-WR-CALNAME', self.team_name)
            cal.add('X-WR-CALDESC', f'All {self.team_name} fixtures for {self.seasons} season')
            cal.add('X-WR-RELCALID', f'{team_name_modified}-{self.seasons}'.replace(' ', ''))
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
