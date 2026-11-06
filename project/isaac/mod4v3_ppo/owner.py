"""Hold the actual private GPU lease through train, independent80 and replay."""
from pathlib import Path
import fcntl
import json
import os
import subprocess
import sys
import time
from .train import put


def main():
    plan_path=Path(sys.argv[1]);plan=json.loads(plan_path.read_bytes())
    root=plan_path.parent;uuid=plan['GPU_UUID']
    lock=Path(plan['gpu_lock']);lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open('a+') as lease:
        fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
        apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,gpu_uuid,used_memory',
            '--format=csv,noheader'],text=True)
        if uuid in apps:raise RuntimeError('Selected GPU is occupied')
        free=subprocess.check_output(['nvidia-smi','--id='+uuid,'--query-gpu=memory.free',
            '--format=csv,noheader,nounits'],text=True)
        if int(free.strip())<22000:raise RuntimeError('GPU is not actually free')
        put(root/'OWNER.json',dict(epoch=time.time(),pid=os.getpid(),GPU_UUID=uuid,
            private_lock=str(lock),compute_apps_before=apps,free_memory_mib=int(free),noledger=True))
        child_env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONPATH=str(root/'code'),
                       PYTHONUNBUFFERED='1')
        def run(mode,name,n,seconds=0,resume=None):
            child_env['CUDA_LAUNCH_BLOCKING']='1' if mode=='probe' else '0'
            bootstrap='import runpy,sys;sys.path.insert(0,'+repr(str(root/'code'))+');runpy.run_module("mod4v3_ppo.train",run_name="__main__")'
            command=[plan['python'],'-B','-c',bootstrap,'--plan',str(plan_path),
                '--mode',mode,'--job',str(root/name),'--num-envs',str(n),'--seconds',str(seconds)]
            if resume:command+=['--resume',str(resume)]
            with (root/(name+'.log')).open('x') as log:
                p=subprocess.Popen(command,env=child_env,stdout=log,stderr=subprocess.STDOUT,pass_fds=(lease.fileno(),))
                put(root/'OWNER_CURRENT.json',dict(epoch=time.time(),child_pid=p.pid,mode=mode,job=name))
                # The application owns a finite save deadline. This outer bound
                # detects crashes/hangs; it does not interrupt an active update.
                status=p.wait()
            put(root/(name+'_EXIT.json'),dict(epoch=time.time(),returncode=status))
            result=root/name/('RESULT.json' if mode=='evaluate' else 'FINAL.json')
            if status or (root/name/'ERROR.json').exists() or not result.exists():
                raise RuntimeError(name+' failed: '+str(status))
        attempt=plan.get('attempt','01')
        if not plan.get('completed_probe'):
            run('probe','probe'+attempt,16,1200)
            run('probe','restore'+attempt,16,1200,root/('probe'+attempt)/'model_final.pt')
        else:
            for directory in plan['completed_probe']:
                if not (root/directory/'FINAL.json').is_file() or (root/directory/'ERROR.json').exists():
                    raise RuntimeError('Referenced successful probe is incomplete')
        production='production'+attempt;evaluation='evaluation80_'+attempt
        run('train',production,plan['num_envs'],plan.get('seconds',3600),plan.get('resume_checkpoint'))
        run('evaluate',evaluation,80,0,root/production/'model_final.pt')
        put(root/'OWNER_COMPLETE.json',dict(epoch=time.time(),training=True,independent80=True,
            replay=str(root/evaluation/'actual_replay.npz')))


if __name__=='__main__':main()
