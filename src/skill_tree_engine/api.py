from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from skill_tree_engine.engine import SkillTreeEngine

KB = Path(os.environ.get("STE_KNOWLEDGE", "/workspace/artifacts/extract-project/kb/knowledge.json"))
WEB = Path(os.environ.get("STE_WEB", str(Path(__file__).resolve().parents[2] / "web")))

app = FastAPI(title="Skill Tree Engine", version="1.0.0")
_engine: SkillTreeEngine | None = None


def get_engine() -> SkillTreeEngine:
    global _engine
    if _engine is None:
        if not KB.exists():
            raise RuntimeError(f"knowledge missing: {KB}")
        _engine = SkillTreeEngine.from_knowledge_file(KB)
    return _engine


@app.on_event("startup")
def _startup():
    get_engine()


@app.get("/health")
def health():
    eng = get_engine()
    return {"status": "ok", "verify": eng.verify()}


@app.get("/v1/tree")
def tree(compact: bool = True):
    eng = get_engine()
    return eng.export_compact() if compact else eng.tree.to_dict()


@app.get("/v1/search")
def search(q: str = Query(..., min_length=1), limit: int = 25):
    eng = get_engine()
    hits = eng.search(q, limit=limit)
    return {
        "q": q,
        "count": len(hits),
        "results": [
            {
                "id": h.id,
                "name": h.name,
                "category": h.category,
                "score": h.score,
                "description": h.description,
                "tags": h.tags,
            }
            for h in hits
        ],
    }


@app.get("/v1/category/{name}")
def category(name: str):
    eng = get_engine()
    nodes = eng.by_category(name)
    if not nodes and name not in (eng.tree.categories if eng.tree else {}):
        raise HTTPException(404, f"unknown category {name}")
    return {
        "category": name,
        "count": len(nodes),
        "nodes": [{"id": n.id, "name": n.name, "score": n.score, "kind": n.kind} for n in nodes],
    }


@app.get("/v1/node/{node_id}")
def node(node_id: str):
    eng = get_engine()
    n = eng.get(node_id)
    if not n:
        raise HTTPException(404, "node not found")
    return n.to_dict()


@app.post("/v1/rebuild")
def rebuild():
    global _engine
    _engine = SkillTreeEngine.from_knowledge_file(KB)
    path = WEB / "data" / "tree-compact.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(__import__("json").dumps(_engine.export_compact(), indent=2))
    return {"ok": True, "verify": _engine.verify(), "wrote": str(path)}


if WEB.exists():
    app.mount("/", StaticFiles(directory=str(WEB), html=True), name="web")


def run():
    import uvicorn

    uvicorn.run("skill_tree_engine.api:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8090")))


if __name__ == "__main__":
    run()
