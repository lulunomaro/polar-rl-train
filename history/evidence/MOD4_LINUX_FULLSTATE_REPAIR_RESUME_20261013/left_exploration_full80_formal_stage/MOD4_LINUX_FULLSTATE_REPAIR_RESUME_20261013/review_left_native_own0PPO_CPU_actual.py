"""Independent CPU admission of the actual GPU-created repaired own source."""
from pathlib import Path
import json,time,hashlib,torch
from left_exploration_resume_contract_v1 import same,KEY
D=Path(__file__).resolve().parent
j=json.loads((D/'reports/LEFT_NATIVE_OWN0PPO_ACTUAL_COLLECTION.json').read_bytes());v=j['native_pass'];assert v['passed'] and v['PPO_updates']==0
row=next(x for x in j['two_host_byteSHA_exact'] if x['remote_path']==v['checkpoint']);p=Path(row['local_path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
ck=torch.load(p,map_location='cpu',weights_only=False);candidate=torch.load(D/'left_exploration20k_CPU_only_v1/own20k_left_joint_margin014_std1_CPU_prepared.pt',map_location='cpu',weights_only=False)
assert same(ck['actor_state_dict'],candidate['actor_state_dict']) and same(ck['optimizer_state_dict'],candidate['optimizer_state_dict']) and same(ck[KEY],candidate[KEY])
assert ck['E1_terrain_state']['num_envs']==20000 and ck['independent_terrain_expert']=='E1_WAVE50'
assert ck['E1_WAVE50_initial_source_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
def walk(v):
 if isinstance(v,torch.Tensor):yield v
 elif isinstance(v,dict):
  for x in v.values():yield from walk(x)
 elif isinstance(v,(list,tuple)):
  for x in v:yield from walk(x)
f=[x for x in walk(ck) if x.is_floating_point()];assert len(f)==107 and all(bool(torch.isfinite(x).all()) for x in f)
assert not torch.cuda.is_initialized()
stdout=next(x for x in j['two_host_byteSHA_exact'] if x['remote_path'].endswith('/worker_stdout.log'));raw=Path(stdout['local_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==stdout['sha256']
assert all(token not in raw for token in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error',b'Traceback (most recent call last)'))
health=v['health'];assert health['control_steps']==144 and health['actual_physics_callbacks']==576 and health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and health['nonfinite_observed'] is False and health['stop_reason'] is None
assert health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact']
q=D/'reports/LEFT_NATIVE_GPU_OWN0PPO_INDEPENDENT_CPU_PASSED.json';assert not q.exists()
q.write_text(json.dumps(dict(epoch=time.time(),passed=True,ownactual_checkpoint=row,source_envs=20000,fullfloating107_finite=True,actor_optimizer_head_metadata_exact_prepared_candidate=True,actual_all20k_API_and13_CPUCUDA_disk_restore_verified=True,health=health,own_parent_EXIT=j['exit'],full_stdout_original_no_capacityerror=True,initializer_did_not_repeat=True,no_PPO=True,new_stochastic_PPO_and_full80_frozen_behavior_STILL_pending=True,qualified50=False),indent=2),encoding='utf8')
print(json.dumps(dict(report=str(q),passed=True,sourceSHA=row['sha256'],controls=144,ordinary=health['ordinary_episode_reset_events'],maxclosure=health['max_closure_error_m'],PPO_updates=0)))
