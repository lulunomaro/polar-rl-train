"""Prepare the explicitly authorized full-state second stair hour, then inventory."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import time

N=Path(__file__).resolve().parent
P=N/'env20000_scut_stairs_1h_20261104'
B=P/'attempt07';A=P/'attempt08';R=A/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda raw:hashlib.sha256(raw).hexdigest()
def put(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,ensure_ascii=False,indent=2)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def prepare():
    review=read(B/'reports/ACTUAL_PATCH07_FINAL_NATIVE_REVIEW.json')
    assert review['current_model_view_image']and review['all4_actual_images_reviewed']
    assert review['decision']['training_execution_valid']
    A.mkdir();R.mkdir()
    authorization=dict(epoch=time.time(),human_quote='打开mujoco让我看看后继续找4090训练一个小时20000环境',
        num_envs=20000,train_seconds=3600,exit_headroom_seconds=300,
        original_canonical_only=True,budget_grant_or_refund=False,
        continuation_of_valid_final=True,new_hour_explicitly_authorized=True)
    put(R/'HUMAN_CONTINUATION_AUTHORIZATION.json',authorization)
    plan=read(B/'PLAN.json')
    for key in list(plan):
        if key.startswith('original_window')or key in ['original_save_deadline','original_nominal_end_epoch','remaining_original_authorized_window','prior_final_failed_training_SHA','prior_failure']:
            plan.pop(key)
    plan.update(run_id='MOD4V1_SCUT_STAIRS_FULLSTATE_CONTINUE_20000ENV_1H_'+str(time.time_ns()),
        remote_root=plan['remote_root'].rsplit('/',1)[0]+'/attempt08',
        train_seconds=3600,max_parent_seconds=3900,exit_headroom_seconds=300,
        source_checkpoint=review['final']['checkpoint'],
        initialization='FULL_V4 same20000 full learning/DR/RNG/queues restore then one fresh physical reset; no PhysX-state continuation',
        full_state_continuation=True,source_optimizer_loaded=True,
        resized_learning_continuation=False,repair_first_axis=False,
        human_latest=authorization['human_quote'],human_authorization=authorization,
        newly_authorized_window=True,old_absolute_window_not_extended=True,
        original_window_extended=False,pending_actual_resource_selection=True,
        previous_final_review=str(B/'reports/ACTUAL_PATCH07_FINAL_NATIVE_REVIEW.json'),
        repair='No new reward or physics change; continue first valid stair final with its complete learning state',
        continuation_reason='User explicitly requests another hour after review; previous usable stair training has31updates after native setup/fixes')
    # All working modules reference the exact previous frozen overlay chain.
    plan['module_overlay']=read(B/'PLAN.json')['module_overlay']
    put(A/'PLAN.json',plan)
    (A/'owner.py').write_bytes((P/'owner.py').read_bytes())
    entry=(B/'entry.py').read_text(encoding='utf8')
    old="init=['--resize-resume' if task.get('resized_learning_continuation') else '--init-checkpoint',task['source_checkpoint']['path']]"
    new="init=['--resume' if task.get('full_state_continuation') else '--resize-resume' if task.get('resized_learning_continuation') else '--init-checkpoint',task['source_checkpoint']['path']]"
    assert entry.count(old)==1;entry=entry.replace(old,new)
    # Validate exact source bytes before restore, without decoding a second time.
    before="    init=['--resume'"
    inject="    if task.get('full_state_continuation'):\n        import hashlib\n        source=Path(task['source_checkpoint']['path'])\n        assert source.stat().st_size==task['source_checkpoint']['bytes']\n        with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==task['source_checkpoint']['SHA']\n"
    assert entry.count(before)==1;entry=entry.replace(before,inject+before)
    ast.parse(entry);(A/'entry.py').write_text(entry,encoding='utf8',newline='\n')
    previous=read(B/'INDEX_SOURCE_FROZEN.json');shared=list(previous['shared_text'])
    for row in previous['files']:
        if row['relative'].startswith('overlay/'):
            shared.append(dict(path=read(B/'PLAN.json')['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
    put(A/'SOURCE_ONLY_PREPARED.json',dict(epoch=time.time(),files=[],shared_text=shared,
        changed_files=['PLAN.json','owner.py','entry.py'],source_only=True,
        whole_tree_model_asset_copy=False,native_started=False,
        source_checkpoint=plan['source_checkpoint'],full_state_continuation=True))
    print(json.dumps(dict(prepared=str(A),full_state_continuation=True,source=plan['source_checkpoint'],PT_reads=0,physics=0)))
def inventory(refresh=False):
    target=R/('FOUR_GPU_REFRESH'+str(len(list(R.glob('FOUR_GPU_REFRESH*')))+2).zfill(2)) if refresh else R
    if refresh:target.mkdir()
    m=load('scut_continue08_fourcard',N/'check_four_gpu.py');m.R=target
    peer=read(Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/CURRENT_WORK_ORDER.json'))
    actual_peer=peer.get('remote_job');owner=peer.get('original_owner')
    if actual_peer and owner:
        m.READ=m.READ.replace('MOD4_STANDING200_SCUT_RECIPE_V20_FLAT_1793718811682640300',Path(actual_peer).name)
        m.READ=m.READ.replace('1549188',str(owner['pid'])).replace('1793718880.82',str(owner['creation']))
    m.main()
def geometry_source():
    m=load('scut_continue08_geometry_source',N/'run.py');m.R=R
    code='''from pathlib import Path
import hashlib,json,time
base=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/terrains')
files={}
for name in ['height_field/utils.py','height_field/hf_terrains.py','height_field/hf_terrains_cfg.py','terrain_generator.py','trimesh/mesh_terrains.py','trimesh/mesh_terrains_cfg.py']:
 p=base/name;raw=p.read_bytes();files[name]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8'))
print(json.dumps(dict(epoch=time.time(),files=files,PT_reads=0,SDK_imports=0,new_physics=0,GPU_probes=0,canonical_writes=0)))'''
    with m.connection('CONTINUE08_ACTUAL_TERRAIN_SOURCE')as(client,d):
        value=d.code(client,d.PY72,code,{},timeout=40)
        put(R/'ACTUAL_TERRAIN_GENERATOR_SOURCE.json',value)
    print(json.dumps(dict(read_paths=list(value['files']),PT_reads=0,physics=0)))
def launch():
    assert not(A/'INDEX_SOURCE_FROZEN.json').exists()
    assert not(R/'LAUNCH_ONCE.json').exists()
    inventories=sorted(R.glob('FOUR_GPU_REFRESH*/FOUR_GPU_HUMAN_REQUEST_ACTUAL.json'))
    inv=read(inventories[-1]) if inventories else None
    if inv is None or time.time()-inv['hosts']['72']['actual']['epoch']>120:
        inventory(refresh=True)
        inv=read(sorted(R.glob('FOUR_GPU_REFRESH*/FOUR_GPU_HUMAN_REQUEST_ACTUAL.json'))[-1])
    host=inv['hosts']['72']['actual']
    assert inv['all_clients_closed']and inv['SESSION_restored']
    apps=host['compute_apps']['stdout']
    candidates=[]
    for line in host['gpu']['stdout'].splitlines():
        fields=[item.strip()for item in line.split(',')]
        if fields[2]!='NVIDIA GeForce RTX 4090':continue
        free,used,util=map(int,fields[4:7])
        occupied=fields[1]in apps
        if free>15669 and(not occupied or(used<=4096 and util<=30)):
            candidates.append((free,not occupied,fields[1]))
    assert candidates,'No currently admissible4090 on original72 host; allfour actualavailability retained'
    chosen=max(candidates)[2]
    m=load('scut_continue08_resource',N/'run.py');m.R=R
    code='''from pathlib import Path
import json,time,fcntl,subprocess,shutil,psutil
b=Path('/home/lc01/Zonglin Li/zonglin2');C=b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
c=json.loads(C.read_bytes());locks={};ready=c['active_segment']is None
uuid=v['GPU_UUID']
for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock',C.parent.parent/('three_expert_v2_'+uuid+'.lock')]:
 try:
  with p.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  locks[str(p)]=True
 except BlockingIOError:locks[str(p)]=False
ready=ready and all(locks.values())
line=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip()for x in line.split(',')]
apps=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True).strip()
ram=psutil.virtual_memory().available;disk=shutil.disk_usage(Path(v['remote_parent'])).free
ready=ready and a[0]==uuid and a[1]=='NVIDIA GeForce RTX 4090'and int(a[2])>15669 and(not apps or(int(a[3])<=4096 and int(a[4])<=30))and ram>64*1024**3 and disk>50*1024**3
ready=ready and c['remaining_training_seconds']>86412.86069250107+3900
print(json.dumps(dict(epoch=time.time(),ready=bool(ready),canonical_active=c['active_segment'],remaining=c['remaining_training_seconds'],locks=locks,GPU_UUID=uuid,resource=dict(line=line,compute_apps=apps,ram=ram,disk=disk),PT_reads=0,physics=0,canonical_writes=0)))'''
    plan=read(A/'PLAN.json')
    label='RIGHTANGLE08_RESOURCE_READY_'+str(time.time_ns())
    with m.connection(label)as(client,d):
        value=d.code(client,d.PY72,code,dict(GPU_UUID=chosen,remote_parent=plan['remote_root'].rsplit('/',1)[0]),timeout=40)
        put(R/'RESOURCE_READY_ACTUAL.json',value)
    if not value['ready']:
        print(json.dumps(dict(blocked=True,resource=value)));return
    assert time.time()-value['epoch']<120
    plan.pop('pending_actual_resource_selection',None)
    plan['GPU_UUID']=value['GPU_UUID']
    (A/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
    prepared=read(A/'SOURCE_ONLY_PREPARED.json');files=list(prepared['files'])
    for name in ['PLAN.json','owner.py','entry.py']:
        path=A/name;raw=path.read_bytes()
        if name.endswith('.py'):ast.parse(raw)
        files.append(dict(path=str(path),relative=name,bytes=len(raw),SHA=H(raw)))
    for row in files:
        raw=Path(row['path']).read_bytes();assert len(raw)==row['bytes']and H(raw)==row['SHA']
    put(A/'INDEX_SOURCE_FROZEN.json',dict(epoch=time.time(),files=files,shared_text=prepared['shared_text'],
        overlay_resolution_order=plan['module_overlays'],source_only=True,full_state_continuation=True,
        whole_tree_model_asset_copy=False,human_new_hour_authorization=str(R/'HUMAN_CONTINUATION_AUTHORIZATION.json'),
        human_geometry_clarification=str(R/'HUMAN_RIGHT_ANGLE_STAIRS_CLARIFICATION.json')))
    controller=load('scut_continue08_original_launch',N/'repaired_training_control.py')
    controller.A=A;controller.R=R;controller.launch()
    facts=read(R/'FIRST_ACTUAL_RETURNED.json')['files']if(R/'FIRST_ACTUAL_RETURNED.json').exists()else{}
    first=facts.get('production/FIRST_UPDATED.json')
    full=facts.get('WORKER_COMPLETE.log',{})
    terms=['[error]','cooking failure','failed to cook','foundlostaggregatepairscapacity','patch buffer overflow','outofmemoryerror','dropped pair']
    errors=[line for line in full.get('text','').splitlines()if any(t in line.lower()for t in terms)]
    put(R/'FIRST_FULL_LOG_VALIDATION.json',dict(epoch=time.time(),full_log_returned=bool(full),
        errors=errors,production_error=facts.get('production/ERROR.json'),FIRST=first,
        full_restore=facts.get('production/FULL_STATE_RESTORE.json')))
    if not first:return
    assert full and not errors and 'production/ERROR.json'not in facts
    assert first['actual_onpolicy_samples']==480000 and first['rollout_controls']==24
    assert first['gradient']['actor_norm']>0 and first['gradient']['critic_norm']>0 and first['full_save']
    assert first['iteration']==plan['source_checkpoint']['iteration']+1
    restore=facts['production/FULL_STATE_RESTORE.json']
    assert restore['source_iteration']==31 and restore['optimizer_state_entries']>0
    assert restore['optimizer_step_min']==restore['optimizer_step_max']==620
    assert restore['source_SHA']==plan['source_checkpoint']['SHA']
    assert 'trimesh.mesh_terrains:inverted_pyramid_stairs_terrain'in facts['production/STARTUP.json']['course']['generator_function']
    controller.bind()
    put(R/'FIRST_NATIVE_VALIDATED_AND_COLLECTOR_BOUND.json',dict(epoch=time.time(),
        FIRST=first,full_log_errors=0,full_state_restore=restore,
        collector=read(R/'POSTROUND_EXACT_CIM.json'),FIRST_not_skill=True,
        GO=facts['GO_PRODUCTION.json']))
    print(json.dumps(dict(FIRST_valid=True,first=first,restore=restore,
        collector=read(R/'POSTROUND_EXACT_CIM.json'),GO=facts['GO_PRODUCTION.json'])))
if __name__=='__main__':
    import argparse,traceback
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','inventory','geometry_source','launch']);a=p.parse_args()
    try:globals()[a.mode]()
    except BaseException:
        if R.exists():put(R/('CONTINUATION_CONTROL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))
        raise
