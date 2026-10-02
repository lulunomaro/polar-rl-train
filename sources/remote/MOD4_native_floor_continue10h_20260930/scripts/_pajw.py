import io
io.open(r"D:/claude2/fangzhen/sim2sim/wsl/demo_run.sh","w",encoding="utf-8",newline="\n").write('''#!/usr/bin/env bash
set -o pipefail
cd /root/ws/sim2sim
SEC=${1:-15}
LOG=${2:-/tmp/demo.log}
timeout $((SEC + 120)) bash scripts/demo.sh --headless --duration "$SEC" > "$LOG" 2>&1
echo "DEMO_EXIT=$?"
''')
print("ok")
