import io
p=r"D:/claude2/fangzhen/sim2sim/wsl/build_ws.sh"
io.open(p,"w",encoding="utf-8",newline="\n").write('''#!/usr/bin/env bash
set -o pipefail
cd /root/ws/sim2sim
[ -d wheelbipe_ros2_sim2sim-main ] && rm -rf wheelbipe_ros2_sim2sim-main
set +u
source /opt/ros/humble/setup.bash
set -u
echo "=== colcon build (this takes a few minutes) ==="
bash scripts/build.sh 2>&1 | tail -45
echo "BUILD_EXIT=$?"
ls install 2>/dev/null | head -20
''')
print("ok")
