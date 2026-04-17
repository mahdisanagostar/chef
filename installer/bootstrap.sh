#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="${1:-$ROOT}"
HOST="${2:-both}"
VAULT_MODE="${3:-new}"

PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" python3 -m chef.cli init --project "$PROJECT" --host "$HOST" --vault "$VAULT_MODE"
