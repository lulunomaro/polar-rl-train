"""Prepare a new native modular-SDK frozen factor payload, CPU only.

No upload, parent execution, GPU launch, RPC, installed SDK mutation or budget write.
"""
from pathlib import Path
import json,hashlib,ast,time,shutil,copy
import torch,numpy as np

D=Path(__file__).resolve().parent;W=D.parent;P=D/'payload';R=D/'reports'
G=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose'
L=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
B=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400'
RUN=B/'training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339'
SOURCE=L/'attempts/same128_continue_second7200_v1/output/model_32396.pt'
SOURCE_SHA='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not P.exists();P.mkdir()
rows=[]
def capture(src,relative):
 src=Path(src);dest=P/relative;dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(src,dest);assert H(src)==H(dest)
 rows.append(dict(original_path=str(src),relative=relative,bytes=dest.stat().st_size,sha256=H(dest),exact_copy=True))
def generated(name,text):
 compile(text,name,'exec');dest=P/name;assert not dest.exists();dest.write_text(text,encoding='utf8')
 rows.append(dict(relative=name,bytes=dest.stat().st_size,sha256=H(dest),new_independent_CPU_prepared=True))
for src in (RUN/'e1_source_snapshot').rglob('*'):
 if src.is_file() and '__pycache__' not in src.parts:capture(src,'runtime/'+src.relative_to(RUN/'e1_source_snapshot').as_posix())
for n in ('robot.usd','import_contract.json'):capture(RUN/'src_snapshot'/n,'runtime/assets/'+n)
capture(RUN/'run_manifest.json','provenance/original459_run_manifest.json')
capture(SOURCE,'source/model_32396_91d.pt')
capture(G/'g4_worldmesh_query_contract.py','g4_worldmesh_query_contract.py')
capture(W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr/feedback_current_factor.py','feedback_current_factor.py')
sdk=json.loads((R/'DIRECT3060_READONLY_CPU_SDK_API_ACTUAL.json').read_text(encoding='utf8'))
sdk_expected={'versions':{p['name']:p.get('version') for p in sdk['packages']},
 'files':[{'path':r['path'],'bytes':r['bytes'],'sha256':r['sha256']} for r in sdk['SDK_source_capture']],
 'backend':'3060 Windows IsaacSim6.0.1 modular Lab6.1.14 PhysX1.1.3 native xyzw/ProxyArray',
 'only_exact_same3060_backend_pairs_allowed':True,'no_local5070_or_Linux_engine_equivalence_claim':True}
(P/'EXPECTED_INSTALLED_3060_BACKEND.json').write_text(json.dumps(sdk_expected,indent=2),encoding='utf8')
rows.append(dict(relative='EXPECTED_INSTALLED_3060_BACKEND.json',bytes=(P/'EXPECTED_INSTALLED_3060_BACKEND.json').stat().st_size,sha256=H(P/'EXPECTED_INSTALLED_3060_BACKEND.json')))

old=(G/'factor_runtime.py').read_text(encoding='utf8')
text=old.replace('from pathlib import Path\nimport json,time,hashlib,numpy as np,torch',
 '''from pathlib import Path
import json,time,hashlib,numpy as np,torch
def tensor(x):
 if isinstance(x,torch.Tensor):return x
 if hasattr(x,'torch'):return x.torch
 import warp as wp
 return wp.to_torch(x)''')
assert text!=old
text=text.replace('def cpu(x):return x.detach().cpu().numpy().copy()','def cpu(x):return tensor(x).detach().cpu().numpy().copy()')
text=text.replace('def js(x):return x.detach().cpu().tolist()','def js(x):return tensor(x).detach().cpu().tolist()')
text=text.replace(" y=cpu(x);y[...,3:7]=y[...,[4,5,6,3]];return y"," return cpu(x)")
text=text.replace('setattr(cfg.sim.physx,k,v)','setattr(cfg.sim.physics,k,v)')
text=text.replace('Rotation.from_matrix(rot).as_quat()[[3,0,1,2]]','Rotation.from_matrix(rot).as_quat()')
text=text.replace("state=r.data.root_state_w[ids].clone()","state=tensor(r.data.root_state_w)[ids].clone()")
text=text.replace('torch.equal(r.data.joint_pos,e._rough_probe_expected_q)','torch.equal(tensor(r.data.joint_pos),e._rough_probe_expected_q)')
text=text.replace("import sys\n  # Resolve peer CPU-prepared module relative to the fixed shared diagnosis root.\n  sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'io_dr'))\n  from feedback_current_factor import install","from feedback_current_factor import install")
start=text.index('def private_rng(e):');end=text.index('\n@torch.inference_mode()',start)
text=text[:start]+'''def private_rng(e):
 # Read actual generator bytes without a draw. Covers named state containers,
 # global Torch streams and command term; exact pair coverage remains auditable.
 out={};seen=set()
 def walk(v,path,depth):
  if isinstance(v,torch.Generator):
   state=v.get_state().cpu().numpy().tobytes()
   out[path]=dict(bytes=len(state),sha256=hashlib.sha256(state).hexdigest(),hex=state.hex());return
  if depth<=0 or id(v) in seen:return
  seen.add(id(v))
  if isinstance(v,dict):items=v.items()
  elif isinstance(v,(tuple,list)):items=enumerate(v)
  elif hasattr(v,'__dict__') and not isinstance(v,(torch.Tensor,np.ndarray)):items=vars(v).items()
  else:return
  for k,x in items:
   if x is e or x is e.scene or x is e.scene['robot']:continue
   walk(x,path+'/'+str(k),depth-1)
 for k in ('_mild_dr','_sensor_mild','_feedback_delay_mild','_physics_action_delay','_spring_pressure','_gas_damping','_chassis_com','_explicit_pd'):
  walk(getattr(e,k),k,8)
 walk(e.command_manager.get_term('twist'),'command/twist',8)
 states={'global/torch_cpu':torch.get_rng_state()}
 if torch.cuda.is_initialized():
  states.update({'global/cuda/'+str(i):s for i,s in enumerate(torch.cuda.get_rng_state_all())})
 for k,v in states.items():
  state=v.cpu().numpy().tobytes();out[k]=dict(bytes=len(state),sha256=hashlib.sha256(state).hexdigest(),hex=state.hex())
 return out
''' +text[end:]
text=text.replace("root_wxyz=js(state)","root_xyzw=js(state)")
text=text.replace("private_RNG_SHA=private_rng(e)","actual_captured_RNG_bytes=private_rng(e)")
assert 'cfg.sim.physx' not in text and 'root_wxyz' not in text
assert "y[...,[4,5,6,3]]" not in text
generated('factor_runtime_3060_native_v1.py',text)

worker='''"""3060 direct-local frozen-policy factor; explicit new native modular backend."""
from pathlib import Path
import argparse,os,sys,json,time,hashlib,traceback,msvcrt,importlib.metadata as metadata
D=Path(__file__).resolve().parent;L=D/'runtime';C=L/'isaac/mod4'
LOCK=Path('D:/MOD4_async_eval/worker.lock')
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser()
for key in ('checkpoint','checkpoint-sha','output','lease','case-id'):p.add_argument('--'+key,required=True)
p.add_argument('--steps',type=int,default=1500);p.add_argument('--num-envs',type=int,default=8);p.add_argument('--seed',type=int,default=20260928)
p.add_argument('--body-sign',type=int,choices=(-1,1),default=1);p.add_argument('--world-sign',type=int,choices=(-1,1),default=1)
p.add_argument('--feedback-current',action='store_true');p.add_argument('--headless',action='store_true');p.add_argument('--device',default='cuda:0')
a=p.parse_args();O=Path(a.output);ck=Path(a.checkpoint)
assert a.steps in (120,1500) and a.num_envs==8 and a.seed==20260928
assert a.checkpoint_sha=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4' and H(ck)==a.checkpoint_sha
lease=json.loads(Path(a.lease).read_bytes())
assert lease['target_host']=='10.24.4.249' and lease['namespace']=='MOD4_3060_DIRECT_FACTOR_20261013'
assert lease['GPU_lease_granted_by_root'] is True and lease['actual_shared_slot_idle_verified'] is True
assert lease['case_id']==a.case_id and lease['checkpoint_sha256']==a.checkpoint_sha
assert lease['worker_sha256']==H(__file__) and lease['factor_runtime_sha256']==H(D/'factor_runtime_3060_native_v1.py')
case={k:getattr(a,k) for k in ('steps','num_envs','seed','body_sign','world_sign','feedback_current','headless','device')}
assert lease['case_parameters']==case
manifest=json.loads((D/'SOURCE_BUNDLE_MANIFEST.json').read_bytes())
assert lease['source_bundle_manifest_sha256']==H(D/'SOURCE_BUNDLE_MANIFEST.json')
for row in manifest['file_rows']:assert H(D/row['relative'])==row['sha256']
sdk=json.loads((D/'EXPECTED_INSTALLED_3060_BACKEND.json').read_bytes())
for name,version in sdk['versions'].items():
 if version is not None:assert metadata.version(name)==version
for row in sdk['files']:assert H(row['path'])==row['sha256']
assert not O.exists() and LOCK.exists()
f=LOCK.open('r+b');f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
O.mkdir(parents=True)
def save(name,value):
 q=O/name;assert not q.exists()
 with q.open('wb') as out:out.write(json.dumps(value,ensure_ascii=False,indent=2).encode());out.flush();os.fsync(out.fileno())
save('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,case=case,lease=lease,no_PPO=True,
 frozen_fixture_original_white3_initialization=True,not_training_fullstate_resume=True,shared_original_OS_lock_acquired=True))
for k,v in json.loads((D/'provenance/original459_run_manifest.json').read_bytes())['env'].items():
 if k.startswith('RM_'):os.environ[k]=str(v)
os.environ['RM_MOD4_USD']=str(L/'assets/robot.usd');os.environ['RM_MILD_DR_PROFILE']='white_v3'
os.environ.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
sys.path[:0]=[str(C),str(D)]
# TD before Isaac is deliberate; native3060 arrays are xyzw and ProxyArray.
import torch,tensordict,numpy as np
from isaaclab.app import AppLauncher
app=None
try:
 app=AppLauncher(headless=a.headless,device=a.device).app;torch.set_num_threads(1)
 from factor_runtime_3060_native_v1 import run_factor
 a.pitch_deg=0.;a.roll_deg=0.;a.height_m=.25;a.entry_margin=.4;a.speed=.3;a.sensor_clean=False;a.policy_factor=False
 run_factor(a,O,D,save);app.close()
 save('EXIT_NATURAL.json',dict(epoch=time.time(),pid=os.getpid(),exit_code=0,app_close_returned=True,no_PPO=True))
except BaseException:
 save('ORIGINAL_ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),no_PPO=True))
 print(traceback.format_exc(),flush=True);os._exit(1)
finally:
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1);f.close()
'''
generated('paired_direct3060_factor_v1.py',worker)
parent=(G/'run_factor_once.py').read_text(encoding='utf8')
parent=parent.replace("D/'paired_geometry_pose.py'","D/'paired_direct3060_factor_v1.py'").replace("D/'factor_runtime.py'","D/'factor_runtime_3060_native_v1.py'")
parent=parent.replace("lease['owned_training_actual_exit_and_shared_lock_free_verified']", "lease['actual_shared_slot_idle_verified']")
parent=parent.replace("lease['checkpoint_path']", "lease['checkpoint_path']")
parent=parent.replace("for src in list(D.glob('*.py'))+[lease_path]:","for src in list(D.glob('*.py'))+[D/'SOURCE_BUNDLE_MANIFEST.json',D/'EXPECTED_INSTALLED_3060_BACKEND.json',lease_path]:")
parent=parent.replace("write('SOURCE_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),files=files,prelaunch=True))", "write('SOURCE_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),files=files,prelaunch=True,source_bundle_manifest_SHA=H(D/'SOURCE_BUNDLE_MANIFEST.json'),installed_backend_source_SHA_verified_by_worker=True))")
generated('run_direct3060_factor_parent_v1.py',parent)

assert H(SOURCE)==SOURCE_SHA and SOURCE.stat().st_size==1_418_935
ck=torch.load(SOURCE,map_location='cpu',weights_only=False)
def walk(v,path=''):
 if isinstance(v,torch.Tensor):yield path,v
 elif isinstance(v,dict):
  for k,x in v.items():yield from walk(x,path+'/'+str(k))
 elif isinstance(v,(list,tuple)):
  for i,x in enumerate(v):yield from walk(x,path+'/'+str(i))
tensorrows=list(walk(ck));floats=[(p,t) for p,t in tensorrows if t.is_floating_point()]
assert len(floats)==107 and all(torch.isfinite(t).all().item() for p,t in floats)
source_fields=[(p,t) for p,t in tensorrows if t.ndim and 128 in t.shape];assert len(source_fields)==99
wave=torch.nonzero(ck['E1_WAVE50_episode_direction_state']['wave_mask']).flatten();assert len(wave)==19
ids=wave[torch.linspace(0,len(wave)-1,8).round().long()];assert len(torch.unique(ids))==8
def project(v):
 if isinstance(v,torch.Tensor):
  axes=[i for i,s in enumerate(v.shape) if s==128];assert len(axes)<=1
  return v.index_select(axes[0],ids).clone() if axes else v.clone()
 if isinstance(v,dict):return {k:(8 if k in ('n','num_envs') and isinstance(x,int) and x==128 else project(x)) for k,x in v.items()}
 if isinstance(v,list):return [project(x) for x in v]
 if isinstance(v,tuple):return tuple(project(x) for x in v)
 return copy.deepcopy(v)
projected=project(ck);temp=P/'source/CPU_ONLY_PROJECTED_8_FULLSTATE_REFERENCE.pt';torch.save(projected,temp)
roundtrip=torch.load(temp,map_location='cpu',weights_only=False)
for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):
 for path,t in walk(ck[key]):assert torch.equal(t,dict(walk(roundtrip[key]))[path])
for path,t in source_fields:
 axes=[i for i,s in enumerate(t.shape) if s==128];assert torch.equal(t.index_select(axes[0],ids),dict(walk(roundtrip))[path])
rows.append(dict(relative=temp.relative_to(P).as_posix(),bytes=temp.stat().st_size,sha256=H(temp),CPU_source_reference_only_not_GPU_training_resume=True))
sourceproof=dict(epoch=time.time(),passed=True,source_checkpoint=dict(path=str(SOURCE),bytes=SOURCE.stat().st_size,sha256=H(SOURCE),float_tensors=107),
 source_num_envs=128,CPU_reference_selected_Wave_ids=ids.tolist(),selected_source_original20k_ids=[ck['LOCAL_TEMPORARY_BRANCH']['source_original_ids'][i] for i in ids.tolist()],
 perenv_fields=99,all_selected_tensor_values_exact=True,all_actor_critic_std_optimizer_global_named_private_RNG_preserved=True,CPU_disk_roundtrip_exact=True,
 CPU_reference_projection_not_used_as_GPU_training_fullstate_resume=True,
 GPU_frozen_fixture_uses_original_white3_protocol_initialization=True,source_actor_same91d_on_new_backend_only=True,
 diagnostic8batch_fixture_same_deterministic_cells_starts_q30_on_baseline_and_factor=True,
 backend='3060 modular Sim6.0.1 Lab6.1.14 PhysX1.1.3 native xyzw',no_PPO_no_GPU=True)
(R/'DIRECT3060_SOURCE91D_128_TO8_CPU_REFERENCE_PASSED.json').write_text(json.dumps(sourceproof,ensure_ascii=False,indent=2),encoding='utf8')
manifest=dict(epoch=time.time(),file_rows=rows,original459_native_runtime_copied_exact=True,
 original91d128_checkpoint_sha256=SOURCE_SHA,CPU_reference_projection_used_for_source_identity_only=True,
 native_quaternion_xyzw=True,no_local_PhysX2_bridge=True,no_installedSDK_files_changed=True,
 diagnostic_small8_resource_capacity_explicit=True,physical_solver_clock_DR_reward_query_contact_COMhardware_thresholds_not_relaxed=True,
 no_PPO_no_GPU_launch_no_RPC_no_connect210_no_budget_write=True,
 launch_requires_new_root_GPU_lease_actual_idle_shared_worker_lock=True,
 prepared_not_future_GPU_pass_or_qualifiedWave=True)
(P/'SOURCE_BUNDLE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
for row in rows:assert H(P/row['relative'])==row['sha256']
report=dict(epoch=time.time(),passed_CPU_preparation=True,files=len(rows),payload=str(P),manifest_SHA=H(P/'SOURCE_BUNDLE_MANIFEST.json'),
 worker_SHA=H(P/'paired_direct3060_factor_v1.py'),factor_runtime_SHA=H(P/'factor_runtime_3060_native_v1.py'),parent_SHA=H(P/'run_direct3060_factor_parent_v1.py'),
 actual_source91d_107_CPU_source_identity_passed=True,99_field_reference_projection_passed=True,
 SDK21_sourcefiles_current_actual_byteSHA_bound=True,native_API_source_reviewed=True,
 no_local_PhysX2_quaternion_reorder_or_Tensor_patch=True,no_GPU_launch_or_target_pass_claimed=True,
 original50_tenwave_point4approach15s1N_after200mm_data_protocol_retained=True,
 baseline_and_D3_actualinitialDR_recipe_queue_RNGbytes_comparison_required=True,
 no_other_factor_or_training_fullstate_protocol_axis=True)
(R/'DIRECT3060_NATIVE_FACTOR_PAYLOAD_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report),flush=True)
