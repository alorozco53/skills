# Templates and Examples

Use these as structural patterns. Preserve the actual project's established node names when updating an existing tree.

## Research experiment campaign

```text
Scientific claim
    │
    ├── Inputs and contracts
    │      ├── datasets ───────────────────────── [PASSED]
    │      └── checkpoints ────────────────────── [PASSED]
    │
    ├── Baselines
    │      ├── method A ───────────────────────── [DONE]
    │      └── method B ───────────────────────── [DONE]
    │
    ├── Proposed method
    │      ├── smoke test ─────────────────────── [PASSED]
    │      ├── full sweep ─────────────────────── [RUNNING]
    │      └── ablations ──────────────────────── [NEXT]
    │
    └── Evidence package
           ├── aggregation ────────────────────── [WAITING: full sweep]
           ├── figures ────────────────────────── [WAITING: aggregation]
           └── paper table ────────────────────── [WAITING: aggregation]
```

## Software feature

```text
Feature delivery
    │
    ├── Contract
    │      ├── API/schema ─────────────────────── [DONE]
    │      └── migration decision ─────────────── [DONE]
    │
    ├── Implementation
    │      ├── core logic ─────────────────────── [DONE]
    │      └── integration ────────────────────── [RUNNING]
    │
    ├── Verification
    │      ├── unit tests ─────────────────────── [PASSED]
    │      ├── integration tests ──────────────── [RUNNING]
    │      └── end-to-end test ────────────────── [WAITING: integration]
    │
    └── Delivery
           ├── review ─────────────────────────── [NEXT]
           └── release ────────────────────────── [WAITING: review]
```

## Paper submission

```text
Submission
    │
    ├── Experimental evidence
    │      ├── principal table ────────────────── [DONE]
    │      ├── ablations ──────────────────────── [RUNNING]
    │      └── error analysis ─────────────────── [NEXT]
    │
    ├── Manuscript
    │      ├── methods ────────────────────────── [DONE]
    │      ├── results ────────────────────────── [WAITING: experiments]
    │      └── appendix ───────────────────────── [RUNNING]
    │
    └── Finalization
           ├── figure consistency ─────────────── [WAITING: figures]
           ├── proofread ──────────────────────── [WAITING: manuscript]
           └── submission package ─────────────── [WAITING: proofread]
```

## Macro plus active frontier

Use when the full project is too large to expand usefully.

```text
Model-merging study
├── Data and checkpoints ──────────────────────── [DONE]
├── Baselines ─────────────────────────────────── [DONE]
├── Proposed methods ──────────────────────────── [RUNNING]
└── Paper integration ─────────────────────────── [WAITING: experiments]

Active frontier
├── Method A, seeds 1–3 ───────────────────────── [DONE]
├── Method B, seeds 1–2 ───────────────────────── [DONE]
├── Method B, seed 3 ──────────────────────────── [RUNNING]
└── Aggregate table ───────────────────────────── [AUTO-NEXT]
```

## ETA plus frontier

```text
Current ETA:

- decoded-source smoke: ~1–3 minutes remaining
- latent α sweep: queued behind the smoke allocation
- 18/60 validation trials are already cached
- expected sweep runtime after starting: ~45–55 minutes

Figure reproduction
    │
    ├── Original diagnostics ───────────────────── [DONE]
    ├── Latent-merging diagnostics ─────────────── [DONE]
    └── Hybrid experiments
           ├── decoded-source path
           │      ├── smoke ────────────────────── [RUNNING]
           │      └── full 8-task evaluation ───── [NEXT]
           └── latent-space path
                  ├── α sweep ──────────────────── [PARTIAL 18/60]
                  ├── selected-α test ───────────── [AUTO-NEXT]
                  └── final plots ───────────────── [WAITING: experiments]
```

Interpretation:

`The immediate frontier is the decoded-source smoke plus the remaining latent-space sweep. After those finish, the principal outstanding compute item is the full eight-task decoded-source evaluation.`

## Stable update example

Before:

```text
├── smoke ─────────────────────────────────────── [RUNNING]
├── full evaluation ───────────────────────────── [NEXT]
└── plots ─────────────────────────────────────── [WAITING: full evaluation]
```

After:

```text
├── smoke ─────────────────────────────────────── [PASSED]
├── full evaluation ───────────────────────────── [RUNNING]
└── plots ─────────────────────────────────────── [WAITING: full evaluation]
```

The value comes from the small diff. Do not rename `full evaluation`, reorder the nodes, or re-expand unrelated completed work unless the plan itself changed.

## Bad: flat chronology

```text
- wrote script
- fixed shape bug
- relaunched
- sweep queued
- plots pending
```

This hides causality and makes resolved incidents visually equal to current work.

## Better: causal frontier

```text
Hybrid experiment
├── implementation/validation ─────────────────── [PASSED]
├── full sweep ────────────────────────────────── [QUEUED]
└── plots ─────────────────────────────────────── [WAITING: full sweep]
```
