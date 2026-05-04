# Notebook Outline

Use this as the default shape when the user wants a replay notebook.

## Default Section Order

1. Title and reproduction target
2. Scope, stop point, and success criterion
3. Imports and user-editable config
4. Artifact, checkpoint, and metadata resolution
5. Source-code map
6. Stepwise replay cells
7. Mismatch checks or invariants
8. Optional expensive or full-eval cell

## Markdown Template For A Section

````markdown
## Step N - Build Block Graphs

CLI reproducer:

```bash
cd /path/to/project
source scripts/job_common.sh
activate_project_env

python entrypoint.py \
  --flag value \
  --section-specific-mode
```

Goal:
Recreate the graph-building step used before merge evaluation.

Source:
- `nino-autoenc/eval_autoenc.py`, `evaluate_single_model`
- `nino-autoenc/ninoae/graph_utils.py`, `build_graphs_for_blocks`

Checks:
- `n_blocks` matches the eval backbone
- graph class matches the family adapter
- notebook overrides are explicit

Notebook-only deviation:
- build graphs blockwise to reduce memory
````

## Recommended Cell Types

- one top config cell
- one cell to inspect source metadata or args
- one cell to reconstruct a specific intermediate
- one cell to assert or compare expectations
- one optional heavy cell for the next stage

## Useful Stop Points

- after config inheritance
- after graph construction
- after AE forward
- after vector reconstruction
- after final evaluation

## When To Ask The User Before Continuing

- multiple plausible entrypoints exist
- the target claim or metric is unclear
- the stopping point is ambiguous
- the notebook could be either a replay or a discrepancy audit
- the notebook would otherwise hardcode a questionable assumption
