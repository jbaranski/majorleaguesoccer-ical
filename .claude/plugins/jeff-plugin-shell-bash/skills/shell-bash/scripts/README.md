# Shell/Bash Scripts

`common-utils.sh` is a function library. Copy it next to your script (or copy the individual functions you need) and source it after the mandatory header from the `shell-bash` skill:

```bash
#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# shellcheck source=common-utils.sh
source "${SCRIPT_DIR}/common-utils.sh"

main() {
  require_command jq "brew install jq"
  require_env API_KEY
  print_step "Starting..."
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
```

The library only defines functions: it sets no shell options, traps or globals (other than its `CU_*` color constants), so it never overrides the caller's strict mode, cleanup trap or `SCRIPT_DIR`.

## Functions

| Area        | Functions                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------- |
| Output      | `print_info`, `print_success`, `print_step`, `print_warning`, `print_error` (last two to stderr), `die` |
| Checks      | `command_exists`, `require_command`, `is_root`, `require_root`, `require_env`                           |
| Interaction | `confirm`, `prompt`, `select_option`                                                                    |
| Files       | `ensure_dir`, `backup_file`, `safe_write` (atomic)                                                      |
| Strings     | `trim`, `lowercase`, `uppercase`                                                                        |
| Time        | `timestamp` (UTC ISO 8601)                                                                              |
| Networking  | `wait_for_port`, `get_public_ip`                                                                        |
| JSON        | `json_get` (requires `jq`)                                                                              |
| Retry       | `retry MAX_ATTEMPTS INITIAL_DELAY cmd...` (exponential backoff)                                         |
