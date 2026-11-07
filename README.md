# Loom

A codebase agent: ask questions about a repo, trace logic across files, get answers grounded in
real code locations. Built as a learning project — one vertical slice through four layers
(application, agent, custom-trained specialist, self-hosted infrastructure) — to relearn
AI/ML engineering fundamentals by building the whole stack, not just calling an API. Fully
local, $0 cost, no deployment.

Target repo: [Celery](https://github.com/celery/celery) (~43.5k LOC), cloned locally into
`data/` — gitignored as a regenerable artifact, not part of this repo's source.


## Status

Mid-**Phase 0** (dumb-but-real baseline): repo chosen, eval questions written, AST-based
token-aware chunking built and verified (~3,150 chunks over 151 files), chunks embedded into a
768-dim local vector store. Next up: similarity search over those vectors, then the actual
agent (retrieve → prompt → frontier API), then recording the Phase 0 baseline numbers.

## Setup

```
poetry install
poetry shell
cp .env.example .env               # fill in FRONTIER_API_KEY
git clone https://github.com/celery/celery data/celery   # target repo; data/ is gitignored
```

## Run

```
poetry run python -m loom
```

Walks `data/celery/celery/`, chunks every file at function/class boundaries (token-aware, sized
to the embedding model's limit), then embeds every chunk. Produces:

- `data/chunks.jsonl` — one JSON object per chunk (`id`, `kind`, `name`, `path`, line range, text)
- `data/embeddings.npy` — a `(num_chunks, 768)` float32 matrix, row-aligned with `chunks.jsonl`

Both are full rebuilds on every run — treat them as regenerable outputs, not source. First run
downloads `all-mpnet-base-v2` (~420MB) from Hugging Face, so expect a one-time delay there.

## Layout

```
src/loom/
├── ingest/   # walk repo, chunk files                         (done)
├── index/    # embed + vector store                           (embedding done, search in progress)
├── agent/    # retrieve -> prompt -> frontier API              (not started)
├── eval/     # scoring harness against the eval question set   (not started)
├── train/    # embedding fine-tune, specialist training        (Phase 1 / Phase 2)
└── serve/    # localhost model serving                         (Phase 3)
```
