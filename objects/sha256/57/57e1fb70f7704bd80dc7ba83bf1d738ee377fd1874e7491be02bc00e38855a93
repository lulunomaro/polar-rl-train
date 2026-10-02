#!/usr/bin/env bash
# Post-v2-chain runbook as code: apply the five pending patches, then run the tagged acceptance
# and compare it with the frozen baseline.
#
# Why this exists: after a 10-12 hour chain, the last thing anyone wants is to reconstruct a
# five-step sequence by hand -- and every one of these patches fixes a defect that is SILENT
# (a check that cannot see its data, a frozen list missing files, evidence overwritten in place).
# Encoding the order here means the sequence is validated BEFORE the chain ends.
#
#   DRY=1 bash migration/linux/post_v2_chain.sh          # print the plan, change nothing
#   bash migration/linux/post_v2_chain.sh                # do it
#
# Steps
#   0  refuse to run while a training/eval/chain is live (one task at a time)
#   1  apply the five patches (idempotent; each keeps its own .bak_pre_*)
#   2  recall the DR note: the smoke gate is knowingly DR-aware after this
#   3  run the formal acceptance with RM_ACCEPT_TAG=v2 so it CANNOT overwrite chain-1 evidence
#   4  compare against docs/acceptance_baseline_16295
set -uo pipefail
cd "$(dirname "$0")/../.."

DRY=${DRY:-0}
TAG=${TAG:-v2}
CKPT=${CKPT:-}

say() { echo "[post-v2] $*"; }

# ---- 0. one task at a time ----------------------------------------------------------------
# exclude any process whose command line mentions THIS script: a caller like
#   bash -c "DRY=1 bash migration/linux/post_v2_chain.sh"
# carries the search pattern in its own argv and would otherwise match itself (measured: it did).
_live_re="[t]rain_mod4_ppo|[e]val_terrain_mod4|[r]un_special_phases_v3"
live=$(ps -eo pid,args | grep -E "$_live_re" | grep -v "post_v2_chain" | wc -l)
if [ "$live" != "0" ]; then
  say "REFUSING: $live training/eval/chain process(es) are live.  Wait for the chain to finish."
  ps -eo pid,etime,args | grep -E "$_live_re" | grep -v "post_v2_chain" | cut -c1-100 | sed 's/^/  /'
  exit 3
fi
say "no training/eval/chain running"

# ---- 1. the five pending patches ----------------------------------------------------------
# The 7 patches this session leaves pending.  Two of them were added AFTER this script was first
# written and were missing from it -- notably `patch_tunnel_episode_and_eval`, which audit 59
# identified as the single highest-value fix (it relaxes the episode/eval window for FOUR subjects
# at once: fly_jump needs 0.29 m/s sustained across 5.80 m in 20 s, i.e. it spends the whole budget
# just reaching the launch platform).  Keep this list in sync with `patch_*.py --check`.
PATCHES="patch_frozen_files_modules patch_smoke_gate_dr_aware patch_accept_tag
patch_gain_parity_keys_fix patch_acceptance_encoder_from_manifest
patch_smoke_verdict_logpath patch_tunnel_episode_and_eval"
say "patches to apply (in order):"
for p in $PATCHES; do say "  $p"; done
if [ "$DRY" != "1" ]; then
  for p in $PATCHES; do
    out=$(python3 "migration/linux/$p.py" 2>&1 | tail -1)
    say "  $p -> $out"
    case "$out" in *FAIL*) say "PATCH FAILED, stopping"; exit 4;; esac
  done
  for f in migration/linux/final_acceptance_mod4.sh migration/linux/run_special_phases_v3.sh; do
    bash -n "$f" || { say "SYNTAX FAIL after patching: $f"; exit 5; }
  done
  say "all patches applied; shell syntax verified"
fi

# ---- 2/3. tagged acceptance ---------------------------------------------------------------
if [ -z "$CKPT" ]; then
  CKPT=$(ls -t logs/isaac_mod4/*/model_*.pt 2>/dev/null | head -1)
  [ -n "$CKPT" ] && say "checkpoint (newest): $CKPT" || say "no checkpoint found -- pass CKPT=..."
fi
say "acceptance: RM_ACCEPT_TAG=$TAG CKPT=$CKPT"
say "  (the tag is what stops this run from overwriting docs/acceptance_phase_v3_* of chain 1)"
say "  NOTE: the gain-parity check will exit 8 on a 2500-vs-60 gain gap unless you choose"
say "        RM_GAIN_PARITY_MAX=0 (accept-with-reason) or retrain at the contract gains."
if [ "$DRY" = "1" ]; then
  say "DRY=1 -- plan only, nothing changed"
  exit 0
fi
RM_ACCEPT_TAG="$TAG" bash migration/linux/final_acceptance_mod4.sh "$CKPT" "$TAG"
rc=$?
say "acceptance rc=$rc  (out: docs/acceptance_${TAG})"

# ---- 4. compare ---------------------------------------------------------------------------
if [ -f "docs/acceptance_${TAG}/nominal.json" ]; then
  python3 migration/linux/compare_v2_vs_baseline.py --v2 "docs/acceptance_${TAG}"
else
  say "no nominal.json under docs/acceptance_${TAG} -- nothing to compare"
fi
exit $rc
