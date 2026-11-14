"""Follow one finite training owner and independent fixed evaluations to completion."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

T=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--access-dir',required=True);a=p.parse_args()
sys.path.insert(0,a.access_dir)
from ssh72 import connect,execute
plan=json.loads((T/'PLAN.json').read_bytes());root=plan['root'];train='train7200'
last_record=0.;last_files=set();collected=set()

def local(params,label):
    child=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/'control72.py'),'--access-dir',a.access_dir,*params],
        cwd=T,capture_output=True,text=True,encoding='utf8')
    (T/'evidence'/label).write_text(child.stdout+child.stderr,encoding='utf8')
    if child.returncode:raise RuntimeError(label+' failed')

def read(s,path):
    try:
        with s.open(path,'rb') as f:return json.loads(f.read())
    except FileNotFoundError:return None

while True:
    client=connect()
    try:
        s=client.open_sftp();roots=set(s.listdir(root))
        try:names=set(s.listdir(root+'/'+train))
        except FileNotFoundError:names=set()
        progress=read(s,root+'/'+train+'/LATEST_PROGRESS.json')
        final=read(s,root+'/'+train+'/FINAL.json');error=read(s,root+'/'+train+'/ERROR.json')
        if progress and time.time()-last_record>=30.:
            compact=dict(epoch=time.time(),iteration=progress['iteration'],updates=progress['new_updates'],
                training_seconds=round(progress['training_elapsed_seconds'],2),counts=progress['jump']['counts'],
                done_totals=progress['jump']['done_totals'],losses=progress['losses'],env_steps=progress['total_env_steps'])
            with (T/'evidence/progress_history.jsonl').open('a') as f:f.write(json.dumps(compact)+'\n')
            print(json.dumps(dict(training=compact)),flush=True);last_record=time.time()
        ready={n for n in names if n.endswith(('.pt','.json')) and n!='LATEST_PROGRESS.json'}
        if ready!=last_files and names:
            local(['--mode','collect','--job',train],'collect_training.log');last_files=ready
        checkpoints=sorted(n for n in names if n.startswith('model_') and n.endswith('.pt') and n!='model_first_complete.pt')
        active=[]
        for job in sorted(n for n in roots if n.startswith('eval_') and '.' not in n):
            closed=read(s,root+'/'+job+'/SAFE_CLOSED.json')
            if closed:
                if job not in collected:
                    local(['--mode','collect','--job',job],'collect_'+job+'.log');collected.add(job)
                    result=read(s,root+'/'+job+'/RESULT.json')
                    print(json.dumps(dict(evaluation=job,summary=result.get('summary') if result else None,closed=closed)),flush=True)
            else:active.append(job)
        status,out,err=execute(client,'nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader',20)
        assert status==0,err
        if not active and 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d' not in out:
            for checkpoint in checkpoints:
                job='eval_'+checkpoint.removesuffix('.pt')
                if job in roots:continue
                local(['--mode','evaluate','--job',job,'--checkpoint',root+'/'+train+'/'+checkpoint,'--num-envs','256'],
                    'launch_'+job+'.log')
                active.append(job);print(json.dumps(dict(queued_evaluation=job)),flush=True);break
        if error:
            local(['--mode','collect','--job',train],'collect_failed_training.log')
            raise RuntimeError('Native owner failed: '+json.dumps(error))
        expected={'eval_'+n.removesuffix('.pt') for n in checkpoints}
        if final and read(s,root+'/'+train+'/SAFE_CLOSED.json') and not active and expected.issubset(collected):
            local(['--mode','collect','--job',train],'collect_final_training.log')
            print(json.dumps(dict(complete=True,final=final,evaluations=len(expected))),flush=True);break
        s.close()
    finally:client.close()
    time.sleep(15.)
