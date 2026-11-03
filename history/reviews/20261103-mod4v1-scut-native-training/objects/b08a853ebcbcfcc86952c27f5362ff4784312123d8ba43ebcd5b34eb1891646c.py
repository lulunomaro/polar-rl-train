"""Finite same-final diagnostic after the original peer releases shared locks.

Source-only overlay; no new training window, budget mutation or old once replay.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,time,traceback

N=Path(__file__).resolve().parent;A=N/'env20000_1h';D=A/'action_clip_eval1';R=D/'reports'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda raw:hashlib.sha256(raw).hexdigest()
def put(path,value):
    with Path(path).open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2)

WRAPPER='''from pathlib import Path
import fcntl,json,os,runpy,sys,time,traceback,importlib.util,subprocess,hashlib
r=Path(__file__).resolve().parent;plan=json.loads((r/'PLAN.json').read_bytes());j=Path(plan['closed_root'])
spec=importlib.util.spec_from_file_location('original_closed_owner',j/'owner.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
locks=[];worker=None;error=None
try:
 for p in [*o.b.LOCKS,o.C.parent.parent/('three_expert_v2_'+plan['GPU_UUID']+'.lock'),o.C.parent.parent/'finite_environment_validation.lock']:
  f=p.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert json.loads(o.C.read_bytes())['active_segment']is None
 peer=json.loads((Path(plan['peer_root'])/'OWNER_EXIT.json').read_bytes())
 assert peer['all_own_waited']and peer['original_cost_settled']and peer['original_leases_released']
 o.resource(plan['GPU_UUID'])
 manifest=json.loads((r/'INSTALL_MANIFEST.json').read_bytes())
 for row in manifest:
  p=r/row['relative'];assert len(p.read_bytes())==row['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 task=json.loads((j/'TASK.json').read_bytes())
 env=o.environment(plan['GPU_UUID']);env['MOD4_SCUT_SOURCE_PATHS']=str(j/'SOURCE_PATHS.json')
 code="import sys,runpy;sys.path.insert(0,"+repr(task['package_root'])+");import mod4v1_scut;mod4v1_scut.__path__[:0]="+repr([str(r/'overlay'),task['module_overlay']])+";runpy.run_module('mod4v1_scut.evaluate',run_name='__main__')"
 c=plan['checkpoint'];args=['--assets',task['assets'],'--runtime',task['runtime'],'--runtime-manifest',task['runtime_manifest'],'--guard',task['guard'],'--profile','jump270','--job-root',str(r/'evaluation'),'--checkpoint',c['path'],'--checkpoint-SHA',c['SHA'],'--repair-unclipped-v2']
 for path in task['support']:args+=['--support',path]
 with (r/'WORKER.log').open('xb')as log:
  worker=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B','-c',code,*args],env=env,cwd=r,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=tuple(f.fileno()for f in locks))
 o.put(r/'WORKER_IDENTITY.json',o.b.ident(worker.pid));rc=worker.wait()
 o.put(r/'WORKER_WAITED.json',dict(epoch=time.time(),returncode=rc,own_waited=True))
 if rc:raise RuntimeError('Actual diagnostic worker failed: '+str(rc))
except BaseException:
 error=traceback.format_exc();o.put(r/'ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error))
finally:
 if worker is not None and worker.poll()is None:worker.wait()
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 o.put(r/'RELEASE.json',dict(epoch=time.time(),error=error,all_own_waited=worker is None or worker.poll()is not None,locks_released=True,optimizer_operations=0,ledger_writes=0))
'''

def prepare():
    D.mkdir();R.mkdir()
    plan=read(A/'PLAN.json');closed=read(A/'reports/POSTROUND_FULL_RETURNED.json')['files']
    assert closed['OWNER_EXIT.json']['all_own_waited']and closed['OWNER_EXIT.json']['original_leases_released']
    peer=read('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/reports/STATUS_SCUT20_FIRST.json')
    source=[]
    for name in ('config.py','train.py','checkpoint.py','sdk.py','evaluate.py'):
        path=G/'project/isaac/mod4v1_scut'/name;raw=path.read_bytes();ast.parse(raw)
        source.append(dict(path=str(path),relative='overlay/'+name,bytes=len(raw),SHA=H(raw)))
    owner=D/'owner_eval.py';owner.write_text(WRAPPER,encoding='utf8');ast.parse(WRAPPER)
    source.append(dict(path=str(owner),relative='owner_eval.py',bytes=owner.stat().st_size,SHA=H(owner.read_bytes())))
    p=dict(kind='SAME_FINAL_CLIP6_DIAGNOSTIC',closed_root=plan['remote_root'],remote_root=plan['remote_root']+'/action_clip_eval1',
        checkpoint=closed['production/FINAL.json']['checkpoint'],GPU_UUID=plan['GPU_UUID'],
        peer_root=peer['job'],peer_identity=peer['files']['OWNER_STARTED.json']['identity'],
        peer_original_go=peer['files']['GO_PRODUCTION.json'],num_envs=80,controls_max=400,seed=9137,
        optimizer_operations=0,ledger_writes=0,source_interface='V2_unclipped',execution_interface='V3_MOD4_clip6',
        no_new_training_window=True,source_checkpoint_unchanged=True,
        actual_validation_pending=True,required_release='FreshLOCALfree, exact peer ownwaited/settled/released, canonicalNone, original authority/private/finite locks')
    put(D/'PLAN.json',p);raw=(D/'PLAN.json').read_bytes()
    source.append(dict(path=str(D/'PLAN.json'),relative='PLAN.json',bytes=len(raw),SHA=H(raw)))
    put(D/'SOURCE_FROZEN.json',dict(files=source,shared_package=plan['package_root'],prior_overlay=plan['module_overlay'],
        actual_run=False,full_tree_copy=False,new_model_copy=False))
    print(json.dumps(dict(prepared=str(D),source_files=len(source),native_pending=True)))

def revise():
    """Freeze the completed audit without overwriting the unused first plan."""
    assert not(R/'LAUNCH_ONCE.json').exists()
    old=read(D/'PLAN.json');plan=dict(old)
    plan.update(kind='SAME_FINAL_COMPREHENSIVE_REPAIR_DIAGNOSTIC',
        execution_interface='V3_MOD4_clip6_source_debugclock',
        fixes=['MOD4 E0 clip6 before physics and action history',
               'SCUT debug clock enabled flag and reward-tail timing',
               'first-episode contact maximum mask','actual spawn yaw reference',
               'pre-reset targets and termination diagnostics'],
        source_revision=2,previous_plan=dict(path=str(D/'PLAN.json'),SHA=H((D/'PLAN.json').read_bytes())))
    source=[]
    for name in ('config.py','train.py','checkpoint.py','sdk.py','evaluate.py','rewards.py','course.py'):
        path=G/'project/isaac/mod4v1_scut'/name;raw=path.read_bytes();ast.parse(raw)
        source.append(dict(path=str(path),relative='overlay/'+name,bytes=len(raw),SHA=H(raw)))
    owner=D/'owner_eval.py';raw=owner.read_bytes();ast.parse(raw)
    source.append(dict(path=str(owner),relative='owner_eval.py',bytes=len(raw),SHA=H(raw)))
    p=D/'PLAN_REV2.json';put(p,plan);raw=p.read_bytes()
    source.append(dict(path=str(p),relative='PLAN.json',bytes=len(raw),SHA=H(raw)))
    before=read(D/'SOURCE_FROZEN.json')
    put(D/'SOURCE_FROZEN_REV2.json',dict(files=source,shared_package=before['shared_package'],
        prior_overlay=before['prior_overlay'],previous_index_SHA=H((D/'SOURCE_FROZEN.json').read_bytes()),
        actual_run=False,full_tree_copy=False,new_model_copy=False))
    print(json.dumps(dict(prepared=str(D),revision=2,source_files=len(source),native_pending=True)))

def run(wait_release=False):
    spec=importlib.util.spec_from_file_location('scut_action_serial',N/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.R=R
    assert not(R/'LAUNCH_ONCE.json').exists(),'Do not replay; read own receipts'
    plan=read(D/'PLAN_REV3.json');index=read(D/'SOURCE_FROZEN_REV3.json')
    for row in index['files']:
        raw=Path(row['path']).read_bytes();assert len(raw)==row['bytes']and H(raw)==row['SHA']
    with m.connection('ACTION_CLIP_NATIVE01')as(client,d):
        code='''from pathlib import Path
import json,time,fcntl
b=Path('/home/lc01/Zonglin Li/zonglin2');cpath=b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
c=json.loads(cpath.read_bytes());peer=Path(v['peer_root']);exitpath=peer/'OWNER_EXIT.json'
e=json.loads(exitpath.read_bytes())if exitpath.exists()else None
start=json.loads((peer/'OWNER_STARTED.json').read_bytes())
same=start['identity']['pid']==v['peer_identity']['pid']and start['identity']['creation']==v['peer_identity']['creation']
ready=c['active_segment']is None and same and e is not None and e['all_own_waited']and e['original_cost_settled']and e['original_leases_released']
print(json.dumps(dict(epoch=time.time(),ready=bool(ready),canonical_active=c['active_segment'],peer_exit=e,peer_identity_matches=same,GPUscan=0,modelreads=0,physics=0)))'''
        check=d.code(client,d.PY72,code,plan,timeout=40)
        if wait_release and not check['ready']:
            put(R/'ORIGINAL_ADMISSION_INITIAL_WAIT.json',check)
            deadline=time.time()+900
            put(R/'ORIGINAL_RELEASE_FINITE_WAIT.json',dict(epoch=time.time(),deadline=deadline,
                same_controller=True,new_training_window=False,wait_holds_no_remote_locks=True,
                peer_root=plan['peer_root'],peer_identity=plan['peer_identity']))
            count=0
            while not check['ready'] and time.time()<deadline:
                if count%4==0:print(json.dumps(dict(waiting_original_release=True,
                    peer=plan['peer_root'],epoch=check['epoch'],native_started=False)),flush=True)
                time.sleep(15);count+=1
                check=d.code(client,d.PY72,code,plan,timeout=40)
        put(R/'ORIGINAL_ADMISSION_READ.json',check)
        if not check['ready']:
            print(json.dumps(dict(resource_busy=True,native_started=False)));return
        create='''from pathlib import Path
import json
p=Path(v['remote_root']);p.mkdir(exist_ok=False);(p/'overlay').mkdir();print(json.dumps(dict(created=str(p))))'''
        d.code(client,d.PY72,create,plan,timeout=40)
        sf=client.open_sftp()
        try:
            for row in index['files']:
                with sf.file(plan['remote_root']+'/'+row['relative'],'wx')as f:f.write(Path(row['path']).read_bytes())
            with sf.file(plan['remote_root']+'/INSTALL_MANIFEST.json','wx')as f:f.write(json.dumps(index['files']).encode())
        finally:sf.close()
        put(R/'LAUNCH_ONCE.json',dict(epoch=time.time(),diagnostic_only=True,plan=plan))
        start='''from pathlib import Path
import subprocess,json,time,psutil
r=Path(v['remote_root'])
with (r/'OWNER.log').open('xb')as f:p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(r/'owner_eval.py')],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
q=psutil.Process(p.pid);print(json.dumps(dict(epoch=time.time(),pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline())))'''
        launch=d.code(client,d.PY72,start,plan,timeout=40);put(R/'OWNER_LAUNCH.json',launch)
        for tick in range(90):
            query='''from pathlib import Path
import json,time,psutil
r=Path(v['root']);f={}
for name in ['GPU_ADMISSION.json','evaluation/NATIVE_STARTUP.json','evaluation/RESULT.json','evaluation/ALL80.json','evaluation/CONTROL_CURVES.json','evaluation/ERROR.json','evaluation/APP_CLOSE_INTENT.json','WORKER_WAITED.json','ORIGINAL_ERROR.json','RELEASE.json']:
 p=r/name
 if p.is_file():f[name]=json.loads(p.read_bytes())
p=r/'WORKER.log'
if p.is_file():
 with p.open('rb')as q:q.seek(max(0,p.stat().st_size-8000));f['WORKER.log']=q.read().decode('utf8','replace')
alive=False
try:q=psutil.Process(v['pid']);alive=q.create_time()==v['creation']and q.status()!=psutil.STATUS_ZOMBIE
except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),files=f,exact_owner_alive=alive)))'''
            result=d.code(client,d.PY72,query,dict(root=plan['remote_root'],**launch),timeout=40)
            if 'RELEASE.json'in result['files']and not result['exact_owner_alive']:
                put(R/'FULL_RETURNED.json',result);evaluation=result['files'].get('evaluation/RESULT.json')
                if evaluation:
                    (D/'evaluation').mkdir();sf=client.open_sftp();transfers=[]
                    try:
                        for key in ('all80_manifold','actual_poses'):
                            item=evaluation[key];path=D/'evaluation'/Path(item['path']).name;sf.get(item['path'],str(path))
                            assert path.stat().st_size==item['bytes']and H(path.read_bytes())==item['SHA']
                            transfers.append(dict(item,local_path=str(path)))
                    finally:sf.close()
                    put(R/'TRANSFERS.json',dict(files=transfers))
                print(json.dumps(dict(result=evaluation,release=result['files']['RELEASE.json'])));return
            if tick%3==0:print(json.dumps(dict(wait=tick,files=list(result['files']))),flush=True)
            time.sleep(10)
        put(R/'FINITE_WAIT_PENDING.json',result)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','revise','run']);p.add_argument('--wait-release',action='store_true');a=p.parse_args()
    try:
        if a.mode=='run':run(a.wait_release)
        else:{'prepare':prepare,'revise':revise}[a.mode]()
    except BaseException:
        if R.exists():put(R/('ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))
        raise
