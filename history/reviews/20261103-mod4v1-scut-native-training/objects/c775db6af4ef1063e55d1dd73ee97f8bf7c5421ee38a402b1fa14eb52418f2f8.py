"""Freeze only changed overlay and fixed text sources; shared binaries stay put."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
code=G/'project/isaac/mod4v1_scut'
base='/home/lc01/Zonglin Li/zonglin2'
shared=base+'/tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400'
J=base+'/tasks/MOD4V1_SCUT_STEP270_2H_'+str(time.time_ns())
read=lambda p:json.loads(Path(p).read_bytes())
def put(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
plan=dict(run_id=J.rsplit('/',1)[1],remote_root=J,
    baseline_git='8654c630b403d717cc1cae707a7b7150946f9d9f',
    source_SCUT_commit='1a26356d6f591734d4f6f666f5cead1a6925da67',
    GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',
    assets=shared+'/assets',runtime=shared+'/runtime/isaac/mod4',
    runtime_manifest=shared+'/original_run_manifest.json',
    guard=shared+'/runtime/isaac/mod4/mod4v1_fresh_dr_guard.py',
    support=[shared+'/source',shared+'/sm_deps',shared+'/runtime',shared],
    profile='jump270',num_envs=80,seed=66,train_seconds=7200,exit_headroom_seconds=300,
    max_parent_seconds=7500,original_strictreserve=86412.86069250107,
    source_checkpoint=dict(path=base+'/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700/roles/E0/production/model_final_complete.pt',
        bytes=14035411,SHA='6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693'),
    initialization='SCUT weights-only finetune; strict actor35 and named critic38to78 map; fresh Adam/iteration',
    position='Selected original1mcentral platform relation, centre0,0,.38; rollpitch±.15/yaw±3.14; four sides .5m away; height270mm',
    task_differences=['Enhanced MOD4v1 USD and fullDR physics','single270mm specialized course instead of rough curriculum',
        'jump270 reward profile from8654 plus explicit spawn relation','Mature MOD4 E0 rather than SCUT robot weights'],
    exact_published_full_training_reproduction=False,
    same_original_canonical=True,new_budget_or_refund=False,
    independent_evaluation='first80 controls400 seed9137 newDR actual400Hz all80 manifold and selected actual body poses')
files=[]
def add(path,relative):
    raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw.decode('utf-8-sig'))
    files.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
for name in ['__init__.py','train.py','config.py','sdk.py','rewards.py','commands.py','upstream.py','checkpoint.py','acceptance.py','math_ops.py','course.py','finetune.py','evaluate.py','SOURCES.json','SOURCES_EXTENSION.json']:
    add(code/name,'package/mod4v1_scut/'+name)
for name in ['owner.py','entry.py']:add(N/name,name)
registry=read(code/'SOURCES.json')['files'];registry.update(read(code/'SOURCES_EXTENSION.json')['files'])
paths={}
required=['base_env','state_base','airborne','jump_takeoff','step_up','stair','state_manager','trained_env','trained_agent','commands','parent_env']
for key in required:
    row=registry[key];p=Path(row['path']);raw=p.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==row['sha256']
    relative='pinned_text/'+row['sha256']+p.suffix
    paths[key]=J+'/'+relative
    add(p,relative)
put(N/'SOURCE_PATHS.json',paths);add(N/'SOURCE_PATHS.json','SOURCE_PATHS.json')
put(N/'PLAN.json',plan);add(N/'PLAN.json','PLAN.json')
manifest=dict(kind='MOD4V1_SCUT_SMALL_OVERLAY_NO_MODELS',files=files,
    shared_runtime_root=shared,shared_asset_and_model_not_copied=True)
put(N/'INDEX_SOURCE_FROZEN.json',manifest)
print(json.dumps(dict(remote=J,files=len(files),upload_bytes=sum(x['bytes']for x in files),
    INDEX_SHA=hashlib.sha256((N/'INDEX_SOURCE_FROZEN.json').read_bytes()).hexdigest()),indent=2))
