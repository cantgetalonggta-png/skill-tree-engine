from __future__ import annotations

import argparse
import json
from pathlib import Path

from skill_tree_engine.engine import SkillTreeEngine


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Skill Tree Engine CLI")
    p.add_argument("--knowledge", required=True, help="Path to knowledge.json")
    p.add_argument("--out", default="./web/data/tree.json", help="Export tree JSON")
    p.add_argument("--compact-out", default="./web/data/tree-compact.json")
    p.add_argument("--verify", action="store_true")
    p.add_argument("--search", default=None)
    args = p.parse_args(argv)

    eng = SkillTreeEngine.from_knowledge_file(args.knowledge)
    report = eng.verify()
    eng.export_json(args.out)
    Path(args.compact_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.compact_out).write_text(json.dumps(eng.export_compact(), indent=2), encoding="utf-8")

    print(json.dumps({"verify": report, "out": args.out, "compact": args.compact_out}, indent=2))
    if args.search:
        hits = eng.search(args.search)
        print(json.dumps([{"id": h.id, "name": h.name, "category": h.category, "score": h.score} for h in hits], indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
