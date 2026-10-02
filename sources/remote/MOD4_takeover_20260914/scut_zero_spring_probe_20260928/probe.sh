#!/usr/bin/env bash
set -euo pipefail
old=/home/egde/rl_candidates/MOD4_takeover_20260914/scut_flat_repair10h_20260927
stage=/home/egde/rl_candidates/MOD4_takeover_20260914/scut_zero_spring_probe_20260928
out="$old/run/spring_force_ab_20260927"
ck="$old/run/scut_flat_resume_env20000_manual_20260927/segment_000/logs/2026-09-27_21-34-12_scut_flat_mod4/model_1720.pt"
py=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
mkdir -p "$out"
echo "START $(date -Is) zero spring stiffness and damping; checkpoint model_1720" >> "$out/status.txt"
OMNI_KIT_ACCEPT_EULA=YES RM_GAS_DISABLE=1 RM_GAS_FORCE_DR=0 RM_DR_OFF=1 \
RM_MOD4_USD="$stage/asset/robot_wheel_convex24.usd" \
"$py" -u "$stage/source/mod4/eval_flat_spring_ab.py" \
  --headless --checkpoint "$ck" --num_envs 16 --steps 1500 \
  --seed 20260926 --report "$out/force_zero_no_spring.json" \
  > "$out/force_zero_no_spring.log" 2>&1
test -s "$out/force_zero_no_spring.json"
echo "DONE $(date -Is) zero spring stiffness and damping" >> "$out/status.txt"
