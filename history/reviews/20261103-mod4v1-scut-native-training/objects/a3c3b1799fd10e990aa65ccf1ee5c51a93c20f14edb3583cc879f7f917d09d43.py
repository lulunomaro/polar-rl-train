"""One new evaluator source attempt, using the actual closed80 final unchanged."""
from pathlib import Path
import importlib.util,json,time,hashlib
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
spec=importlib.util.spec_from_file_location('scut_eval_serial',N/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
plan=json.loads((N/'attempt04/PLAN.json').read_bytes());job=plan['remote_root']
source=(G/'project/isaac/mod4v1_scut/evaluate.py').read_bytes()
with m.connection('EVAL80_INFERENCE_FIX01')as(client,d):
    m.put('EVAL80_INFERENCE_FIX01_ONCE.json',dict(epoch=time.time(),source_SHA=hashlib.sha256(source).hexdigest(),zero_optimizer=True))
    code='''from pathlib import Path
import json,fcntl,time
j=Path(v['job']);e=json.loads((j/'OWNER_EXIT.json').read_bytes());assert e['all_own_waited']and e['original_leases_released']
b=Path('/home/lc01/Zonglin Li/zonglin2');c=json.loads((b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']is None
p=j/'eval_inference_fix01';p.mkdir(exist_ok=False)
print(json.dumps(dict(epoch=time.time(),root=str(p),source_final=json.loads((j/'production/FINAL.json').read_bytes()))))'''
    actual=d.code(client,d.PY72,code,dict(job=job),timeout=40);m.put('EVAL80_INFERENCE_FIX01_PREPARE.json',actual)
    wrapper='''from pathlib import Path
import fcntl,json,os,runpy,sys,time,traceback,importlib.util
j=Path(__file__).resolve().parent.parent;r=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('owner_eval_only',j/'owner.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
locks=[];error=None
try:
 for p in [*o.b.LOCKS,o.C.parent.parent/('three_expert_v2_'+json.loads((j/'TASK.json').read_bytes())['GPU_UUID']+'.lock'),o.C.parent.parent/'finite_environment_validation.lock']:
  f=p.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert json.loads(o.C.read_bytes())['active_segment']is None
 task=json.loads((j/'TASK.json').read_bytes());o.resource(task['GPU_UUID'])
 # Runtime writes occur inside this evaluator process; no ledger mutation.
 os.environ.update(o.environment(task['GPU_UUID']))
 sys.path.insert(0,task['package_root']);import mod4v1_scut
 mod4v1_scut.__path__[:0]=[str(r),task['module_overlay']]
 os.environ['MOD4_SCUT_SOURCE_PATHS']=str(j/'SOURCE_PATHS.json')
 final=json.loads((j/'production/FINAL.json').read_bytes());c=final['checkpoint']
 args=['mod4v1_scut.evaluate','--assets',task['assets'],'--runtime',task['runtime'],'--runtime-manifest',task['runtime_manifest'],'--guard',task['guard'],'--profile',task['profile'],'--job-root',str(r/'evaluation'),'--checkpoint',c['path'],'--checkpoint-SHA',c['SHA']]
 for p in task['support']:args+=['--support',p]
 sys.argv=args
 runpy.run_module('mod4v1_scut.evaluate',run_name='__main__')
except BaseException:
 error=traceback.format_exc();o.put(r/'ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error));raise
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 o.put(r/'RELEASE.json',dict(epoch=time.time(),error=error,locks_released=True,optimizer_operations=0,ledger_writes=0))
'''
    sf=client.open_sftp()
    try:
        for name,raw in [('evaluate.py',source),('owner_eval.py',wrapper.encode())]:
            with sf.file(actual['root']+'/'+name,'wx')as f:f.write(raw);f.flush()
    finally:sf.close()
    start='''from pathlib import Path
import subprocess,json,time,psutil
r=Path(v['root'])
with (r/'WORKER.log').open('xb')as f:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(r/'owner_eval.py')],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=psutil.Process(p.pid).create_time())))'''
    launch=d.code(client,d.PY72,start,dict(root=actual['root']),timeout=40);m.put('EVAL80_INFERENCE_FIX01_LAUNCH.json',launch)
    print(json.dumps(launch),flush=True)
    for tick in range(45):
        code='''from pathlib import Path
import json,time,psutil
r=Path(v['root']);f={}
for name in ['evaluation/NATIVE_STARTUP.json','evaluation/RESULT.json','evaluation/ALL80.json','evaluation/ERROR.json','evaluation/APP_CLOSE_INTENT.json','ORIGINAL_ERROR.json','RELEASE.json']:
 p=r/name
 if p.is_file():f[name]=json.loads(p.read_bytes())
p=r/'WORKER.log'
if p.is_file():
 with p.open('rb')as q:q.seek(max(0,p.stat().st_size-6000));f['WORKER.log']=q.read().decode('utf8','replace')
alive=psutil.pid_exists(v['pid'])
print(json.dumps(dict(epoch=time.time(),files=f,alive=alive)))'''
        row=d.code(client,d.PY72,code,dict(root=actual['root'],pid=launch['pid']),timeout=40)
        if 'evaluation/RESULT.json'in row['files']or not row['alive']:
            m.put('EVAL80_INFERENCE_FIX01_RETURNED.json',row)
            sf=client.open_sftp()
            try:
                result=row['files'].get('evaluation/RESULT.json')
                if result:
                    target=N/'evaluation80_inference_fix01';target.mkdir()
                    for key in ['all80_manifold','actual_poses']:
                        item=result[key];path=target/Path(item['path']).name
                        sf.get(item['path'],str(path));assert path.stat().st_size==item['bytes']and hashlib.sha256(path.read_bytes()).hexdigest()==item['SHA']
            finally:sf.close()
            print(json.dumps(dict(files=list(row['files']),result=row['files'].get('evaluation/RESULT.json'),error=row['files'].get('evaluation/ERROR.json'))),flush=True);break
        if tick%3==0:print(json.dumps(dict(wait=tick,files=list(row['files']))),flush=True)
        time.sleep(10)
    else:m.put('EVAL80_INFERENCE_FIX01_PENDING.json',row)
