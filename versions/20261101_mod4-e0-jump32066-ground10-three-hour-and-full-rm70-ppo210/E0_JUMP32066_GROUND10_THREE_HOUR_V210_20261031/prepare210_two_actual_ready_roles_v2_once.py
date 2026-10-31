"""Static two-ready-role handoff before GO. No GPU/model/remote execution."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,shutil,sys,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';C=N/'control_v2'
S=T/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031'
P=N/'w35_package'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def put(n,v):write(R/n,json.dumps(v,indent=2,allow_nan=False))
def load(name,p):
 q=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m
assert not (R/'ROOT210_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
assert H(S/'adapter_v3/INDEX208_FULL_PRODUCTION_V3.json')=='5142c78e9955e1c46672c8b6c6f3d06ad9a7c578f0f48e9bcb3c19cc61edce25'
scene=read(T/'W35_RM70_ORIGINAL_CAD_SCENE_ADMISSION_V211_20261101/reports/ROOT211_ORIGINAL_CAD_SCENE_ZERO_PT_RETURNED_ACTUAL.json')
robot=read(T/'W35_RM70_OWN_MOD4_ROBOT_ADMISSION_V212_20261101/reports/ROOT212_ORIGINAL_RM70_OWN_ROBOT80_ZERO_PT_RETURNED_ACTUAL.json')
assert scene['passed'] and robot['passed'] and robot['returncode']==0 and robot['all_own_children_waited'] and robot['private_EX_released']
assert robot['result']['controls']==8 and robot['result']['physics_callbacks']==64 and robot['result']['feedback_samples']==16
cpu_path=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_fixed92_NEW_FINAL_whole_CPU_reviewer_v1/W35_FIXED92_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V2.json'
cpu=read(cpu_path);assert cpu['passed'] and cpu['new_branch_format_qualified'] and cpu['model']['SHA']=='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
assert cpu['review']['all_whole_model_tensors_finite'] and cpu['review']['Adam_step']==648360 and cpu['review']['stored_RSL_iteration']==32336
schedule=read(N/'SCHEDULE_PUBLIC.json');schedule['kind']='PARALLEL210_STATIC_E0_THREE_HOUR_AND_FULL_RM70_ONE_HOUR'
schedule['owner_root']='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_PARALLEL210_E0_3H_RM70_1H_2611v210/owner'
schedule['run_id']='PARALLEL210_E0_3H_RM70_1H_'+str(time.time_ns())
schedule['W35_208']='actual211scene and212own80robot0PT PASS, full20k restore/native24 before firstPPO still required'
wjob='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_FULL_RM70_20261101v210/w35_72'
inputs=read(S/'reports/INSTALL208_SOURCE_INPUTS.json');rows={}
for row in inputs['base_rows']+inputs['all_binaries_metadata_only']:
 p=Path(row['local_path']);rel=row['installed_relative'];assert p.stat().st_size==row['bytes']
 if p.suffix.lower() not in ('.usd','.usda','.usdc','.npz','.npy','.pt'):assert H(p)==row['SHA'],str(p)
 rows[rel]=dict(relative=rel,local_path=str(p),bytes=row['bytes'],SHA=row['SHA'])
# Only actually frozen production sources, not an active directory glob.
v3=read(S/'adapter_v3/INDEX208_FULL_PRODUCTION_V3.json')
selected=[Path(x['path']) for x in v3['files'] if Path(x['path']).suffix=='.py' and not Path(x['path']).name.startswith(('derive_','seal_'))]
for row in v3['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
for p in list((S/'source').glob('*.py'))+selected:
 rel='runtime/isaac/mod4/'+p.name;rows[rel]=dict(relative=rel,local_path=str(p),bytes=p.stat().st_size,SHA=H(p))
for relative,sha,size in [('assets/arena_collision.usdc','9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b',635933),('data/arena_collision.npz','f79dae96a377992da9901979429db4a2e1af050399091f721d75a576f5b3e954',528810)]:
 p=T.parent/'rmuc2026_training'/relative;assert p.stat().st_size==size
 rows['original_field/'+relative]=dict(relative='original_field/'+relative,local_path=str(p),bytes=size,SHA=sha,asset_relative=relative)
worker=S/'adapter_v3/worker_full208_v3.py';assert H(worker)=='f76b4fe619b75222412835232a15cf8ce16d4c4f1445ba6d070720d05080a4fd'
task=dict(kind='MOD4_W35_FULL_RM70_208_V3',run_id=schedule['run_id'],role_key='w35_72',num_envs=20000,
 source_SHA=cpu['model']['SHA'],source_bytes=17619013,source_iteration=32336,source_Adam_step=648360,source_LR=.00011390625000000003,
 original_canonical_generation='MOD4_SINGLE_WRITER72_20261026',worker_SHA=H(worker),GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',
 actual_private_EX_held_by_parent=True,actual_private_EX_scope='required at original node dispatch, actual new resource receipt is node/ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json',
 actual_scene0PT211_passed=True,actual_robot0PT212_passed=True,original_saved_W35_fullstate_CPU_proof_reused=True,
 new_RM70_geometry_course_and_xyzw_source_reviewed=True,source_read_purpose=dict(physical_byte_opens=1,decodes=1,source_bytes=17619013),
 original_frozen_W35_not_overwritten=True,full_RM70_skill_not_claimed=True,complete_SuperMimic_conversion=False)
write(P/'TASK.json',json.dumps(task,indent=2));rows['TASK.json']=dict(relative='TASK.json',local_path=str(P/'TASK.json'),bytes=(P/'TASK.json').stat().st_size,SHA=H(P/'TASK.json'))
write(N/'PACKAGE210_W35_MANIFEST.json',json.dumps(dict(kind='W35_FULL_RM70_208_V3_COMPLETE_FROZEN_SOURCE',files=list(rows.values()),
 input_model_metadata=dict(original_path=cpu['model']['path'],bytes=17619013,SHA=cpu['model']['SHA'],new_stream_copy_count=1,worker_actual_input_read_and_decode=1)),indent=2))
spec=dict(key='w35_72',execution_backend='target72',GPU_UUID=task['GPU_UUID'],source_SHA=task['source_SHA'],source_iteration=32336,source_Adamstep=648360,
 source_bytes=17619013,max_parent_seconds=3900,exit_headroom_seconds=300,num_envs=20000,no_physics_change=True,
 source_kind='MOD4_W35_FULL_RM70_208_V3',actual_scene211_passed=True,actual_robot212_passed=True,original_full_RM70_CAD_geometry=True,
 manifest_file='PACKAGE210_W35_MANIFEST.json',manifest_SHA=H(N/'PACKAGE210_W35_MANIFEST.json'),job_root=wjob,
 private_lock='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',
 python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',worker_script='runtime/isaac/mod4/worker_full208_v3.py')
schedule['experts']['w35_72']=spec;write(N/'SCHEDULE_V2_PUBLIC.json',json.dumps(schedule,indent=2))
ready=dict(epoch=time.time(),passed=True,kind=spec['source_kind'],source_SHA=task['source_SHA'],source_iteration=32336,Adam_step=648360,
 manifest_SHA=spec['manifest_SHA'],all_actor_critic_optimizer_tensors_finite=True,actual_35_38_6_shapes=True,source_fullstate_CPU_passed=True,
 actual_target0PT_waited_RC=0,actual_target0PT_controls=8,actual_target0PT_physics=64,actual_target0PT_feedback=16,target0PT_private_EX_released=True,
 actual_scene211_passed=True,actual_robot212_passed=True,original_full_RM70_CAD_geometry=True,SDK_xyzw_selected=True,original_guard_and400N50DR=True,
 historical_fullstate_CPU_proof_path=str(cpu_path),historical_fullstate_CPU_proof_SHA=H(cpu_path),
 actual20k_memory_fullrestore_native24_required_before_first_update=True,new_skill_or_SuperMimic_success=False)
write(N/'ADMISSION210_READY_W35.json',json.dumps(ready,indent=2))
C.mkdir()
for name in ('single_writer72_authority_V85M_source.py','owner210_protocol.py'):shutil.copyfile(N/'control'/name,C/name)
send=(N/'control/forwarded_original_owner_control_v1.py').read_text('utf8');needle="('h1','h1_210','e2','h1_seed28','e0_72')";assert needle in send
send=send.replace(needle,"('h1','h1_210','e2','h1_seed28','e0_72','w35_72')")
write(C/'forwarded_original_owner_control_v1.py',send)
common=(N/'control/three_slot_common_v1.py').read_text('utf8').replace("B/'SCHEDULE_PUBLIC.json'","B/'SCHEDULE_V2_PUBLIC.json'").replace('from owner210_protocol import valid_ready','from parallel210_protocol_v2 import valid_ready')
write(C/'three_slot_common_v1.py',common);shutil.copyfile(N/'parallel210_protocol_v2.py',C/'parallel210_protocol_v2.py')
owner=(N/'control/mixed210_finite_owner_authority72.py').read_text('utf8').replace('from owner210_protocol import validate_schedule,flat_go_fields','from parallel210_protocol_v2 import validate_schedule,flat_go_fields')
owner=owner.replace("set(specs)=={'e0_72'}","set(specs)=={'e0_72','w35_72'}")
write(C/'parallel210_finite_owner_authority72.py',owner)
node=(N/'control/mixed210_fullstate_slot_node.py').read_text('utf8')
old='go["literal_original_fudan_JUMP"]';assert old in node
node=node.replace(old,'(go.get("literal_original_fudan_JUMP") if spec["key"]=="e0_72" else go.get("genuine_W35_full_original_RM70_course"))')
write(C/'parallel210_fullstate_slot_node.py',node)
for p in C.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
def fn(p,name):return ast.dump(next(x for x in ast.parse(p.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name==name))
for name in ('charge_values','authenticated_row','terminal'):assert fn(C/'three_slot_common_v1.py',name)==fn(N/'control/three_slot_common_v1.py',name)
assert send.replace("('h1','h1_210','e2','h1_seed28','e0_72','w35_72')",needle)==(N/'control/forwarded_original_owner_control_v1.py').read_text('utf8')
write(N/'CONTROL210_V2_MANIFEST.json',json.dumps(dict(files=[dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(C.glob('*.py'))]),indent=2))
# Cross-check the actual original-owner GO against both separate worker guards.
sys.path[:0]=[str(C),str(N/'package')]
proto=load('parallel210_source_join',C/'parallel210_protocol_v2.py');assert proto.validate_schedule(schedule)
e0=load('e0_three_hour_guard',N/'package/mixed210_task_protocol.py')
tree=ast.parse(worker.read_bytes());validate=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate')
import os,types
scope=dict(KIND=task['kind'],SHA=task['source_SHA'],BYTES=17619013,ADAM=648360,ITER=32336,LR=task['source_LR'],GENERATION='MOD4_SINGLE_WRITER72_20261026',os=os,time=types.SimpleNamespace(time=lambda:101.))
exec(compile(ast.Module(body=[validate],type_ignores=[]),str(worker),'exec'),scope)
original_gpu=os.environ.get('CUDA_VISIBLE_DEVICES');os.environ['CUDA_VISIBLE_DEVICES']=task['GPU_UUID']
joined=[];rejected=0
try:
 for key,ad in [('e0_72',read(N/'ADMISSION210_READY.json')),('w35_72',ready)]:
  sp=schedule['experts'][key];q=dict(value=ad,SHA=hashlib.sha256(json.dumps(ad,indent=2).encode()).hexdigest())
  row=dict(key=key,phase='ready',manifest_SHA=sp['manifest_SHA'],original_error=False,closed_source_CPU=q);assert proto.valid_ready(row,sp)
  g=proto.flat_go_fields(sp);g.update(run_id=schedule['run_id'],learning_started_epoch=100.,save_deadline=100.+sp['max_parent_seconds']-300,nominal_end_epoch=100.+sp['max_parent_seconds'],max_parent_seconds=sp['max_parent_seconds'],exit_headroom_seconds=300)
  if key=='e0_72':assert e0.validate_go(g,schedule['run_id'],read(N/'package/TASK210.json'),101.)
  else:
   args=types.SimpleNamespace(mode='train',num_envs=20000,out=Path(wjob)/'production',run_id=schedule['run_id'])
   scope['validate'](task,g,args,Path(wjob))
  for field,value in [('source_SHA','0'*64),('actual_target0PT_waited_RC',1),('source_fullstate_CPU_passed',False),('actual_target0PT_physics',0)]:
   bad=copy.deepcopy(ad);bad[field]=value;br=copy.deepcopy(row);br['closed_source_CPU']=dict(value=bad,SHA=hashlib.sha256(json.dumps(bad,indent=2).encode()).hexdigest());assert not proto.valid_ready(br,sp);rejected+=1
  joined.append(key)
finally:
 if original_gpu is None:os.environ.pop('CUDA_VISIBLE_DEVICES',None)
 else:os.environ['CUDA_VISIBLE_DEVICES']=original_gpu
put('ROOT210_TWO_ACTUAL_READY_ROLES_OWNER_WORKER_JOIN_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,roles=joined,ready_negatives=rejected,
 E0_learning_seconds=10800,W35_learning_seconds=3600,original_raw_charge_HMAC_body_twofcntl_unchanged=True,
 source_model_or_raw_reads=0,target0PT_not_replayed=True,fullstate_GPU_and_first_actual_update_pending=True,
 one_hour_single_role210_launch_UNUSED_superseded_before_GO=True))
print(json.dumps(dict(passed=True,roles=joined,ready_rejections=rejected,E0_hours=3,W35_hours=1)))
