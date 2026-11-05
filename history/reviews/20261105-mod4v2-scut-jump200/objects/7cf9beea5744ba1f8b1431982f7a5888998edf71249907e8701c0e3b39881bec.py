"""Complete the missing evaluation/log read after the actual owner PID race."""
from pathlib import Path
import hashlib
import json
import time
import traceback
from shared_control_access import connection

N=Path(__file__).resolve().parent
A=N/'fudan_warp_final461_1h'
R=A/'reports/eval_recovery01'
R.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_bytes())
put=lambda name,value:(R/name).write_text(json.dumps(value,indent=2),encoding='utf8')

OWNER='''from pathlib import Path
import fcntl,importlib.util,json,os,subprocess,time,traceback,psutil
r=Path(__file__).resolve().parent;j=r.parent
spec=importlib.util.spec_from_file_location('original_direct_owner',j/'owner.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
plan=json.loads((j/'PLAN.json').read_bytes());lock=None;worker=None;error=None
try:
 release=json.loads((j/'OWNER_EXIT.json').read_bytes())
 assert release['all_own_waited'] and release['original_leases_released']
 assert release['error'] and 'psutil.ZombieProcess' in release['error']
 close=json.loads((j/'production/APP_CLOSE_INTENT.json').read_bytes())
 assert close['env_closed'] and close['error'] is None and close['final_exists']
 assert not (j/'evaluation').exists()
 lock=(o.STATE/('three_expert_v2_'+plan['GPU_UUID']+'.lock')).open('rb+')
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 o.put(r/'RESOURCE.json',o.resource(plan['GPU_UUID']))
 with(r/'EVAL.log').open('xb')as log:
  worker=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(j/'entry.py'),'evaluate'],cwd=j,env=o.environment(plan['GPU_UUID']),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=(lock.fileno(),),start_new_session=True)
 o.put(r/'WORKER.json',dict(pid=worker.pid,creation=psutil.Process(worker.pid).create_time()))
 rc=worker.wait();o.put(r/'WAITED.json',dict(epoch=time.time(),returncode=rc,own_waited=True))
 result=json.loads((j/'evaluation/RESULT.json').read_bytes()) if(j/'evaluation/RESULT.json').exists()else None
 assert rc==0 and result and result['passed_execution'] and not(j/'evaluation/ERROR.json').exists()
except BaseException:
 error=traceback.format_exc();o.put(r/'ERROR.json',dict(epoch=time.time(),error=error))
finally:
 if worker is not None and worker.poll()is None:worker.wait()
 if lock is not None:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 o.put(r/'RELEASE.json',dict(epoch=time.time(),error=error,own_waited=worker is None or worker.poll()is not None,GPU_lock_released=True,model_final_unchanged=True,optimizer_operations=0,canonical_reads=0,canonical_writes=0))
if error:raise RuntimeError(error)
'''


def main():
    assert not(R/'LAUNCH_ONCE.json').exists()
    plan=read(A/'PLAN.json');j=plan['remote_root'];remote=j+'/eval_recovery01'
    with connection(R,'WARP620_MISSING_EVAL')as(client,t):
        code='''from pathlib import Path
import json,psutil,hashlib,time
j=Path(v['job']);r=j/'eval_recovery01';r.mkdir(exist_ok=False)
assert not(j/'evaluation').exists()
out={}
for n in ['WORKER.log','OWNER.log']:
 p=j/n;raw=p.read_bytes();out[n]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8','replace'))
for n in ['production/FINAL.json','production/APP_CLOSE_INTENT.json','OWNER_EXIT.json']:
 out[n]=json.loads((j/n).read_bytes())
print(json.dumps(dict(epoch=time.time(),files=out)))'''
        actual=t.code(client,t.PY72,code,dict(job=j),timeout=45)
        put('CLOSED_TRAIN_AND_COMPLETE_LOGS.json',actual)
        sf=client.open_sftp()
        try:
            with sf.file(remote+'/owner.py','wx')as f:f.write(OWNER.encode());f.flush()
        finally:sf.close()
        put('LAUNCH_ONCE.json',dict(epoch=time.time(),source_SHA=actual['files']['production/FINAL.json']['checkpoint']['SHA'],missing_evaluation_only=True))
        start='''from pathlib import Path
import subprocess,psutil,json,time
r=Path(v['remote'])
with(r/'OWNER.log').open('xb')as f:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(r/'owner.py')],cwd=r,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
q=psutil.Process(p.pid);print(json.dumps(dict(pid=p.pid,creation=q.create_time(),epoch=time.time())))'''
        owner=t.code(client,t.PY72,start,dict(remote=remote),timeout=30);put('OWNER_LAUNCH.json',owner)
        for tick in range(90):
            check='''from pathlib import Path
import json,psutil,time
r=Path(v['remote']);j=r.parent;out={}
for n in ['RESOURCE.json','WORKER.json','WAITED.json','RELEASE.json','ERROR.json']:
 p=r/n
 if p.exists():out[n]=json.loads(p.read_bytes())
alive=psutil.pid_exists(v['pid'])and psutil.Process(v['pid']).create_time()==v['creation']
if 'RELEASE.json'in out and not alive:
 for n in ['evaluation/RESULT.json','evaluation/ALL80.json','evaluation/CONTROL_CURVES.json','evaluation/NATIVE_STARTUP.json','evaluation/ERROR.json','evaluation/APP_CLOSE_INTENT.json']:
  p=j/n
  if p.exists():out[n]=json.loads(p.read_bytes())
 for name in ['EVAL.log','OWNER.log']:
  p=r/name
  if p.exists():out[name]=p.read_text(errors='replace')
print(json.dumps(dict(epoch=time.time(),files=out,exact_owner_alive=alive)))'''
            result=t.code(client,t.PY72,check,dict(remote=remote,**owner),timeout=45)
            if 'RELEASE.json'in result['files']and not result['exact_owner_alive']:break
            if tick%6==0:print(json.dumps(dict(wait=tick,files=list(result['files']))),flush=True)
            time.sleep(10)
        else:put('PENDING.json',result);raise RuntimeError('Original recovery owner still responsible')
        put('FULL_RETURNED.json',result)
        files=result['files'];assert not files['RELEASE.json']['error'] and files['evaluation/RESULT.json']['passed_execution']
        target=A/'evaluation';target.mkdir(exist_ok=False)
        sf=client.open_sftp();rows=[]
        try:
            for key in ['all80_manifold','actual_poses']:
                row=files['evaluation/RESULT.json'][key];p=target/Path(row['path']).name
                sf.get(row['path'],str(p))
                digest=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
                assert p.stat().st_size==row['bytes']and digest==row['SHA']
                rows.append(dict(row,local_path=str(p),SHA_verified=True))
        finally:sf.close()
        put('FORMAL_TRANSFERS.json',dict(epoch=time.time(),files=rows))
    put('COMPLETED.json',dict(epoch=time.time(),source_iteration=620,actual_eval=True))
    print(json.dumps(dict(completed=True,result=files['evaluation/RESULT.json'])),flush=True)


if __name__=='__main__':
    try:main()
    except BaseException:
        put('CONTROL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()))
        raise
