#!/usr/bin/env bash
set -euo pipefail
stage=/home/egde/rl_candidates/MOD4_takeover_20260914/scut_v14_strong_posture_20260928
run="$stage/run/posture_mechanics_probe"
ck="$stage/run/scut_v14_strong_posture_20260928/segment_000/logs/2026-09-28_08-24-52_scut_flat_mod4/model_2650.pt"
mkdir -p "$run"
test -s "$ck"
OMNI_KIT_ACCEPT_EULA=YES CUDA_VISIBLE_DEVICES=0 PYTHONUNBUFFERED=1 \
RM_MOD4_MAP=fudan_plane RM_MOD4_TERRAIN=flat RM_EVAL_LEG_SWEEP=1 \
RM_MOD4_USD="$stage/asset/robot_wheel_convex24.usd" \
RM_GAS_SCUT_V14=1 RM_GAS_FORCE_DR=1 RM_GAS_FORCE_DR_ONLY=1 \
RM_GAS_FORCE_FRAME=reference RM_GAS_FORCE_NOMINAL_N=500.58095715 \
RM_GAS_FORCE_MIN_N=500.58095715 RM_GAS_FORCE_MAX_N=500.58095715 RM_GAS_FORCE_EDGE_PROB=0 \
/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -u \
  "$stage/source/mod4/eval_flat_diagnostics.py" --headless \
  --checkpoint "$ck" --num_envs 64 --steps 300 --seed 20260926 \
  --report "$run/model2650_leg_sweep_3s.json" > "$run/model2650_leg_sweep_3s.log" 2>&1
test -s "$run/model2650_leg_sweep_3s.json"
