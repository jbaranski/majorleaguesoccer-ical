---
name: shell-bash
description: Defensive Bash scripting conventions — mandatory strict-mode header, trap cleanup, long-option argument parsing, logging helpers, main guard, and common quoting/subshell mistakes. Use when writing, editing, or reviewing any shell script, or when a Makefile, CI step, or automation task needs non-trivial shell.
---

# Shell & Bash Scripting

## Mandatory Script Header

Every script must start with this exact header. No exceptions.

```bash
#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
```

- `set -e` — exit on error
- `set -u` — error on undefined variables (catches typos like `$HOMR`)
- `set -o pipefail` — pipe failures propagate (without this `false | true` exits 0)
- `IFS=$'\n\t'` — prevent word splitting on spaces
- `BASH_SOURCE[0]` — correct script dir even when sourced or called via symlink

## Trap Cleanup

Always register cleanup for temp files:

```bash
TEMP_FILE=""

cleanup() {
  local exit_code=$?
  [[ -n "$TEMP_FILE" ]] && rm -f "$TEMP_FILE"
  exit "$exit_code"
}
trap cleanup EXIT
```

## Argument Parsing

Use manual parsing — `getopts` doesn't support long options:

```bash
VERBOSE=false
DRY_RUN=false

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -v|--verbose) VERBOSE=true; shift ;;
      -n|--dry-run) DRY_RUN=true; shift ;;
      -h|--help)    usage; exit 0 ;;
      --)           shift; break ;;
      -*)           die "Unknown option: $1" ;;
      *)            break ;;
    esac
  done
  SOURCE="${1:-}"
  DEST="${2:-}"
}
```

## Conventions

- Use `[[ ]]`, never `[ ]`; use `(( ))` for arithmetic.
- Iterate arrays with `"${arr[@]}"`, never `${arr[*]}`.
- Declare every function variable `local`.
- Send errors to stderr and exit non-zero:

```bash
die() {
  echo "ERROR: $*" >&2
  exit 1
}
```

## Reading Files and Command Output

```bash
# Read file line by line — NEVER do: for line in $(cat file)
while IFS= read -r line; do
  echo "$line"
done < "$file"

# Process command output (process substitution keeps vars in scope)
while IFS= read -r entry; do
  process "$entry"
done < <(find . -name "*.txt")

# Read into array
mapfile -t lines < "$file"   # bash 4+; macOS /bin/bash is 3.2, so use a while-read loop there
```

## Common Mistakes to Avoid

```bash
# WRONG — word splits on spaces, breaks on filenames with spaces
for f in $(ls *.txt); do ...

# RIGHT
for f in *.txt; do ...

# WRONG — loses pipe exit status
cmd | grep pattern
if [[ $? -eq 0 ]]; then ...

# RIGHT — check inline
if cmd | grep -q pattern; then ...

# WRONG — subshell; VAR is lost after loop
find . -name "*.txt" | while read -r f; do
  VAR="$f"
done
echo "$VAR"  # empty!

# RIGHT — process substitution
while IFS= read -r f; do
  VAR="$f"
done < <(find . -name "*.txt")
echo "$VAR"  # works

# WRONG — unquoted, breaks on spaces/globs
cp $file $dest

# RIGHT
cp "$file" "$dest"
```

## Logging Pattern

```bash
log()   { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] ${*:2}"; }
info()  { log INFO "$@"; }
warn()  { log WARN "$@" >&2; }
error() { log ERROR "$@" >&2; }
debug() { [[ "${VERBOSE:-false}" == true ]] && log DEBUG "$@" || true; }
```

## Main Guard

Always guard execution so the script can be sourced for testing:

```bash
main() {
  parse_args "$@"
  # ...
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
```
