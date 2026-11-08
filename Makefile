.PHONY: build test serve deploy-pages

KB ?= ../extract-project/kb/knowledge.json

build:
	PYTHONPATH=src python3 -m skill_tree_engine.cli --knowledge $(KB) --out web/data/tree.json --compact-out web/data/tree-compact.json --verify

test:
	PYTHONPATH=src python3 -m pytest tests -q

serve:
	python3 -m http.server 8090 --directory web
