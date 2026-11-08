#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT/src"
KB="${STE_KNOWLEDGE:-$ROOT/../extract-project/kb/knowledge.json}"
python3 -m skill_tree_engine.cli --knowledge "$KB" --out "$ROOT/web/data/tree.json" --compact-out "$ROOT/web/data/tree-compact.json" --verify
python3 -m pytest "$ROOT/tests" -q
echo "INSTALL_OK"
