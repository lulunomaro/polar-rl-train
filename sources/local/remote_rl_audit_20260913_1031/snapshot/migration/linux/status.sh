#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
launcher_dir="$ROOT/logs/linux_launch"

show_pid_file() {
  local label="$1" pid_file="$2" pid
  if [[ ! -f "$pid_file" ]]; then
    echo "$label: PID file missing ($pid_file)"
    return
  fi
  pid="$(<"$pid_file")"
  if [[ ! "$pid" =~ ^[0-9]+$ ]]; then
    echo "$label: invalid PID file ($pid_file)"
    return
  fi
  echo "$label -> $pid_file"
  if ! ps -p "$pid" -o pid,etime,%cpu,%mem,cmd; then
    echo "$label: stale PID $pid"
  fi
}

if [[ -f "$launcher_dir/latest_closed_chain_pid_file" ]]; then
  show_pid_file "deployable closed-chain trainer" \
    "$(<"$launcher_dir/latest_closed_chain_pid_file")"
else
  show_pid_file "deployable closed-chain trainer" \
    "$launcher_dir/cc_dm3519_prod_v2.pid"
fi
show_pid_file "closed-chain MuJoCo viewer (inference only)" \
  "$launcher_dir/closed_chain_visible.pid"

nvidia-smi \
  --query-gpu=name,pstate,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw,power.limit,clocks.sm,temperature.gpu \
  --format=csv,noheader

if [[ -f "$launcher_dir/latest_closed_chain_log_file" ]]; then
  log_file="$(<"$launcher_dir/latest_closed_chain_log_file")"
  echo "Closed-chain log: $log_file"
  tail -n 80 "$log_file"
fi

if [[ -f "$launcher_dir/closed_chain_visible.log" ]]; then
  echo "Closed-chain viewer log: $launcher_dir/closed_chain_visible.log"
  tail -n 25 "$launcher_dir/closed_chain_visible.log"
fi

if command -v xwininfo >/dev/null 2>&1; then
  echo "Training viewer windows on DISPLAY=:0:"
  DISPLAY=:0 XAUTHORITY="${XAUTHORITY:-/run/user/$(id -u)/gdm/Xauthority}" \
    xwininfo -root -tree 2>/dev/null | grep -Ei "MuJoCo|Isaac Lab" || true
fi
