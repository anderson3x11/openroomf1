#!/usr/bin/env bash
# Run by hand on a home PC after a race (Sunday evening): process the latest race, then commit and
# push data/. Coolify rebuilds the site on the push.
#
# Needs: uv, git with push access. Timing comes from OpenF1 (about 10 minutes per Grand Prix:
# its free tier allows 30 requests a minute). The race before is processed again too, about
# 20 minutes in all.
set -euo pipefail

cd "$(dirname "$0")/.."
SEASON="${SEASON:-$(date +%Y)}"

uv run python -m pipeline run --season "$SEASON" --latest
# The race before, again: OpenF1 adds its pit stop times days after the race. Not blocking.
uv run python -m pipeline run --season "$SEASON" --previous || echo "previous race not refreshed"

git add data
if git diff --cached --quiet -- data; then
	echo "no new data, nothing to publish"
	exit 0
fi
git commit -m "chore(data): update $SEASON latest race" -- data
git push
