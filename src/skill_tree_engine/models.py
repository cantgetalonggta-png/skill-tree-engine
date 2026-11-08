from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class SkillNode:
    id: str
    name: str
    kind: str = "skill"
    description: str = ""
    path: str = ""
    policies: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    scope: str = ""
    category: str = "general"
    depth: int = 0
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    unlocks: List[str] = field(default_factory=list)
    score: float = 0.0
    tags: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SkillTree:
    root_id: str
    nodes: Dict[str, SkillNode]
    categories: Dict[str, List[str]]
    edges: List[Dict[str, str]]
    stats: Dict[str, Any]
    product: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_id": self.root_id,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "categories": self.categories,
            "edges": self.edges,
            "stats": self.stats,
            "product": self.product,
            "generated_at": self.generated_at,
        }

    def subtree(self, node_id: str) -> List[str]:
        out: List[str] = []
        stack = [node_id]
        seen = set()
        while stack:
            cur = stack.pop()
            if cur in seen or cur not in self.nodes:
                continue
            seen.add(cur)
            out.append(cur)
            stack.extend(self.nodes[cur].children)
        return out
