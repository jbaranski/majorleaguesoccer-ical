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
  - Example: `2026:2026` or `2025:2025,2026:2026` for multiple seasons
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

- **EXCLUDED_COMPETITIONS**: Comma-separated list of league IDs to exclude from calendars
  - Use `MLS-COM-000003,MLS-COM-000004,MLS-COM-000005,MLS-COM-00002W,MLS-COM-00002X,MLS-COM-00002R`
  - `curl -X GET  https://stats-api.mlssoccer.com/competitions  | jq .` to see what they mean

### Setting Environment Variables

You can set environment variables either by exporting them in your shell session or by passing them inline when running the application.

#### Using export (Linux/macOS)

```bash
export SEASONS="2025:2025,2026:2026"
export LEAGUE="MLS-COM-000001"
export OUTPUT_ROOT="."
export LOG_LEVEL="DEBUG"
export NUM_TEAMS_EXPECTED="30"
export EXCLUDED_COMPETITIONS="MLS-COM-000003,MLS-COM-000004,MLS-COM-000005,MLS-COM-00002W,MLS-COM-00002X,MLS-COM-00002R"
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
SEASONS="2026:2026" LEAGUE="mls" OUTPUT_ROOT="." python -m src.main
```

## Output

The application will:

1. Fetch team standings and fixtures from the MLS Stats API
2. Generate iCalendar (.ics) files for each team
3. Save calendar files to `{OUTPUT_ROOT}/calendars/`
4. Calendar files are named using the team name (lowercased, spaces removed)
   - Example: `dcunited.ics`, `intermiamicf.ics`

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
2. The `calendars/` directory must exist before running (create it manually or update OUTPUT_ROOT)
3. The application validates that all required environment variables are set before running
4. Season standings must be available in the API before that season can be processed
5. Always regenerate `requirements.txt` after updating dependencies in Pipfile

## Troubleshooting

### Missing environment variables
If you see `AssertionError`, check that all required environment variables are set:
- SEASONS
- LEAGUE
- OUTPUT_ROOT

### Calendar directory doesn't exist
Create the output directory:
```bash
mkdir -p calendars
```

### Incorrect number of teams
Adjust `NUM_TEAMS_EXPECTED` to match the actual number of teams in the league for your season.
