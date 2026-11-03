"""Source-only E0 recovery after same-final repaired native failure; no model read."""
from pathlib import Path
import ast,hashlib,json,time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2)

Q=N/'env20000_1h/action_clip_eval1'
facts=read(Q/'reports/FULL_RETURNED.json')['files']
assert facts['RELEASE.json']['all_own_waited']and facts['RELEASE.json']['locks_released']
assert facts['evaluation/RESULT.json']['strict']==0
assert all((Q/'evaluation'/name/'RENDER_REPORT.json').exists()for name in ('recorded_native','recorded_native_late'))
A=N/'env20000_repair_e0_1h_20261104';A.mkdir();(A/'reports').mkdir()
plan=read(N/'PLAN.json');remote=read(N/'env20000_1h/PLAN.json')['remote_root']
plan.update(run_id='MOD4V1_SCUT_REPAIRED_E0_20000ENV_1H_'+str(time.time_ns()),
    remote_root=plan['remote_root']+'/env20000_repair_e0_1h_20261104',
    package_root=remote.rsplit('/',1)[0]+'/package',
    module_overlay=plan['remote_root']+'/env20000_repair_e0_1h_20261104/overlay',
    num_envs=20000,train_seconds=3600,max_parent_seconds=3900,
    resized_learning_continuation=False,
    initialization='SCUT weights-only mature enhancedMOD4v1 E0; fresh Adam/iteration, not failed-final continuation',
    repair_git='bf08f3019a9176f10d4b5bf9c7fd008b3e52c333',
    previous_failed_final=read(N/'env20000_1h/reports/POSTROUND_COMPLETED.json')['final']['checkpoint'],
    recovery_evidence=dict(repaired_samefinal_result=facts['evaluation/RESULT.json'],
        reason='F1 clip6 and F2 debugclock now actualverified; finalactor firstaxis 100% clipped,0top0strict after native replay; return matureE0 rather than repeat degraded checkpoint',
        independent80_controls_min=42,independent80_controls_mean=182.55,independent80_controls_max=399),
    light_GPU_occupancy_allowed=True,same_original_canonical=True,new_budget_or_refund=False)
put(A/'PLAN.json',plan)
owner_source=read(N/'env20000_1h/INDEX_SOURCE_FROZEN.json')['files']
oldowner=next(r for r in owner_source if r['relative']=='owner.py')
owner='''from pathlib import Path
import hashlib,json
J=Path(__file__).resolve().parent
plan=json.loads((J/'PLAN.json').read_bytes())
P=Path('''+repr(remote+'/owner.py')+''')
raw=P.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='''+repr(oldowner['SHA'])+'''
source=raw.decode('utf8')
assert source.count("if __name__=='__main__':main()")==1
source=source.replace("if __name__=='__main__':main()",'')
exec(compile(source,str(P),'exec'),globals())
def resource(uuid):
    import psutil,shutil,subprocess,time
    line=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    row=[s.strip()for s in line.split(',')]
    apps=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True).strip()
    free,used,util=int(row[2]),int(row[3]),int(row[4])
    if not(row[0]==uuid and row[1]=='NVIDIA GeForce RTX 4090'and free>15669 and(not apps or(used<=4096 and util<=30))):
        raise BlockingIOError('Selected4090 has insufficient measured capacity')
    ram=psutil.virtual_memory().available;disk=shutil.disk_usage(J).free
    if ram<=64*1024**3 or disk<=50*1024**3:raise BlockingIOError('Original host headroom required')
    return dict(epoch=time.time(),line=line,compute_apps=apps,light_occupancy_allowed=True,ram=ram,disk=disk)
if __name__=='__main__':main()
'''
ast.parse(owner);(A/'owner.py').write_text(owner,encoding='utf8',newline='\n')
entry=(N/'entry.py').read_text(encoding='utf8')
assert entry.count("str(J/'SOURCE_PATHS.json')")==1
entry=entry.replace("str(J/'SOURCE_PATHS.json')",repr(remote+'/SOURCE_PATHS.json'))
ast.parse(entry);(A/'entry.py').write_text(entry,encoding='utf8',newline='\n')
files=[]
for name in ('config.py','train.py','checkpoint.py','sdk.py','evaluate.py','rewards.py','course.py'):
    p=G/'project/isaac/mod4v1_scut'/name;raw=p.read_bytes();ast.parse(raw)
    files.append(dict(path=str(p),relative='overlay/'+name,bytes=len(raw),SHA=H(raw)))
for name in ('PLAN.json','owner.py','entry.py'):
    p=A/name;raw=p.read_bytes();files.append(dict(path=str(p),relative=name,bytes=len(raw),SHA=H(raw)))
shared=[]
original=read(N/'INDEX_SOURCE_FROZEN.json')['files']
for row in original:
    rel=row['relative']
    if rel.startswith('package/')and rel.rsplit('/',1)[-1]not in {f['relative'].rsplit('/',1)[-1]for f in files}:
        shared.append(dict(path=remote.rsplit('/',1)[0]+'/'+rel,bytes=row['bytes'],SHA=row['SHA']))
shared.append(dict(path=remote+'/owner.py',bytes=oldowner['bytes'],SHA=oldowner['SHA']))
p=Q/'SOURCE_FROZEN_REV3.json'
put(A/'INDEX_SOURCE_FROZEN.json',dict(files=files,shared_text=shared,shared_package=plan['package_root'],
    recovery_diagnostic_source_index_SHA=H(p.read_bytes()),new_tree_copy=False,new_model_copy=False,
    unchanged_reward_PPO_physics_spawn=True,CPU56_reports_reused=True))
print(json.dumps(dict(prepared=str(A),run_id=plan['run_id'],source_only_files=len(files),shared_refs=len(shared),
    source_model=plan['source_checkpoint'],native_started=False)))
