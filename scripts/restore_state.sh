#!/usr/bin/env bash
# Vraca stanje iz orphan grane `state` u ./_state (ako grana postoji).
set -euo pipefail
mkdir -p _state
if git ls-remote --exit-code --heads origin state >/dev/null 2>&1; then
  git fetch -q --depth=1 origin state
  git archive FETCH_HEAD | tar -x -C _state
  echo "stanje vraceno ($(ls _state | wc -l) stavki)"
else
  echo "grana state ne postoji, krece prazno stanje"
fi
