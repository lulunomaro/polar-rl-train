#!/usr/bin/env bash
set -euo pipefail
root=/home/egde/rl_candidates/MOD4_takeover_20260914
stage="$root/scut_v14_spring_mod4_20260928"
old="$root/scut_flat_repair10h_20260927"
out="$stage/run/nominal_probe"
ck="$old/run/scut_flat_resume_env20000_manual_20260927/segment_000/logs/2026-09-27_21-34-12_scut_flat_mod4/model_1720.pt"
py=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
mkdir -p "$out"
echo "START $(date -Is) V14 linear spring, nominal force, same model_1720" > "$out/status.txt"
OMNI_KIT_ACCEPT_EULA=YES RM_GAS_SCUT_V14=1 RM_GAS_FORCE_DR=1 \
RM_GAS_FORCE_DR_ONLY=1 RM_DR_OFF=1 RM_GAS_FORCE_FRAME=reference \
RM_GAS_FORCE_NOMINAL_N=500.58095715 \
RM_GAS_FORCE_MIN_N=500.58095715 RM_GAS_FORCE_MAX_N=500.58095715 \
RM_GAS_FORCE_EDGE_PROB=0 \
RM_MOD4_USD="$stage/asset/robot_wheel_convex24.usd" \
"$py" -u "$stage/source/mod4/eval_flat_spring_ab.py" \
  --headless --checkpoint "$ck" --num_envs 16 --steps 1500 \
  --seed 20260926 --report "$out/scut_v14_nominal.json" \
  > "$out/scut_v14_nominal.log" 2>&1
test -s "$out/scut_v14_nominal.json"
echo "DONE $(date -Is) V14 linear spring nominal" >> "$out/status.txt"
