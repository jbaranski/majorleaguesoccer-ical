#!/usr/bin/env bash
# Common Bash utilities. Source this from a script that already has the mandatory header
# from the shell-bash skill (strict mode, IFS, SCRIPT_DIR):
#
#   source "${SCRIPT_DIR}/common-utils.sh"
#
# This file is a library: it defines functions only. It does not set shell options, traps,
# or globals, so it never overrides the caller's strict mode, cleanup trap, or SCRIPT_DIR.

# Colors only when stdout is a terminal
if [[ -t 1 ]]; then
  CU_RED='\033[0;31m' CU_GREEN='\033[0;32m' CU_YELLOW='\033[0;33m'
  CU_BLUE='\033[0;34m' CU_CYAN='\033[0;36m' CU_NC='\033[0m'
else
  CU_RED='' CU_GREEN='' CU_YELLOW='' CU_BLUE='' CU_CYAN='' CU_NC=''
fi

# --- Output ---------------------------------------------------------------

print_info()    { printf '%b %s\n' "${CU_BLUE}i${CU_NC}" "$*"; }
print_success() { printf '%b %s\n' "${CU_GREEN}ok${CU_NC}" "$*"; }
print_warning() { printf '%b %s\n' "${CU_YELLOW}warn${CU_NC}" "$*" >&2; }
print_error()   { printf '%b %s\n' "${CU_RED}error${CU_NC}" "$*" >&2; }
print_step()    { printf '%b %s\n' "${CU_CYAN}->${CU_NC}" "$*"; }

die() {
  print_error "$@"
  exit 1
}

# --- Checks ---------------------------------------------------------------

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

require_command() {
  local cmd="$1"
  local hint="${2:-Please install ${cmd}}"
  command_exists "$cmd" || die "${cmd} is required. ${hint}"
}

is_root() {
  [[ "$EUID" -eq 0 ]]
}

require_root() {
  is_root || die "This script must be run as root"
}

require_env() {
  local var="$1"
  [[ -n "${!var:-}" ]] || die "Environment variable ${var} is required"
}

# --- User interaction -----------------------------------------------------

# confirm "Question?" [y|n]  — default answer is the second argument (y)
confirm() {
  local question="${1:-Continue?}"
  local default="${2:-y}"
  local response
  if [[ "$default" == "y" ]]; then
    read -rp "${question} [Y/n] " response
    [[ -z "$response" || "$response" =~ ^[Yy] ]]
  else
    read -rp "${question} [y/N] " response
    [[ "$response" =~ ^[Yy] ]]
  fi
}

# prompt "Question" [default] — prints the answer
prompt() {
  local question="$1"
  local default="${2:-}"
  local result
  if [[ -n "$default" ]]; then
    read -rp "${question} [${default}]: " result
    printf '%s\n' "${result:-$default}"
  else
    read -rp "${question}: " result
    printf '%s\n' "$result"
  fi
}

# select_option "Prompt" opt1 opt2 ... — prints the chosen option
select_option() {
  local question="$1"
  shift
  local opt
  PS3="${question} "
  select opt in "$@"; do
    if [[ -n "$opt" ]]; then
      printf '%s\n' "$opt"
      break
    fi
  done
}

# --- Files ----------------------------------------------------------------

ensure_dir() {
  [[ -d "$1" ]] || mkdir -p "$1"
}

backup_file() {
  local file="$1"
  local backup
  backup="${file}.bak.$(date +%Y%m%d_%H%M%S)"
  if [[ -f "$file" ]]; then
    cp -p "$file" "$backup"
    print_info "Backed up ${file} to ${backup}"
  fi
}

# safe_write FILE CONTENT — atomic replace via a temp file in the same directory
safe_write() {
  local file="$1"
  local content="$2"
  local tmp
  tmp="$(mktemp "${file}.XXXXXX")"
  printf '%s\n' "$content" >"$tmp"
  mv "$tmp" "$file"
}

# --- Strings --------------------------------------------------------------

trim() {
  local var="$*"
  var="${var#"${var%%[![:space:]]*}"}"
  var="${var%"${var##*[![:space:]]}"}"
  printf '%s' "$var"
}

# tr rather than ${1,,} so this also works on macOS's bash 3.2
lowercase() { printf '%s\n' "$1" | tr '[:upper:]' '[:lower:]'; }
uppercase() { printf '%s\n' "$1" | tr '[:lower:]' '[:upper:]'; }

# --- Time -----------------------------------------------------------------

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# --- Networking -----------------------------------------------------------

# wait_for_port HOST PORT [TIMEOUT_SECONDS]
wait_for_port() {
  local host="$1"
  local port="$2"
  local timeout="${3:-30}"
  local start
  start="$(date +%s)"
  print_step "Waiting for ${host}:${port}..."
  until nc -z "$host" "$port" 2>/dev/null; do
    if (($(date +%s) - start > timeout)); then
      die "Timeout waiting for ${host}:${port}"
    fi
    sleep 1
  done
  print_success "${host}:${port} is available"
}

get_public_ip() {
  curl -fsS https://ifconfig.me || curl -fsS https://api.ipify.org
}

# --- JSON (requires jq) ---------------------------------------------------

# json_get JSON FILTER
json_get() {
  printf '%s' "$1" | jq -r "$2"
}

# --- Retry ----------------------------------------------------------------

# retry MAX_ATTEMPTS INITIAL_DELAY_SECONDS command [args...] — exponential backoff
retry() {
  local max_attempts="$1"
  local delay="$2"
  shift 2
  local attempt
  for ((attempt = 1; attempt <= max_attempts; attempt++)); do
    if "$@"; then
      return 0
    fi
    if ((attempt < max_attempts)); then
      print_warning "Attempt ${attempt} failed, retrying in ${delay}s..."
      sleep "$delay"
      delay=$((delay * 2))
    fi
  done
  print_error "Command failed after ${max_attempts} attempts: $*"
  return 1
}
