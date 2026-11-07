import os, subprocess, time, json, sys
from pathlib import Path
root=Path('/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107')
current_job=root/'scut_flat_v30_v28warm_1h_20261108_r1'
second_job=root/'scut_flat_v30_v28warm_2h_20261108_r1'
second_log=root/'scut_flat_v30_v28warm_2h_20261108_r1.log'
status_path=root/'WATCH_2H_STATUS.json'
current_pid=int((root/'scut_flat_v30_v28warm_1h_20261108_r1.pid').read_text().strip())

def put(value):
    tmp=status_path.with_name(status_path.name+'.partial')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    os.replace(tmp,status_path)

def alive(pid):
    try:
        os.kill(pid,0)
        return True
    except OSError:
        return False

def gpu_has_pid(pid):
    try:
        out=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,stderr=subprocess.DEVNULL)
        return str(pid) in {x.strip() for x in out.splitlines()}
    except Exception:
        return True

put(dict(phase='waiting',current_pid=current_pid,time=time.time()))
while True:
    if (current_job/'ERROR.json').exists():
        put(dict(phase='stopped',reason='current_error',time=time.time()))
        break
    final=current_job/'FINAL.json'
    safe=current_job/'SAFE_CLOSED.json'
    if final.exists() and safe.exists():
        if not alive(current_pid) or not gpu_has_pid(current_pid):
            if second_job.exists() or second_log.exists():
                put(dict(phase='stopped',reason='second_job_or_log_exists',time=time.time()))
                break
            env=dict(os.environ)
            env.update(WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
            cmd=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','-B','-u','-m','mod4v3_ppo.scut_flat_train','--plan',str(root/'PLAN_LOCAL.json'),'--mode','train','--job',str(second_job),'--num-envs','4096','--seconds','7200','--iterations','6528','--resume',str(current_job/'model_final.pt')]
            with open(second_log,'ab',buffering=0) as out:
                child=subprocess.Popen(cmd,cwd=str(root/'support'),env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
            (root/'scut_flat_v30_v28warm_2h_20261108_r1.pid').write_text(str(child.pid)+'\n')
            put(dict(phase='launched',current_pid=current_pid,second_pid=child.pid,time=time.time(),job=str(second_job),seconds=7200,iterations=6528))
            break
    if not alive(current_pid):
        put(dict(phase='stopped',reason='current_exit_without_complete_final_safe',time=time.time(),final=final.exists(),safe=safe.exists()))
        break
    time.sleep(15)
