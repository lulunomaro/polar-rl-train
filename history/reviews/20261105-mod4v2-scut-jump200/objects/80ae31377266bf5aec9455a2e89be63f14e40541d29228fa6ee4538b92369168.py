"""Evaluate only the surviving complete FIRST after a confirmed host reboot."""
from pathlib import Path
import hashlib,json,time,traceback
from shared_control_access import connection
N=Path(__file__).resolve().parent
A=N/'supermimic_final1940_residual025_1h'
R=A/'recovery_first1941_eval80'
read=lambda p:json.loads(Path(p).read_bytes())


def put(name,value):
    with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2)


EVAL='''from pathlib import Path
import json,sys,os,runpy
r=Path(__file__).resolve().parent;j=r.parent
p=json.loads((j/'PLAN.json').read_bytes());v=json.loads((r/'PLAN.json').read_bytes())
sys.path.insert(0,p['package_root'])
import mod4v2_scut
for path in reversed([str(j/'overlay'),*p['previous_overlay_paths']]):mod4v2_scut.__path__.insert(0,path)
os.environ['MOD4_SCUT_SOURCE_PATHS']=p['scut_source_paths']
os.environ['MOD4V2_NEWTON_MJCF']=p['mjcf_remote']
s=v['checkpoint'];module='mod4v2_scut.supermimic_evaluate'
sys.argv=[module,'--package',p['hardware_remote'],'--components',p['runtime'],
 '--reset-bank',p['reset_bank'],'--job-root',str(r/'evaluation'),
 '--checkpoint',s['path'],'--checkpoint-SHA',s['SHA'],
 '--binding',str(j/'SUPERMIMIC_BINDINGS.json')]
runpy.run_module(module,run_name='__main__')
'''

OWNER='''from pathlib import Path
import fcntl,hashlib,importlib.util,json,os,psutil,subprocess,time,traceback
r=Path(__file__).resolve().parent;j=r.parent
spec=importlib.util.spec_from_file_location('original_owner',j/'owner.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
p=json.loads((r/'PLAN.json').read_bytes());lock=None;worker=None;error=None
try:
 for expected in p['original_identities']:
  if psutil.pid_exists(expected['pid']):
   proc=psutil.Process(expected['pid'])
   assert proc.create_time()!=expected['creation']or proc.status()==psutil.STATUS_ZOMBIE
 source=Path(p['checkpoint']['path'])
 with source.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==p['checkpoint']['SHA']
 assert source.stat().st_size==p['checkpoint']['bytes']
 lock=(o.STATE/('three_expert_v2_'+p['GPU_UUID']+'.lock')).open('rb+')
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 o.put(r/'RESOURCE.json',o.resources(p['GPU_UUID']))
 with(r/'EVAL.log').open('xb')as log:
  worker=subprocess.Popen([str(j/'run-newton.sh'),'-u','-B',str(r/'evaluate.py')],cwd=r,
   env=o.environment(p['GPU_UUID']),stdout=log,stderr=subprocess.STDOUT,
   stdin=subprocess.DEVNULL,pass_fds=(lock.fileno(),),start_new_session=True)
 o.put(r/'WORKER.json',dict(pid=worker.pid,creation=psutil.Process(worker.pid).create_time()))
 rc=worker.wait();o.put(r/'WAITED.json',dict(epoch=time.time(),returncode=rc,own_waited=True))
 result=json.loads((r/'evaluation/RESULT.json').read_bytes())if(r/'evaluation/RESULT.json').exists()else None
 assert rc==0 and result and result['passed_execution']
except BaseException:
 error=traceback.format_exc();o.put(r/'ERROR.json',dict(epoch=time.time(),error=error))
finally:
 if worker is not None and worker.poll()is None:worker.wait()
 if lock is not None:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 o.put(r/'RELEASE.json',dict(epoch=time.time(),error=error,own_waited=worker is None or worker.poll()is not None,
  GPU_lock_released=True,optimizer_operations=0,canonical_reads=0,canonical_writes=0,
  original_window_not_extended=True,source_kind='Surviving FIRST1941; not a final2842 checkpoint'))
if error:raise RuntimeError(error)
'''


def main():
    R.mkdir(exist_ok=False)
    old=read(A/'PLAN.json');inspection=read(sorted((A/'reports').glob('NEWTON_INTERRUPTED_WINDOW_INSPECT_*_RETURNED.json'))[-1])
    assert all(not x['exact_alive']for x in inspection['identities'].values())
    first=read(A/'reports/FIRST_ACTUAL_RETURNED.json')['files']['production/FIRST_UPDATED.json']['checkpoint']
    assert first['SHA']in{c['SHA']for c in inspection['checkpoints']if not c['partial']}
    plan=dict(checkpoint=first,GPU_UUID=old['GPU_UUID'],original_identities=[x['expected']for x in inspection['identities'].values()],
              source_kind='Surviving FIRST1941 after reboot; original final absent',optimizer_operations=0)
    put('PLAN.json',plan)
    (R/'owner.py').write_text(OWNER,encoding='utf8');(R/'evaluate.py').write_text(EVAL,encoding='utf8')
    remote=old['remote_root']+'/'+R.name
    with connection(R,'FIRST1941_MISSING_EVAL_AFTER_REBOOT')as(c,t):
        t.code(c,t.PY72,"from pathlib import Path;import json;p=Path(v['root']);p.mkdir(exist_ok=False);print(json.dumps(dict(created=str(p))))",dict(root=remote),timeout=30)
        sf=c.open_sftp()
        try:
            for name in ('PLAN.json','owner.py','evaluate.py'):
                with sf.file(remote+'/'+name,'wx')as f:f.write((R/name).read_bytes());f.flush()
        finally:sf.close()
        put('LAUNCH_ONCE.json',dict(epoch=time.time(),source=first,training_restarts=0,missing_evaluation_only=True))
        spawn='''from pathlib import Path
import subprocess,psutil,json,time
r=Path(v['root']);j=r.parent
with(r/'OWNER.log').open('xb')as f:p=subprocess.Popen([str(j/'run-newton.sh'),'-u','-B',str(r/'owner.py')],cwd=r,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
print(json.dumps(dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),epoch=time.time())))'''
        owner=t.code(c,t.PY72,spawn,dict(root=remote),timeout=30);put('OWNER_LAUNCH.json',owner)
        snapshot='''from pathlib import Path
import psutil,json,time,hashlib
r=Path(v['root']);out={}
for name in ['RESOURCE.json','WORKER.json','WAITED.json','RELEASE.json','ERROR.json','evaluation/RESULT.json','evaluation/ALL80.json','evaluation/CONTROL_CURVES.json','evaluation/NATIVE_STARTUP.json','evaluation/APP_CLOSE_INTENT.json','evaluation/ERROR.json']:
 p=r/name
 if p.exists():out[name]=json.loads(p.read_bytes())
alive=False
if psutil.pid_exists(v['pid']):
 p=psutil.Process(v['pid']);alive=p.create_time()==v['creation']and p.status()!=psutil.STATUS_ZOMBIE
if 'RELEASE.json'in out:
 for name in ['OWNER.log','EVAL.log']:
  raw=(r/name).read_bytes();out[name]=dict(path=str(r/name),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8','replace'),complete=True)
print(json.dumps(dict(epoch=time.time(),files=out,exact_owner_alive=alive)))'''
        for count in range(90):
            result=t.code(c,t.PY72,snapshot,dict(root=remote,**owner),timeout=60)
            if 'RELEASE.json'in result['files']and not result['exact_owner_alive']:break
            time.sleep(5)
        else:put('PENDING.json',result);raise RuntimeError('Original eval owner remains responsible')
        put('FULL_RETURNED.json',result);files=result['files']
        assert files['RELEASE.json']['error']is None and files['evaluation/RESULT.json']['passed_execution']
        (R/'production').mkdir();(R/'evaluation').mkdir()
        sf=c.open_sftp();rows=[]
        try:
            for row in [first,files['evaluation/RESULT.json']['all80_manifold'],files['evaluation/RESULT.json']['actual_poses']]:
                target=R/('production'if row['path'].endswith('.pt')else'evaluation')/Path(row['path']).name
                sf.get(row['path'],str(target))
                with target.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
                assert sha==row['SHA']and target.stat().st_size==row['bytes']
                rows.append(dict(row,local_path=str(target),SHA_verified=True))
        finally:sf.close()
        put('FORMAL_TRANSFERS.json',dict(epoch=time.time(),files=rows))
    put('COMPLETED.json',dict(epoch=time.time(),complete=True,source=first,original_failed_window_preserved=True,optimizer_operations=0))
    print(json.dumps(dict(completed=True,checkpoint=first,result=files['evaluation/RESULT.json'])),flush=True)


if __name__=='__main__':
    try:main()
    except BaseException:
        if R.exists():put('CONTROL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()))
        raise
