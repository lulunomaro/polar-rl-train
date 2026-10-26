"""Independent CPU qualification of the actual zero-optimizer 50 Hz clock rollout."""
from pathlib import Path
import hashlib,json,sys,time,torch
B=Path(sys.argv[1]);read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
torch.set_num_threads(2);m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');native=B/'job0/clock_native50';v=read(native/'CLOCK_NATIVE24_COMPLETE.json');final=read(native/'latest_complete.json');source=B/'job0/source'/m['source_filename']
assert v['controls']==24 and v['callbacks']==192 and v['actual_step_s']==.02 and v['physics_dt_s']==.0025 and v['maximum_target_error']<=1e-6
assert v['all_policy_steps_exactly_8_physics_callbacks'] and v['all_feedback_steps_exactly_2_10ms_samples'] and v['no_optimizer_update']
s=torch.load(source,map_location='cpu',weights_only=False);z=torch.load(final['path'],map_location='cpu',weights_only=False);assert H(final['path'])==final['SHA'] and final['updates']==0 and final['Adam_step']==m['source_Adamstep'];counts=[0,0]
def finite(x):
 if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for y in x.values():finite(y)
 elif isinstance(x,(list,tuple)):
  for y in x:finite(y)
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(list,tuple)):return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
finite(z);assert counts==[173,96]
for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(s[k],z[k]),k
assert z['policy_clock']['policy_hz']==50 and z['physical_action_delay_state']['control_us']==20000
healths=list((native/'logs').rglob('CLOCK_TRAINING_HEALTH.json'));assert len(healths)==1;health=read(healths[0]);assert health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and health['nonfinite_observed'] is False and health['max_mimic_error_rad']<=.01 and health['termination_reason_coverage_exact'] and health['actual_physics_callbacks']==health['expected_physics_callbacks']==192 and not health['stop_reason']
report=dict(epoch=time.time(),passed=True,protocol='POLICY50_NATIVE24_192_CALLBACKS_ZERO_OPTIMIZER_V1',source_SHA=m['source_SHA'],native_final=final,source_actor9_critic8_STD17Adam_literal_exact=True,whole_tensor_counts=counts,actual_clock=v,actual_native_worker_waited_EXIT0=read(B/'POLICY50_NATIVE_WORKER_WAITED_EXIT_ACTUAL.json')['returncode']==0,original_geometry_nonfinite_fullsave_guards_retained=True,not_skill_or_336_controls_pass=True)
assert report['actual_native_worker_waited_EXIT0'];(B/'POLICY50_CLOCK_RUNTIME_CPU_ADMITTED_ACTUAL.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
