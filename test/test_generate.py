import unittest

from src.pipeline.context import CompetitionContext, CompetitionType
from src.pipeline.steps.generate import generate_calendars

TEAMS = {"A": "Team A", "B": "Team B"}


def _fixture(match_id: str, competition_id: str) -> dict:
    return {
        "match_id": match_id,
        "competition_id": competition_id,
        "competition_name": competition_id,
        "planned_kickoff_time": "2026-11-25T01:00:00+00:00",
        "home_team_id": "A",
        "away_team_id": "B",
        "home_team_name": TEAMS["A"],
        "away_team_name": TEAMS["B"],
    }


def _master_match_ids(fixtures: list[dict], competition_type: CompetitionType, competition_id: str) -> dict:
    ctx = CompetitionContext(
        competition_id=competition_id,
        competition_type=competition_type,
        seasons=(("MLS-SEA-0001KA", "2026"),),
        included_competition_ids=frozenset(),
        output_root=".",
        provider=None,
        teams=TEAMS,
        fixtures=fixtures,
    )
    calendars = generate_calendars(ctx).calendars
    return {c.team_name: {e.match_id for e in c.events} for c in calendars if c.is_competition_calendar}


class GenerateMasterCalendarsTest(unittest.TestCase):
    def test_league_fixtures_fan_out_to_every_mapped_master_calendar(self) -> None:
        fixtures = [
            _fixture("regular", "MLS-COM-000001"),
            _fixture("playoff", "MLS-COM-000002"),
            _fixture("unmapped", "MLS-COM-000032"),
        ]
        masters = _master_match_ids(fixtures, CompetitionType.LEAGUE, "MLS-COM-000001")
        self.assertEqual(masters, {"mls": {"regular", "playoff"}, "mlsplayoffs": {"playoff"}})

    def test_international_master_calendar_uses_mapped_filename(self) -> None:
        fixtures = [_fixture("wc", "MLS-COM-000035")]
        masters = _master_match_ids(fixtures, CompetitionType.INTERNATIONAL, "MLS-COM-000035")
        self.assertEqual(masters, {"worldcup": {"wc"}})


if __name__ == "__main__":
    unittest.main()
