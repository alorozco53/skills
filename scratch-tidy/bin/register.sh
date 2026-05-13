#!/usr/bin/env bash
# scratch-tidy/register.sh — append one row to the agent's session manifest.
#
# Usage:
#   register.sh <path> <intent> <lifetime>
#     <path>     absolute or current-relative path (script resolves to absolute)
#     <intent>   cache | output | script | log | input
#     <lifetime> ephemeral | persistent
#
# Requires SCRATCH_TIDY_SESSION env var (set once at session start).
# Manifest written to $SCRATCH/tmp/.tidy_manifest/<session>.tsv (TSV append).
# Idempotent: a second call with the same path overwrites the previous entry's
# intent/lifetime via the LAST-row-wins rule in tidy.py.

set -euo pipefail

if [[ -z "${SCRATCH_TIDY_SESSION:-}" ]]; then
    echo "register.sh: ERROR — SCRATCH_TIDY_SESSION env var not set" >&2
    echo "  fix: export SCRATCH_TIDY_SESSION=\"$(basename \"$0\")-\$(date +%Y%m%d-%H%M%S)\"" >&2
    exit 2
fi
if [[ -z "${SCRATCH:-}" ]]; then
    echo "register.sh: ERROR — SCRATCH env var not set" >&2
    exit 2
fi

if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <path> <intent> <lifetime>" >&2
    echo "  intent   ∈ cache | output | script | log | input" >&2
    echo "  lifetime ∈ ephemeral | persistent" >&2
    exit 2
fi

path="$1"
intent="$2"
lifetime="$3"

case "$intent" in
    cache|output|script|log|input) ;;
    *) echo "register.sh: ERROR — invalid intent '$intent'" >&2; exit 2 ;;
esac
case "$lifetime" in
    ephemeral|persistent) ;;
    *) echo "register.sh: ERROR — invalid lifetime '$lifetime'" >&2; exit 2 ;;
esac

# Resolve to absolute (don't require existence — agent may register before creation)
if [[ "$path" != /* ]]; then
    path="$(pwd)/$path"
fi

manifest_dir="$SCRATCH/tmp/.tidy_manifest"
mkdir -p "$manifest_dir"
manifest="$manifest_dir/$SCRATCH_TIDY_SESSION.tsv"

# Header on first write
if [[ ! -f "$manifest" ]]; then
    printf 'ts_iso\tpath\tintent\tlifetime\n' > "$manifest"
fi

# Append a row
printf '%s\t%s\t%s\t%s\n' "$(date -Iseconds)" "$path" "$intent" "$lifetime" >> "$manifest"
