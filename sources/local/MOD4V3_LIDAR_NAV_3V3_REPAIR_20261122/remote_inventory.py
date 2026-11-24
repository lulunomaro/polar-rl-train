from nav_common import HERE, put, donor_imports
donor_imports()
from remote_e0 import connect, execute
with connect('host72') as ssh:
    commands=["nvidia-smi -i 0 --query-gpu=index,uuid,name,memory.used,utilization.gpu --format=csv,noheader,nounits",
              "ls -d '/home/lc01/Zonglin Li/zonglin2/tasks/'MOD4V3_MANUAL_FSM_STAIR_UNIFIED_20261122/*/dependencies 2>/dev/null",
              "ls -d '/home/lc01/Zonglin Li/zonglin2/tasks/'MOD4V3_MOVING_JUMP_360MM_GPU_RL_20261121 2>/dev/null"]
    for command in commands:
        print(execute(ssh,command),flush=True)
