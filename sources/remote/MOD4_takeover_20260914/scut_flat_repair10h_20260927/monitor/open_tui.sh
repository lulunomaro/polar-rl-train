#!/usr/bin/env bash
set -euo pipefail
BASE=/home/egde/rl_candidates/MOD4_takeover_20260914/scut_flat_repair10h_20260927
exec /usr/bin/gnome-terminal --window --geometry=154x48 --title='MOD4 RL 实时训练监控' -- /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -u "$BASE/monitor/tui.py" --url http://10.24.4.210:8765/api/state
