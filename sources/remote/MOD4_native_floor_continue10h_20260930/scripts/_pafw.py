import io, os
D = r"D:/claude2/fangzhen/sim2sim/wsl"
os.makedirs(D, exist_ok=True)
def W(name, body):
    p = os.path.join(D, name)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(body.lstrip("\n"))
    print("wrote", name, os.path.getsize(p), "bytes")

W("fix_crlf.py", '''
import io, os, glob
for p in glob.glob(r"D:/claude2/fangzhen/sim2sim/wsl/*.sh"):
    t = io.open(p, encoding="utf-8").read()
    t2 = t.replace("\\r\\n", "\\n").replace("\\r", "\\n")
    if t2 != t:
        io.open(p, "w", encoding="utf-8", newline="\\n").write(t2)
        print("normalized", os.path.basename(p))
print("done")
''')

W("bootstrap_run.sh", '''
#!/usr/bin/env bash
set -uo pipefail
cd /root/ws/sim2sim
echo "=== repo ==="; ls
echo "=== bootstrap ==="
bash scripts/bootstrap.sh --skip-ros-deps 2>&1 | tail -25
echo "BOOTSTRAP_EXIT=$?"
ls -la deps 2>/dev/null | head
''')

W("build_ws.sh", '''
#!/usr/bin/env bash
set -uo pipefail
cd /root/ws/sim2sim
source /opt/ros/humble/setup.bash
echo "=== colcon build ==="
bash scripts/build.sh 2>&1 | tail -40
echo "BUILD_EXIT=$?"
''')

W("demo_run.sh", '''
#!/usr/bin/env bash
set -uo pipefail
cd /root/ws/sim2sim
DUR=${1:-20}
echo "=== demo --headless --duration $DUR ==="
timeout $((DUR + 180)) bash scripts/demo.sh --headless --duration "$DUR" 2>&1 | tail -60
echo "DEMO_EXIT=$?"
''')

W("status.sh", '''
#!/usr/bin/env bash
cd /root/ws/sim2sim
echo "--- deps:"; ls deps 2>/dev/null
echo "--- build logs:"; ls -t log 2>/dev/null | head -3
echo "--- install:"; ls install 2>/dev/null | head -20
echo "--- train log tail:"; tail -c 400 /mnt/d/claude2/fangzhen/logs/train_v1.log 2>/dev/null | tr -d "\\r" | tail -5
''')
