#!/usr/bin/env bash
set -euo pipefail
stage=/home/egde/rl_candidates/MOD4_takeover_20260914/scut_flat_repair10h_20260927
out="$stage/run/spring_force_ab_20260927"
ck="$stage/run/scut_flat_resume_env20000_manual_20260927/segment_000/logs/2026-09-27_21-34-12_scut_flat_mod4/model_1720.pt"
py=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
echo "START $(date -Is) force=350 actual-force-audit" >> "$out/status.txt"
OMNI_KIT_ACCEPT_EULA=YES RM_GAS_FORCE_DR=1 RM_GAS_FORCE_DR_ONLY=1 RM_DR_OFF=1 \
RM_GAS_FORCE_FRAME=reference RM_GAS_FORCE_NOMINAL_N=350 \
RM_GAS_FORCE_MIN_N=350 RM_GAS_FORCE_MAX_N=350 \
"$py" -u "$stage/source/mod4/eval_flat_spring_ab.py" \
  --headless --checkpoint "$ck" --num_envs 16 --steps 1500 \
  --seed 20260926 --report "$out/force_350_actual.json" \
  > "$out/force_350_actual.log" 2>&1
test -s "$out/force_350_actual.json"
echo "DONE $(date -Is) force=350 actual-force-audit" >> "$out/status.txt"
