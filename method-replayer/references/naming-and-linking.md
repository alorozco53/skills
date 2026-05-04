# Naming And Linking

## Notebook Naming

- Use `<entrypoint>_<focus>_replay.ipynb` for reproduction-first notebooks.
- Use `<entrypoint>_<focus>_audit.ipynb` for discrepancy-first notebooks.
- Add family, model, or mode only when it materially disambiguates the notebook.

Good examples:

- `eval_autoenc_vit_merge_replay.ipynb`
- `merge_autoenc_tasksum_audit.ipynb`
- `eval_autoenc_vit_block_merge_replay.ipynb`

Avoid:

- `*_trace.ipynb`
- `*_debug.ipynb`
- `*_tmp.ipynb`
- `*_final2.ipynb`

## Markdown Links Back To Code

Use repo-relative links from the notebook directory.

Example for a notebook located at `nino-autoenc/analysis/vit_results/`:

- `[eval_autoenc.py](../../eval_autoenc.py)`
- `[graph_utils.py](../../ninoae/graph_utils.py)`
- `[training.py](../../ninoae/training.py)`

Also mention the exact function or class names in prose:

- `evaluate_single_model`
- `run_merge_evaluation`
- `build_graphs_for_blocks`
- `merge`

## Line References

- Prefer file links plus function names over brittle line anchors.
- If the renderer is known to support anchors, keep them supplementary rather than essential.
- When anchors are unreliable, write plain text references like `eval_autoenc.py:L1667` in the markdown explanation.

## Markdown Phrasing Pattern

Use short labels when introducing a section:

- `Goal:`
- `Source:`
- `Checks:`
- `Assumptions:`
- `Notebook-only deviation:`

This keeps replay notebooks easy to scan and easy to audit against the source code.
