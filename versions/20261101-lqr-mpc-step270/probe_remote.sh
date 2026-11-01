set -e
TASK='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MUJOCO_LQR_MPC_STEP270_20261101'
tar -xzf "$TASK/model_bundle.tar.gz" -C "$TASK"
bash "$TASK/run.sh" "$TASK/initial_probe.py"
