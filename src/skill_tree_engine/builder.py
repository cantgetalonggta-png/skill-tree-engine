from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from .classifier import classify, depth_for_kind, tags_from_text
from .models import SkillNode, SkillTree


def build_tree_from_knowledge(kb: Dict[str, Any]) -> SkillTree:
    product = kb.get("product") or {"name": "Skill Tree", "tagline": ""}
    root_id = "root"
    nodes: Dict[str, SkillNode] = {}
    edges: List[Dict[str, str]] = []
    categories: Dict[str, List[str]] = defaultdict(list)

    root = SkillNode(
        id=root_id,
        name=product.get("name") or "Skill Distillery",
        kind="root",
        description=product.get("tagline") or "Root of skill tree",
        category="root",
        depth=0,
    )
    nodes[root_id] = root

    # category hubs
    cat_ids = {}
    skills = kb.get("skills") or []
    docs = kb.get("docs") or []

    # provisional classify to know categories
    for s in skills:
        cat = classify(s.get("name", ""), s.get("description", ""), s.get("path", ""), s.get("kind", ""))
        s["_cat"] = cat
        cat_ids.setdefault(cat, f"cat:{cat}")

    for cat, cid in sorted(cat_ids.items()):
        node = SkillNode(
            id=cid,
            name=cat.replace("_", " ").title(),
            kind="category",
            description=f"Category hub: {cat}",
            category=cat,
            depth=1,
            parent_id=root_id,
        )
        nodes[cid] = node
        nodes[root_id].children.append(cid)
        edges.append({"from": root_id, "to": cid, "type": "contains"})
        categories[cat] = []

    def add_skill(s: Dict[str, Any], kind_default: str = "skill") -> None:
        sid = str(s.get("id") or s.get("name"))
        if sid in nodes:
            return
        cat = s.get("_cat") or classify(
            s.get("name", ""), s.get("description", ""), s.get("path", ""), s.get("kind", "")
        )
        parent = cat_ids.get(cat, root_id)
        node = SkillNode(
            id=sid,
            name=s.get("name") or sid,
            kind=s.get("kind") or kind_default,
            description=(s.get("description") or "")[:500],
            path=s.get("path") or "",
            policies=list(s.get("policies") or []),
            tests=list(s.get("tests") or []),
            scope=str(s.get("scope") or ""),
            category=cat,
            depth=depth_for_kind(s.get("kind") or kind_default, cat),
            parent_id=parent,
            tags=tags_from_text(s.get("name", ""), s.get("description", "")),
            score=float(len(s.get("policies") or []) + len(s.get("tests") or []) + min(5, len((s.get("description") or "")) // 80)),
            meta={"preview": (s.get("preview") or "")[:200]} if s.get("preview") else {},
        )
        nodes[sid] = node
        nodes[parent].children.append(sid)
        categories[cat].append(sid)
        edges.append({"from": parent, "to": sid, "type": "contains"})

        # prerequisite edges: skills with policies unlock tested skills of same cat lightly
        if node.tests and node.policies:
            # self-contained advanced node
            pass

    for s in skills:
        add_skill(s, "skill")

    for d in docs:
        d = dict(d)
        d["_cat"] = classify(d.get("name", ""), d.get("description", ""), d.get("path", ""), "doc")
        cat_ids.setdefault(d["_cat"], f"cat:{d['_cat']}")
        if d["_cat"] not in nodes:
            cid = cat_ids[d["_cat"]]
            if cid not in nodes:
                nodes[cid] = SkillNode(
                    id=cid,
                    name=d["_cat"].replace("_", " ").title(),
                    kind="category",
                    description=f"Category hub: {d['_cat']}",
                    category=d["_cat"],
                    depth=1,
                    parent_id=root_id,
                )
                nodes[root_id].children.append(cid)
                edges.append({"from": root_id, "to": cid, "type": "contains"})
                categories[d["_cat"]] = categories.get(d["_cat"], [])
        add_skill({**d, "kind": d.get("kind") or "doc"}, "doc")

    # simple unlock chains: within category, sort by score and link sequential prereqs
    for cat, ids in categories.items():
        ranked = sorted(ids, key=lambda i: nodes[i].score, reverse=True)
        for i in range(1, min(len(ranked), 40)):
            prev, cur = ranked[i - 1], ranked[i]
            if cur not in nodes[prev].unlocks:
                nodes[prev].unlocks.append(cur)
            if prev not in nodes[cur].prerequisites:
                nodes[cur].prerequisites.append(prev)
            edges.append({"from": prev, "to": cur, "type": "unlocks"})

    stats = {
        "nodes": len(nodes),
        "skills": sum(1 for n in nodes.values() if n.kind == "skill"),
        "docs": sum(1 for n in nodes.values() if n.kind == "doc"),
        "categories": sum(1 for n in nodes.values() if n.kind == "category"),
        "edges": len(edges),
        "source_skills": len(skills),
        "source_docs": len(docs),
    }

    return SkillTree(
        root_id=root_id,
        nodes=nodes,
        categories=dict(categories),
        edges=edges,
        stats=stats,
        product=product,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
