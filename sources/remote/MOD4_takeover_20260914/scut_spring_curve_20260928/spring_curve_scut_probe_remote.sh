#!/usr/bin/env bash
set -euo pipefail
old=/home/egde/rl_candidates/MOD4_takeover_20260914/scut_flat_repair10h_20260927
stage=/home/egde/rl_candidates/MOD4_takeover_20260914/scut_spring_curve_20260928
out="$old/run/spring_force_ab_20260927"
ck="$old/run/scut_flat_resume_env20000_manual_20260927/segment_000/logs/2026-09-27_21-34-12_scut_flat_mod4/model_1720.pt"
py=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
echo "START $(date -Is) scut-derived F0=400 k=2857.142857" >> "$out/status.txt"
OMNI_KIT_ACCEPT_EULA=YES RM_GAS_FORCE_DR=1 RM_GAS_FORCE_DR_ONLY=1 RM_DR_OFF=1 \
RM_GAS_FORCE_FRAME=reference RM_GAS_FORCE_NOMINAL_N=400 \
RM_GAS_FORCE_MIN_N=400 RM_GAS_FORCE_MAX_N=400 \
RM_GAS_LINEAR_STIFFNESS_N_M=2857.142857142857 \
RM_MOD4_USD="$stage/asset/robot_wheel_convex24.usd" \
"$py" -u "$stage/source/mod4/eval_flat_spring_ab.py" \
  --headless --checkpoint "$ck" --num_envs 16 --steps 1500 \
  --seed 20260926 --report "$out/force_400_scut_curve.json" \
  > "$out/force_400_scut_curve.log" 2>&1
test -s "$out/force_400_scut_curve.json"
echo "DONE $(date -Is) scut-derived F0=400 k=2857.142857" >> "$out/status.txt"
