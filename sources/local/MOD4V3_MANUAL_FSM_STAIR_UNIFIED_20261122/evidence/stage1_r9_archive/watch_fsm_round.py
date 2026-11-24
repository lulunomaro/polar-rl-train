"""Finish a precheck, then launch one already-authorized bounded training round."""
from argparse import ArgumentParser
import json
import subprocess
import time
from fsm_paths import PYTHON,HERE
from remote_manual_fsm import connect,execute,REMOTE
import shlex

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--tag',required=True);p.add_argument('--seconds',type=int,default=900)
    p.add_argument('--after-probe')
    p.add_argument('--checkpoint')
    p.add_argument('--dr-exposure-schedule',action='store_true')
    args=p.parse_args()
    wait_tag=args.after_probe or args.tag
    for _ in range(180):
        with connect('host72') as ssh:
            output=execute(ssh,shlex.join(['test','-f',str(REMOTE/wait_tag/'probe_EXIT.json')])+' && echo CLOSED || true').strip()
            if output:
                row=execute(ssh,'nvidia-smi -i 0 --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits').strip()
                used,util=[int(v.strip()) for v in row.split(',')]
                if used<150 and util==0:
                    break
        time.sleep(10.)
    else:raise TimeoutError('Precheck/idle wait expired; no PPO launched')
    if args.after_probe:
        subprocess.run([str(PYTHON),'-B','-X','utf8',str(HERE/'remote_manual_fsm.py'),'probe','--tag',args.tag,
                        '--checkpoint',args.checkpoint],check=True,cwd=HERE)
        subprocess.run([str(PYTHON),'-B','-X','utf8',str(HERE/'watch_fsm_round.py'),'--tag',args.tag,
                        '--seconds',str(args.seconds)]+(['--dr-exposure-schedule'] if args.dr_exposure_schedule else []),check=True,cwd=HERE)
        return
    subprocess.run([str(PYTHON),'-B','-X','utf8',str(HERE/'remote_manual_fsm.py'),'train',
        '--tag',args.tag,'--seconds',str(args.seconds)]+(['--dr-exposure-schedule'] if args.dr_exposure_schedule else []),check=True,cwd=HERE)

if __name__=='__main__':main()
