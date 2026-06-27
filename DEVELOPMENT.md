# Development Guide

This guide covers how to set up and run the Python code in the `src/` directory locally.

## Prerequisites

- Python 3.13 or higher
- pip or pipenv for package management

## Environment Setup

1. Install pipenv if you don't have it:
```bash
pip install pipenv
```

2. Create the virtual environment and install dependencies (including dev dependencies):
```bash
pipenv install -d
```

3. Activate the virtual environment:
```bash
pipenv shell
```

## Environment Variables

The following environment variables are required to run the application:

### Required Variables

- **SEASONS**: Comma-separated list of season ID and year pairs in the format `season_id:season_year,season_id:season_year`
  - Example: `MLS-SEA-0001KA:2026,MLS-SEA-0001K9:2025`
  - This tells the app which MLS season(s) to fetch data for
  - Determine season dates by `curl -X GET https://stats-api.mlssoccer.com/competitions/MLS-COM-000001/seasons | jq .`

- **LEAGUE**: The league ID for the MLS API
  - Determine league IDs by `curl -X GET  https://stats-api.mlssoccer.com/competitions  | jq .`
  - It's `MLS-COM-000001`

- **OUTPUT_ROOT**: The root directory where generated calendar files will be saved
  - Example: `/Users/user/development/majorleaguesoccer-ical` or `.` for current directory
  - Calendar files will be created in `{OUTPUT_ROOT}/calendars/`

### Optional Variables

- **LOG_LEVEL**: Set to `DEBUG` for verbose logging, otherwise defaults to `INFO`
  - Example: `DEBUG` or `INFO`

- **NUM_TEAMS_EXPECTED**: Expected number of teams in the league (defaults to 30)
  - Example: `30`

- **MLS_EXCLUDED_COMPETITIONS**: Comma-separated list of competition IDs to exclude from the main league calendar
  - Use `MLS-COM-000003,MLS-COM-000004,MLS-COM-000005,MLS-COM-00002X,MLS-COM-00002R`
  - These are non-MLS competitions (e.g. US Open Cup, Leagues Cup) that appear in the fixture feed but should not be in league calendars
  - `curl -X GET  https://stats-api.mlssoccer.com/competitions  | jq .` to see what they mean
  - Note: This was previously called `EXCLUDED_COMPETITIONS`

- **INTERNATIONAL_COMPETITIONS**: Comma-separated list of competition IDs for which separate international calendars should be generated
  - Example: `MLS-COM-00002W,MLS-COM-00002Z,MLS-COM-000030,MLS-COM-000035`
  - Each competition ID listed here will produce its own set of per-team `.ics` files plus a master competition `.ics`
  - These competitions are also automatically excluded from the main league calendar
  - To find competition IDs: `curl -X GET https://stats-api.mlssoccer.com/competitions | jq .`

### Setting Environment Variables

You can set environment variables either by exporting them in your shell session or by passing them inline when running the application.

#### Using export (Linux/macOS)

```bash
export SEASONS="MLS-SEA-0001KA:2026,MLS-SEA-0001K9:2025"
export LEAGUE="MLS-COM-000001"
export OUTPUT_ROOT="."
export LOG_LEVEL="DEBUG"
export NUM_TEAMS_EXPECTED="30"
export MLS_EXCLUDED_COMPETITIONS="MLS-COM-000003,MLS-COM-000004,MLS-COM-000005,MLS-COM-00002X,MLS-COM-00002R"
export INTERNATIONAL_COMPETITIONS="MLS-COM-00002W,MLS-COM-00002Z,MLS-COM-000030,MLS-COM-000035"
```

These will persist for your current shell session.

## Running the Application

### Using Python directly

```bash
python -m src.main
```

### Using pipenv

```bash
pipenv run python -m src.main
```

### With environment variables inline

```bash
SEASONS="MLS-SEA-0001KA:2026,MLS-SEA-0001K9:2025" LEAGUE="MLS-COM-000001" OUTPUT_ROOT="." LOG_LEVEL="DEBUG" NUM_TEAMS_EXPECTED="30" MLS_EXCLUDED_COMPETITIONS="MLS-COM-000003,MLS-COM-000004,MLS-COM-000005,MLS-COM-00002X,MLS-COM-00002R" INTERNATIONAL_COMPETITIONS="MLS-COM-00002W,MLS-COM-00002Z,MLS-COM-000030,MLS-COM-000035" python -m src.main
```

## Output

The application will:

1. Fetch team standings and fixtures from the MLS Stats API
2. Generate iCalendar (.ics) files for each team and each configured international competition
3. Save calendar files to `{OUTPUT_ROOT}/calendars/`
4. League calendar files are named using the team name (lowercased, spaces/punctuation removed)
   - Example: `dcunited.ics`, `intermiamicf.ics`
   - Each team also gets `_home.ics` and `_away.ics` variants
   - A master `mls.ics` contains all league fixtures deduplicated
5. International calendar files are named using the team name plus a master file named by competition
   - Example: `goldcup.ics` for CONCACAF Gold Cup

## Architecture

The application uses a pipeline/plugin architecture:

```
src/
  pipeline/
    context.py          # CompetitionContext frozen dataclass + CompetitionType enum
    steps/
      fetch_teams.py    # Fetches teams via the data provider
      fetch_fixtures.py # Fetches fixtures via the data provider
      generate.py       # Generates FootballCalendar objects
      write.py          # Writes .ics files to disk
  providers/
    base.py             # DataProvider Protocol
    mls_stats_api.py    # MLSStatsAPIProvider implementation
  football_calendar.py  # FootballCalendar + FootballCalendarEvent dataclasses
  utils.py              # Utility functions and constants
  main.py               # Thin orchestrator
```

Each pipeline step is a function `(CompetitionContext) -> CompetitionContext`. Context is immutable (`frozen=True`); steps return updated copies via `dataclasses.replace`.

## Updating Dependencies

This project uses pipenv for dependency management. The `requirements.txt` file is generated from the Pipfile and is used by the GitHub Action for CI/CD.

### Adding or updating dependencies

1. Add or update dependencies in the Pipfile using pipenv:
```bash
# Add a new production dependency
pipenv install <package-name>

# Add a new dev dependency
pipenv install -d <package-name>

# Update all dependencies
pipenv update
```

2. After modifying dependencies, regenerate `requirements.txt` for the GitHub Action:
```bash
pipenv requirements > requirements.txt
```

## Development Tips

1. Use `LOG_LEVEL=DEBUG` to see detailed logging output
2. The application validates that all required environment variables are set before running
3. Season standings must be available in the API before that season can be processed
4. Always regenerate `requirements.txt` after updating dependencies in Pipfile

## Troubleshooting

### Missing environment variables
If you see `AssertionError`, check that all required environment variables are set:
- SEASONS
- LEAGUE
- OUTPUT_ROOT

### Incorrect number of teams
Adjust `NUM_TEAMS_EXPECTED` to match the actual number of teams in the league for your season. For the 2026 season no standings are available yet, so to determine all the MLS teams we have to call and fetch the 2025 standings. We will remove that once the 2026 seasons become available.
