#!/usr/bin/env bash
# One-off: stop the v1 special-phase chain (mis-specified weights, see run_special_phases_v2.sh
# header) and pick a loadable resume checkpoint from the abandoned run.  Prints RESUME=<path>.
# Deliberately leaves the GPU idle afterwards; the caller starts the v2 chain.
set -uo pipefail
cd /home/egde/fangzhen_linux
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python

echo "--- stopping v1 chain and its training"
pgrep -af "bash migration/linux/run_special_phases.sh" || echo "no v1 chain process"
for p in $(pgrep -f "bash migration/linux/run_special_phases.sh"); do kill "$p" 2>/dev/null; done
for p in $(pgrep -f "train_mod4_ppo.py --headless"); do kill "$p" 2>/dev/null; done

for i in $(seq 1 60); do
  pgrep -f "train_mod4_ppo.py --headless" >/dev/null || break
  sleep 5
done
if pgrep -f "train_mod4_ppo.py --headless" >/dev/null; then
  echo "--- still alive after 300 s, sending SIGKILL"
  for p in $(pgrep -f "train_mod4_ppo.py --headless"); do kill -9 "$p" 2>/dev/null; done
  sleep 20
fi
pgrep -af "train_mod4_ppo.py --headless" || echo "training stopped"
pgrep -af "bash migration/linux/run_special_phases.sh" || echo "v1 chain stopped"

echo "--- waiting for GPU memory to drop"
for i in $(seq 1 40); do
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
  [ "${used:-99999}" -lt 1500 ] && break
  sleep 5
done
echo "gpu_used_mib=$used"

echo "--- resume candidate"
D=$(ls -dt logs/isaac_mod4/*_mod4_fixed_mixed/ | head -1)
echo "newest_run=$D"
RESUME=""
for f in $(ls -t "$D"model_*.pt 2>/dev/null | head -6); do
  if $PY -c "import torch,sys;torch.load(sys.argv[1],map_location='cpu',weights_only=False)" "$f" >/dev/null 2>&1; then
    echo "OK   $f"
    [ -z "$RESUME" ] && RESUME="$f"
  else
    echo "BAD  $f"
  fi
done
echo "RESUME=$RESUME"
