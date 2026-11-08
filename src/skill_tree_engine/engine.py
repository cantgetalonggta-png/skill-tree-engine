from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .builder import build_tree_from_knowledge
from .models import SkillNode, SkillTree


class SkillTreeEngine:
    """Runtime engine: load KB → tree → query/search/verify/export."""

    def __init__(self, tree: Optional[SkillTree] = None):
        self.tree = tree

    @classmethod
    def from_knowledge_file(cls, path: str | Path) -> "SkillTreeEngine":
        kb = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(build_tree_from_knowledge(kb))

    @classmethod
    def from_knowledge(cls, kb: Dict[str, Any]) -> "SkillTreeEngine":
        return cls(build_tree_from_knowledge(kb))

    def rebuild(self, kb: Dict[str, Any]) -> SkillTree:
        self.tree = build_tree_from_knowledge(kb)
        return self.tree

    def get(self, node_id: str) -> Optional[SkillNode]:
        assert self.tree
        return self.tree.nodes.get(node_id)

    def search(self, query: str, limit: int = 25) -> List[SkillNode]:
        assert self.tree
        q = query.lower().strip()
        hits = []
        for n in self.tree.nodes.values():
            if n.kind in {"root", "category"}:
                continue
            blob = f"{n.name} {n.description} {' '.join(n.tags)} {n.category}".lower()
            if q in blob:
                hits.append(n)
        hits.sort(key=lambda n: (-n.score, n.name.lower()))
        return hits[:limit]

    def by_category(self, category: str) -> List[SkillNode]:
        assert self.tree
        ids = self.tree.categories.get(category, [])
        return [self.tree.nodes[i] for i in ids if i in self.tree.nodes]

    def verify(self) -> Dict[str, Any]:
        assert self.tree
        missing_parents = []
        orphan_edges = []
        for n in self.tree.nodes.values():
            if n.parent_id and n.parent_id not in self.tree.nodes:
                missing_parents.append(n.id)
            for c in n.children:
                if c not in self.tree.nodes:
                    orphan_edges.append({"parent": n.id, "child": c})
        for e in self.tree.edges:
            if e["from"] not in self.tree.nodes or e["to"] not in self.tree.nodes:
                orphan_edges.append(e)
        ok = not missing_parents and not orphan_edges
        return {
            "ok": ok,
            "stats": self.tree.stats,
            "missing_parents": missing_parents,
            "orphan_edges": orphan_edges[:20],
            "categories": sorted(self.tree.categories.keys()),
        }

    def export_json(self, path: str | Path) -> Path:
        assert self.tree
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.tree.to_dict(), indent=2), encoding="utf-8")
        return p

    def export_compact(self) -> Dict[str, Any]:
        assert self.tree
        # UI-friendly compact graph
        nodes = []
        for n in self.tree.nodes.values():
            nodes.append(
                {
                    "id": n.id,
                    "name": n.name,
                    "kind": n.kind,
                    "category": n.category,
                    "depth": n.depth,
                    "parent": n.parent_id,
                    "score": n.score,
                    "tags": n.tags[:6],
                    "description": n.description[:180],
                    "children_count": len(n.children),
                    "prerequisites": n.prerequisites[:5],
                    "unlocks": n.unlocks[:5],
                }
            )
        return {
            "generated_at": self.tree.generated_at,
            "product": self.tree.product,
            "stats": self.tree.stats,
            "categories": self.tree.categories,
            "nodes": nodes,
            "edges": self.tree.edges,
        }
