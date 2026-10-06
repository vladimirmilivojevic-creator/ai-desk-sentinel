#!/usr/bin/env bash
# Dogadjaji N2+ (events/) i dnevni log (log/) idu na main. Samo ovaj workflow pise u te direktorijume.
set -euo pipefail
git config user.name "sentinel-bot"
git config user.email "sentinel-bot@users.noreply.github.com"
for d in events log; do
  if [ -d "$d" ]; then git add "$d"; fi
done
if git diff --cached --quiet; then
  echo "nema novih dogadjaja ili logova"
  exit 0
fi
git commit -q -m "events/log $(date -u +%Y-%m-%dT%H:%M:%SZ)"
for i in 1 2 3; do
  git pull -q --rebase origin main && git push -q origin HEAD:main && { echo "objavljeno"; exit 0; }
  sleep $((RANDOM % 5 + 2))
done
echo "push na main nije uspeo"
exit 1
