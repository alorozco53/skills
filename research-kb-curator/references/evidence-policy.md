# Evidence Policy

## Access hierarchy

Use this order of preference:

1. full paper from an authoritative source;
2. official supplement, appendix, code repository, or author page;
3. official abstract or metadata page;
4. trustworthy secondary account;
5. search snippet only for discovery, never as substantive evidence.

Record the strongest level actually accessed. Do not upgrade it based on what
was probably available.

## Required distinction

### Authors' claim

A statement the authors explicitly make.

### Evidence

A result, proof, analysis, ablation, table, figure, theorem, or observation
presented in the source.

### Assessment

A judgment about what the evidence does or does not establish.

### Interpretation

A reasoned reading not explicitly asserted by the authors.

### Speculation

A possible explanation, connection, or future direction that is not established
by the source.

These categories may appear in the same block, but they must remain visibly
separate.

## Locators

Use the most precise locator available:

- theorem, proposition, lemma, or corollary;
- equation number;
- table or figure number;
- algorithm number;
- section or appendix subsection;
- page number, especially when numbering is absent.

Prefer:

```text
Table 3; Section 4.2, pp. 8–9
```

over:

```text
Experiments section
```

If the document's rendered and printed page numbers differ, state which one is
used when ambiguity matters.

## Evidence strength

Use concrete descriptions rather than inflated labels.

Examples:

- controlled comparison under a shared setup;
- ablation isolating one component;
- correlation across methods;
- result on one architecture family;
- theorem under explicit assumptions;
- qualitative case study;
- author hypothesis consistent with observed results.

Do not call correlation causal. Do not call a missing negative result proof of
absence.

## Abstract-only processing

Allowed:

- bibliographic metadata;
- the abstract's explicit claims;
- high-level stated contribution;
- questions to verify later.

Not allowed:

- exact experimental setup not stated in the abstract;
- detailed limitations inferred from unseen sections;
- table, figure, or equation references;
- strong judgments about evidence quality.

## Secondary-source processing

Identify the secondary source and preserve the original-paper link when known.
Never attribute a secondary interpretation directly to the paper's authors.

## Conflicts

When sources disagree:

1. compare architecture, data, task, metric, training regime, calibration
   access, alignment assumptions, and evaluation protocol;
2. determine whether the disagreement survives those differences;
3. preserve both results;
4. avoid forcing a single conclusion when evidence remains mixed.

## Agent uncertainty

Use explicit language:

- `Verified in full text`
- `Abstract-only`
- `Not verified`
- `Inferred from the experimental setup`
- `Possible interpretation`
- `Unsupported by the inspected material`

Uncertainty is metadata, not an embarrassment.
