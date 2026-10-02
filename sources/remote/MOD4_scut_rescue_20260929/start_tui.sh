#!/usr/bin/env bash
set -euo pipefail
root=/home/egde/rl_candidates/MOD4_scut_rescue_20260929
export DISPLAY="${DISPLAY:-:0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=${XDG_RUNTIME_DIR}/bus}"
exec gnome-terminal --window --maximize --title='MOD4 SCUT 训练与真实高度验收' -- /usr/bin/python3 -u "$root/isaac/mod4/tui_rescue.py"
