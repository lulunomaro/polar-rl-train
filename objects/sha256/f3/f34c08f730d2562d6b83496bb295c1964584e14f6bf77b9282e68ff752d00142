#!/usr/bin/env bash
# 4090 终端训练监控：在本机（目标机）桌面开一个 GNOME 终端跑 Rich 仪表盘。
# 只读训练 stdout 日志，不碰训练进程 / GPU 计算。
set -uo pipefail
BASE=/home/egde/fangzhen_linux
PY=${PY:-/usr/bin/python3}
LOG=${LOG:-/home/egde/rl_candidates/MOD4_scut_rescue_20260929/train_0.log}
TOTAL=${TOTAL:-4350}
ENVS=${ENVS:-20000}
STEPS=${STEPS:-24}
exec /usr/bin/gnome-terminal --window --geometry=154x48 --title='MOD4 4090 训练监控' \
  -- $PY -u "$BASE/runs4090/monitor/tui_rich.py" --source log --log "$LOG" \
     --total "$TOTAL" --envs "$ENVS" --steps "$STEPS"
