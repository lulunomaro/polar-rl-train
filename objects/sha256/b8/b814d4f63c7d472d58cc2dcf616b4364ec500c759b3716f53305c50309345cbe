#!/usr/bin/env bash
set -euo pipefail
export DISPLAY=:0
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export XAUTHORITY=/run/user/1000/gdm/Xauthority
exec gnome-terminal --window --maximize --title='MOD4 原生平面修复 — 新10小时预算' -- /usr/bin/python3 -u /home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/isaac/mod4/tui_rescue.py
