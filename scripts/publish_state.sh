#!/usr/bin/env bash
# Jedan force-push commit po krugu na granu `state` (istorija ne raste).
# Token se nikad ne stampa; nema `set -x`.
set -euo pipefail
cd _state
rm -rf .git
git init -q -b state
git config user.name "sentinel-bot"
git config user.email "sentinel-bot@users.noreply.github.com"
git add -A
git commit -q -m "state $(date -u +%Y-%m-%dT%H:%M:%SZ)"
URL="${PUSH_URL:-https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git}"
git push -q --force "$URL" HEAD:refs/heads/state
echo "stanje objavljeno"
