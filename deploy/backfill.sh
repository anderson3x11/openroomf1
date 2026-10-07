#!/usr/bin/env bash
# Process every race of a season already held: `deploy/backfill.sh 2025` (or a range of
# rounds: `deploy/backfill.sh 2026 1 16`). Then commit and push data/ to publish.
set -euo pipefail

REPO="${REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
SEASON="$1"
FIRST="${2:-1}"
LAST="${3:-24}"

cd "$REPO"
for round in $(seq "$FIRST" "$LAST"); do
	uv run python -m pipeline run --season "$SEASON" --round "$round" || echo "round $round failed or not held yet"
done
