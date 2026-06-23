---
name: shell-bash
description: Shell scripting and Bash programming patterns
domain: programming-languages
version: 1.0.0
tags: [bash, shell, scripting, automation, cli]
triggers:
  keywords:
    primary: [bash, shell, sh, zsh, script, terminal, cli]
    secondary: [grep, sed, awk, pipe, cron, automation, makefile]
  context_boost: [devops, linux, unix, automation, sysadmin]
  context_penalty: [web, frontend, mobile, gui]
  priority: medium
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

## Variable Expansion

```bash
# Defaults and guards
"${var:-default}"     # use default if unset or empty
"${var:=default}"     # assign default if unset or empty
"${var:?error msg}"   # abort with error if unset or empty

# String operations
"${str#prefix}"       # remove shortest prefix match
"${str##*/}"          # basename (remove longest prefix)
"${str%suffix}"       # remove shortest suffix match
"${str%/*}"           # dirname (remove last slash + rest)
"${str%%.*}"          # remove all extensions
"${str/old/new}"      # replace first match
"${str//old/new}"     # replace all matches
"${#str}"             # string length
"${str^^}"            # uppercase
"${str,,}"            # lowercase
```

## Arrays — Always Quote

```bash
declare -a items=("one" "two" "three")
items+=("four")

echo "${items[0]}"     # first element
echo "${items[-1]}"    # last element
echo "${#items[@]}"    # length
echo "${items[@]}"     # all elements — ALWAYS quote with "${arr[@]}"

# Iterate — NEVER use ${arr[*]}, always ${arr[@]}
for item in "${items[@]}"; do
  echo "$item"
done

# With index
for i in "${!items[@]}"; do
  echo "$i: ${items[$i]}"
done

# Associative arrays (bash 4+)
declare -A config=([host]="localhost" [port]="5432")
for key in "${!config[@]}"; do
  echo "$key=${config[$key]}"
done
```

## Test Operators

Use `[[` not `[`. Never use `[` — it's POSIX sh and lacks regex, `&&`/`||`, etc.

```bash
# Files
[[ -e "$path" ]]     # exists (any type)
[[ -f "$path" ]]     # regular file
[[ -d "$path" ]]     # directory
[[ -r "$path" ]]     # readable
[[ -w "$path" ]]     # writable
[[ -x "$path" ]]     # executable
[[ -s "$path" ]]     # size > 0

# Strings
[[ -z "$str" ]]      # empty
[[ -n "$str" ]]      # not empty
[[ "$a" == "$b" ]]
[[ "$a" != "$b" ]]
[[ "$str" =~ ^[0-9]+$ ]]  # regex match

# Numbers (use (( )) for arithmetic)
(( a == b ))
(( a != b ))
(( a < b ))
(( a > b ))
(( a <= b ))
(( a >= b ))
```

## Functions

Always use `local` for every variable inside a function:

```bash
# Good
process_file() {
  local file="$1"
  local result
  result=$(some_command "$file")
  echo "$result"
}

# Return status
is_valid() {
  local value="$1"
  [[ "$value" =~ ^[0-9]+$ ]]
}

if is_valid "$input"; then
  echo "ok"
fi

# Error output
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
mapfile -t lines < "$file"
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
