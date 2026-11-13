"""Current-task observer: freeze checkpoints and queue policy-only GPU1 tests."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

T = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--access-dir',required=True)
args = parser.parse_args()
sys.path.insert(0,args.access_dir)
from ssh72 import connect,execute
plan = json.loads((T/'PLAN.json').read_bytes())
remote = plan['root']
train = 'train120m_r1'
train_remote = remote+'/'+train
gpu1 = 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
last_update = -1
last_record = 0.
collected = set()
evaluated = set()
last_train_files = set()
last_summary = None


def read(sftp,path):
    try:
        with sftp.open(path,'rb') as stream:
            return json.loads(stream.read())
    except FileNotFoundError:
        return None


def run_local(script,params,log):
    child = subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/script),
        '--access-dir',args.access_dir,*params],cwd=T,capture_output=True,text=True,encoding='utf8')
    (T/'evidence'/log).write_text(child.stdout+child.stderr,encoding='utf8')
    if child.returncode:
        raise RuntimeError(script+' failed; see evidence/'+log)


def collect(job,weights=False):
    params = ['--job',job,'--collect']
    if weights:
        params.append('--weights')
    run_local('collect72.py',params,'collect_'+job+'_'+str(time.time_ns())+'.log')


while True:
    client = connect()
    try:
        sftp = client.open_sftp()
        roots = sftp.listdir(remote)
        names = set(sftp.listdir(train_remote))
        progress = read(sftp,train_remote+'/LATEST_PROGRESS.json')
        final = read(sftp,train_remote+'/FINAL.json')
        error = read(sftp,train_remote+'/ERROR.json')
        if progress and progress['new_updates'] != last_update:
            last_update = progress['new_updates']
            compact = dict(epoch=time.time(),iteration=progress['iteration'],updates=last_update,
                training_seconds=round(progress['training_elapsed_seconds'],2),
                counts=progress['jump']['counts'],done_totals=progress['jump']['done_totals'],
                losses=progress['losses'])
            print(json.dumps(dict(training=compact)),flush=True)
            if time.time()-last_record >= 60.:
                with (T/'evidence/progress_history.jsonl').open('a') as stream:
                    stream.write(json.dumps(compact)+'\n')
                last_record = time.time()
        checkpoints = sorted(n for n in names if n.startswith('model_') and n.endswith('.pt') and n!='model_first_complete.pt')
        ready_train = {n for n in names if n.endswith(('.json','.pt')) and n!='LATEST_PROGRESS.json'}
        if ready_train != last_train_files:
            collect(train,weights=True)
            last_train_files = ready_train
        active = []
        for job in sorted(n for n in roots if n.startswith('eval_')):
            closed = read(sftp,remote+'/'+job+'/SAFE_CLOSED.json')
            if closed:
                if job not in collected:
                    collect(job)
                    collected.add(job)
                    result_path = T/'evidence'/job/'RESULT.json'
                    if result_path.exists():
                        value = json.loads(result_path.read_bytes())
                        print(json.dumps(dict(evaluation=job,sha256=value['checkpoint_sha256'],summary=value['summary'])),flush=True)
                        evaluated.add(job)
                    else:
                        print(json.dumps(dict(evaluation=job,status='failed',evidence=str(T/'evidence'/job))),flush=True)
            else:
                active.append(job)
        status,out,err = execute(client,'nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader',20)
        assert status == 0,err
        if not active and gpu1 not in out:
            for checkpoint in checkpoints:
                job = 'eval_'+checkpoint.removesuffix('.pt')
                if job in roots:
                    continue
                run_local('launch72.py',['--mode','evaluate','--job',job,'--num-envs','256',
                    '--fixed-eval','--checkpoint',train_remote+'/'+checkpoint],'launch_'+job+'.log')
                print(json.dumps(dict(queued_evaluation=job,checkpoint=checkpoint)),flush=True)
                active.append(job)
                break
        if error:
            collect(train,weights=True)
            print(json.dumps(dict(training_failed=error)),flush=True)
            raise RuntimeError('Training error recorded; no automatic optimizer restart')
        if final and read(sftp,train_remote+'/SAFE_CLOSED.json') and not active:
            expected = {'eval_'+n.removesuffix('.pt') for n in checkpoints}
            if expected.issubset(set(roots)) and all(read(sftp,remote+'/'+n+'/SAFE_CLOSED.json') for n in expected):
                collect(train,weights=True)
                print(json.dumps(dict(complete=True,final=final,successful_evaluations=sorted(evaluated))),flush=True)
                break
        sftp.close()
    finally:
        client.close()
    time.sleep(20.)
