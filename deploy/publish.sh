#!/usr/bin/env bash
# Run by hand on a home PC after a race (Sunday evening): process the latest race, then commit and
# push data/. Coolify rebuilds the site on the push.
#
# Needs: uv, git with push access, a residential connection (live timing refuses datacenter IPs).
set -euo pipefail

cd "$(dirname "$0")/.."
SEASON="${SEASON:-$(date +%Y)}"

uv run python -m pipeline run --season "$SEASON" --latest

git add data
if git diff --cached --quiet -- data; then
	echo "no new data, nothing to publish"
	exit 0
fi
git commit -m "Data: $SEASON, latest race" -- data
git push
