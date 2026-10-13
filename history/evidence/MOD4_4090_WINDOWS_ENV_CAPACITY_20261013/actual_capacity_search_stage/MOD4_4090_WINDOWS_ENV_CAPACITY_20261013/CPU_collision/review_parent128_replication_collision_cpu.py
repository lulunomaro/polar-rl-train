"""Read-only CPU review of existing v12 scene/state contract; no SDK import or GPU."""
from pathlib import Path
import ast,copy,hashlib,json,time
import torch

W=Path(r'C:/Users/lulu/Desktop/claude/mjcf')
T=W/'MOD4_4090_WINDOWS_TEMP20GB_20261013'
E=T/'REMOTE_ACTUAL_EVIDENCE_1791891813944594400/temporary_scope128_memory20GB_logger_ready_v12_20261013'
A=W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/runtime/isaac/mod4'
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=H(p))
def source_evidence(p,needles):
 lines=Path(p).read_text(encoding='utf8').splitlines()
 return dict(**ref(p),evidence=[dict(line=i+1,text=s) for i,s in enumerate(lines) if any(x in s for x in needles)])
def tensor_path(v,parts):
 for p in parts:v=v[int(p)] if isinstance(v,(list,tuple)) else v[p]
 return v

def main():
 assert not torch.cuda.is_initialized()
 mf=E/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';m=json.loads(mf.read_bytes())
 assert m['num_envs']==128
 current_paths={
  'temporary_worker.py':E/'payload/temporary_worker.py',
  'temporary_training_runtime.py':E/'payload/temporary_training_runtime.py',
  'temporary_state_binding.py':E/'payload/temporary_state_binding.py',
  'selected_source_projection.py':E/'payload/selected_source_projection.py',
  'mod4_task.py':A/'mod4_task.py',
  'retention_learning_env.py':A/'retention_learning_env.py',
  'wave50_direction_runtime.py':A/'wave50_direction_runtime.py',
  'wave50_route_runtime.py':A/'wave50_route_runtime.py',
  'wave50_lifetime_runtime.py':A/'wave50_lifetime_runtime.py',
  'e1_rough_recipe.py':A/'e1_rough_recipe.py',
  'e1_rough_ground.py':A/'e1_rough_ground.py',
  'e1_full_pose_reset.py':A/'e1_full_pose_reset.py',
  'interactive_scene.py':Path(r'F:/isaacsim/IsaacLab/source/isaaclab/isaaclab/scene/interactive_scene.py'),
  'interactive_scene_cfg.py':Path(r'F:/isaacsim/IsaacLab/source/isaaclab/isaaclab/scene/interactive_scene_cfg.py'),
 }
 matches=[]
 for name,p in current_paths.items():
  rows=[r for r in m['sourcefreeze_files'] if r['path'].replace('\\','/').endswith('/'+name) and '/floor_fix_source_before/' not in r['path'].replace('\\','/')]
  assert len(rows)==1,(name,len(rows))
  assert H(p)==rows[0]['sha256'] and p.stat().st_size==rows[0]['bytes'],name
  matches.append(dict(name=name,local=ref(p),actual_remote_v12_sourcefreeze=rows[0],byteSHA_exact=True))
 cfg=ast.parse(current_paths['interactive_scene_cfg.py'].read_text(encoding='utf8'))
 defaults={}
 for cl in cfg.body:
  if isinstance(cl,ast.ClassDef) and cl.name=='InteractiveSceneCfg':
   for n in cl.body:
    if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and n.target.id in ('replicate_physics','filter_collisions'):
     defaults[n.target.id]=ast.literal_eval(n.value)
 assert defaults==dict(replicate_physics=True,filter_collisions=True)
 overrides=[]
 for name in ['temporary_worker.py','temporary_training_runtime.py','mod4_task.py']:
  tree=ast.parse(current_paths[name].read_text(encoding='utf8'))
  for n in ast.walk(tree):
   if isinstance(n,(ast.Assign,ast.AnnAssign)):
    targets=n.targets if isinstance(n,ast.Assign) else [n.target]
    for x in targets:
     if isinstance(x,ast.Attribute) and x.attr in defaults:overrides.append(dict(source=name,line=n.lineno,target=ast.unparse(x)))
 assert not overrides
 sdk=source_evidence(current_paths['interactive_scene.py'],['enable_env_ids=self.cfg.filter_collisions','source_prim_path=self.env_prim_paths[0]','prim_paths=self.env_prim_paths','self.cloner.filter_collisions(','global_paths=self._global_prim_paths'])
 task=source_evidence(current_paths['mod4_task.py'],['prim_path: str = "/World/envs/env_.*/Robot"','class Mod4SceneCfg','prim_path="{ENV_REGEX_NS}/Robot/links/','enabled_self_collisions=True'])
 query=source_evidence(current_paths['e1_rough_ground.py'],['prim_root="/World/ground"','Usd.PrimRange(root)','Terrain collider belongs to a rigid body'])
 reset=source_evidence(current_paths['e1_full_pose_reset.py'],['torch.unique(xy,dim=0,return_inverse=True)','root_ground={k:v[inverse]','z=z_unique[inverse]','q = bank[\'q\'][None].repeat','robot.write_joint_state_to_sim','robot.write_root_state_to_sim'])
 terrain=source_evidence(current_paths['e1_rough_recipe.py'],['prim_path="/World/ground"','collision_group=-1'])
 source=T/'OWN_PPO_CPU_INPUTS_1791891584295189300/OWN_PPO_SAVED.pt'
 ck=torch.load(source,map_location='cpu',weights_only=False)
 b=ck['WINDOWS4090_TEMPORARY_BRANCH'];state=ck['E1_terrain_state']
 assert b['num_envs']==128 and len(set(b['source_original_ids']))==128
 assert state['spawn_xy'].shape==(128,2) and len(torch.unique(state['spawn_xy'],dim=0))==128
 assert state['reset_expected_q'].shape==(128,30)
 rng=torch.get_rng_state().clone()
 code=ast.parse(current_paths['temporary_state_binding.py'].read_text(encoding='utf8'))
 f=next(x for x in code.body if isinstance(x,ast.FunctionDef) and x.name=='perenv_inventory')
 ns=dict(torch=torch,N=128);exec(compile(ast.Module(body=[f],type_ignores=[]),'<actual_v12_inventory>','exec'),ns)
 inventory=ns['perenv_inventory'](ck);assert len(inventory)==99
 unique_assert=next(n for n in ast.walk(code) if isinstance(n,ast.Assert) and 'len(set(b[\'source_original_ids\']))' in ast.unparse(n.test))
 bad=copy.deepcopy(b);bad['source_original_ids'][1]=bad['source_original_ids'][0]
 rejected=False
 try:exec(compile(ast.Module(body=[unique_assert],type_ignores=[]),'<actual_v12_unique_source_assert>','exec'),dict(b=bad,N=128))
 except AssertionError:rejected=True
 assert rejected
 cases=[]
 for k in (2,4,8):
  ids=torch.arange(128).repeat_interleave(k);N=len(ids)
  fields=[]
  for path,shape,dtype in inventory:
   x=tensor_path(ck,path.strip('/').split('/'));axes=[i for i,n in enumerate(shape) if n==128]
   assert len(axes)==1,(path,shape)
   y=x.index_select(axes[0],ids).clone()
   assert y.data_ptr()!=x.data_ptr()
   assert torch.equal(y,x.index_select(axes[0],ids))
   # sibling rows are separate offsets, although their initial values agree.
   sibling=y.index_select(axes[0],torch.tensor([1])).clone();index=[slice(None)]*y.ndim;index[axes[0]]=0
   old=y[tuple(index)].clone();y[tuple(index)]=~old if old.dtype==torch.bool else old+1
   assert torch.equal(y.index_select(axes[0],torch.tensor([1])),sibling)
   fields.append(dict(path=path,axis=axes[0],parent_shape=list(shape),child_shape=list(y.shape),dtype=dtype,exact_repeated_selected_values_before_mutation=True,sibling_storage_independent=True))
  xy=state['spawn_xy'].index_select(0,ids);q=state['reset_expected_q'].index_select(0,ids)
  assert len(torch.unique(xy,dim=0))==128 and q.shape==(N,30)
  ancestor=[b['source_original_ids'][i] for i in ids.tolist()]
  cases.append(dict(child_envs=N,replicas_per_parent=k,unique_parent_slots=128,unique_child_slot_ids=N,
   same_worldXY_groups=128,unique_ancestor20k_source_ids=128,ancestor_ids_are_explicitly_repeated_not_new20k_origins=True,
   family_counts=[x*k for x in b['family_counts']],spawnXY_sha256=hashlib.sha256(xy.numpy().astype('<f4').tobytes()).hexdigest(),
   q30_sha256=hashlib.sha256(q.numpy().astype('<f4').tobytes()).hexdigest(),perenv99_replication=fields))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed_CPU_source_and_replication_math_only=True,no_SSH_no_SDK_import_no_GPU_no_code_mutation=True,
  original_actual_v12_manifest=ref(mf),actual_v12_source_byteSHA_matches=matches,
  parent_CPU_saved_snapshot=ref(source),snapshot_is_earlier_complete_own128_only_latest_final_SHA_binding_still_required=True,
  scene_default=defaults,no_worker_or_task_collision_filter_overrides=overrides,
  collision_filter_source=sdk,robot_and_sensor_namespace_source=task,static_global_terrain_source=terrain,
  raycast_static_terrain_only_source=query,fullpose_sameXY_unique_inverse_source=reset,
  collision_answer='The exact configured SDK CUDA replication requests different env IDs for distinct env prims, independent of worldXY. This supports overlap isolation by source contract, but actual replicated-overlap native physics has not been measured.',
  original_v12_unique_ancestor_assert=dict(line=unique_assert.lineno,test=ast.unparse(unique_assert.test),original_duplicate_fixture_rejected=rejected),
  copied128_to_new_scope_must_not_pass_as_original_same128=True,
  actual_replication_cases=cases,actor_critic_std_Adam_not_shape128_projected=True,globalnamed_private_RNG_bytes_not_replicated_or_drawn=True,
  episode_direction_route_lifetime_requirements=[
   'New explicit capacity profile: unique child_slot_id, parent128_slot_id, replica_id, original20k ancestor id, exact parent checkpoint SHA. Repeated ancestry is permitted only in the new disclosed identity.',
   'Bind new num_envs and sequence map/origin/input SHA consistently in terrain-entry-direction-route-lifetime metadata; retain original global1600 assignment/profile/geometry SHA.',
   'Use exact99 perenv path+axis inventory. Preserve actor/critic/Adam shapes, which also contain128 dimensions.',
   'Each child owns independent perenv tensor rows; shared original RNG generator byte state is restored once, not duplicated into undocumented independent child streams. Future N-sized draws consume more bytes.',
   'Per-child physical reset changes its episode once and refreshes only that child direction/route/lifetime/DR; sibling rows remain unchanged. Same physicalepisode tow direction comes from fixed birth side, no live heading correction.',
  ],
  strict_native_needed_before_learning=[
   'Capture actual scene.cfg.replicate_physics/filter_collisions, device CUDA, unique env prim paths and authored/per-actor env ID filtering. Do not infer active filtering from file/default values alone.',
   'Audit actual articulation view row→env prim mapping, N roots, all30 joint order, body/link counts; contact views count N*2 wheel bodies with fixed per-env names. Do not silently collapse duplicate XY rows.',
   'Deliberately overlap copied siblings using exact30q/zero velocities/DR/reset maps; verify no robot↔different-env collision pairs or response while actual shared static terrain contact persists. Existing v12 native disjoint spawns do not certify this case.',
   'Original full footprint bank/clearance and independent world-mesh rays pass original1e-6 query tolerance. SameXY dedup rays use inverse mapping for every child; never dedup physical actors/contact views.',
   'Selected child reset: sibling q/root/episode/sensor-bias/delay/actionqueue/direction/route/lifetime state unchanged, callback clock preserved; all reason coverage/finite/contact integral/COM/hardware remain original.',
   'After all new-scope source strict restore markers/CUDA disk roundtrip and episode+1, benchmark original24-control PPO batches/save cost and actual peak under authorized20GB policy. Prepared CPU report is not native or throughput success.',
  ],
  retained_production_tolerances=dict(query_m=1e-6,contact_N=1.,contact_integral_mean_N=.1,COM_world_m=1e-5,closure_m=.002,mimic_rad=.01),
  same_assignment_is_global1600_not_unique_child_batch_assignment=True,
  native_replica_collision_isolation_passed=False,new_capacity_GPU_or_PPO_granted_by_this_report=False,production_qualification_claimed=False,
  Git_supplement_owner_root=True)
 out=D/'PARENT128_REPLICATION_COLLISION_AND_STATE_BINDING_CPU_ACTUAL_REVIEW.json'
 assert not out.exists();out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(out),CPU_passed=True,new_native_overlap_pending=True,replica_counts=[256,512,1024],all99_fields_checked=True,old_duplicate_sourceID_validator_rejected=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  import traceback
  out=D/('CPU_COLLISION_SOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
  out.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source=ref(__file__),no_GPU_no_SSH=True),indent=2),encoding='utf8')
  raise
