#!/usr/bin/env bash
# Desk helper (WSL2/Linux, ADR 0014): regenerate randomTrips.py demand
# against the current cities/sjc/network/sjc.net.xml and open sumo-gui.
# No domain logic here (ADR 0002) -- just the two commands from
# docs/local/sjc-quickstart.md step 5, wired to CLI args.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: scripts/linux/run-sjc-sim.sh [duration_seconds] [period_seconds]

  duration_seconds  simulated time to generate traffic for (randomTrips.py -e; default 3600)
  period_seconds    seconds between vehicle insertions -- LOWER means MORE
                     traffic (randomTrips.py -p; default 2)

Example: scripts/linux/run-sjc-sim.sh 1800 1   # 30 simulated min, ~1 vehicle/s
EOF
  exit 1
}

[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && usage

DURATION="${1:-3600}"
PERIOD="${2:-2}"

if ! [[ "$DURATION" =~ ^[0-9]+$ ]] || ! [[ "$PERIOD" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  usage
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

NET=cities/sjc/network/sjc.net.xml
ROU=cities/sjc/network/sjc-random.rou.xml
TRIPS=cities/sjc/network/sjc-random.trips.xml

if [[ ! -f "$NET" ]]; then
  echo "error: $NET not found -- build it first (arteria network build --city sjc)" >&2
  exit 1
fi

echo "Regenerating demand: ${DURATION}s simulated, ${PERIOD}s between vehicle insertions..."
python "$SUMO_HOME/tools/randomTrips.py" -n "$NET" -r "$ROU" -o "$TRIPS" -e "$DURATION" -p "$PERIOD"

echo "Launching sumo-gui..."
exec sumo-gui -n "$NET" -r "$ROU"
