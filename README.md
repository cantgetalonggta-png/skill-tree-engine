# Skill Tree Engine

Hierarchical skill-tree runtime over EXTRACT distilled `knowledge.json`.

## Quick start

```bash
export PYTHONPATH=src
python3 -m skill_tree_engine.cli \
  --knowledge ../extract-project/kb/knowledge.json \
  --out web/data/tree.json \
  --compact-out web/data/tree-compact.json \
  --verify

python3 -m pytest tests -q
python3 -m http.server 8090 --directory web
# open http://127.0.0.1:8090/
```

## API

```bash
STE_KNOWLEDGE=../extract-project/kb/knowledge.json \
STE_WEB=./web \
PYTHONPATH=src python3 -m uvicorn skill_tree_engine.api:app --port 8090
```

Endpoints: `/health`, `/v1/tree`, `/v1/search?q=`, `/v1/category/{name}`, `/v1/node/{id}`, `/v1/rebuild`
