import json
from pathlib import Path

from skill_tree_engine.engine import SkillTreeEngine
from skill_tree_engine.builder import build_tree_from_knowledge


def sample_kb():
    return {
        "product": {"name": "Test Distillery", "tagline": "unit"},
        "skills": [
            {
                "id": "s1",
                "name": "PDF Extractor",
                "kind": "skill",
                "description": "extract text from pdf documents",
                "path": "skills/pdf.md",
                "policies": ["safe"],
                "tests": ["t1"],
                "scope": "ingest",
            },
            {
                "id": "s2",
                "name": "Hybrid Search",
                "kind": "skill",
                "description": "bm25 vector hybrid search",
                "path": "skills/search.md",
                "policies": [],
                "tests": [],
                "scope": "search",
            },
            {
                "id": "s3",
                "name": "Billing Governance Guardrail",
                "kind": "skill",
                "description": "HITL billing governance policy",
                "path": "skills/gov.md",
                "policies": ["hitl"],
                "tests": ["g1"],
                "scope": "security",
            },
        ],
        "docs": [
            {
                "id": "d1",
                "name": "Android Manifest Notes",
                "description": "smali apk package analysis notes",
                "kind": "doc",
                "path": "docs/a.md",
            }
        ],
    }


def test_build_and_verify():
    tree = build_tree_from_knowledge(sample_kb())
    eng = SkillTreeEngine(tree)
    v = eng.verify()
    assert v["ok"] is True
    assert tree.stats["skills"] == 3
    assert tree.stats["docs"] == 1
    assert "ingestion" in tree.categories or "search" in tree.categories or "security" in tree.categories


def test_search():
    eng = SkillTreeEngine.from_knowledge(sample_kb())
    hits = eng.search("hybrid")
    assert any(h.id == "s2" for h in hits)


def test_export(tmp_path: Path):
    eng = SkillTreeEngine.from_knowledge(sample_kb())
    out = eng.export_json(tmp_path / "tree.json")
    data = json.loads(out.read_text())
    assert "nodes" in data and "root" in data["nodes"]
