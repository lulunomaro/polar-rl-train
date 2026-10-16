from pathlib import Path
import os,json,time,hashlib,copy,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
from e2_final112_frozen_source_guard_CPU_v1 import validate_E2_source
U=Path(__file__).resolve().parent;R=U/'reports';W=U.parent
def main():
 row=json.loads((R/'EXISTING_E2_ACTUAL_CLOSED_FULL_FINAL_COLLECTED.json').read_bytes())['model'];p=Path(row['local_path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];s=torch.load(p,map_location='cpu',weights_only=False);rng=torch.get_rng_state().clone();proof=validate_E2_source(s);negative=[]
 for name in ('sourcekind','yawcap','sourcewidth','Adamstep','NaNstd','missing_typed','actor_inputdim','fake_E1_only'):
  bad=copy.deepcopy(s)
  if name=='sourcekind':bad['E2_moving4_command_state']['kind']='E1_WAVE35'
  if name=='yawcap':bad['E2_moving4_command_state']['moving_yaw_cap']=2.
  if name=='sourcewidth':bad['owned_new_expert_task']['per_GPU_envs']=80
  if name=='Adamstep':next(iter(bad['optimizer_state_dict']['state'].values()))['step']+=1
  if name=='NaNstd':bad['actor_state_dict']['distribution.std_param'][0]=float('nan')
  if name=='missing_typed':bad.pop('physical_action_delay_state')
  if name=='actor_inputdim':bad['actor_state_dict']['mlp.0.weight']=bad['actor_state_dict']['mlp.0.weight'][:,:34]
  if name=='fake_E1_only':bad.pop('E2_moving4_command_state');bad['E1_terrain_state']={}
  try:validate_E2_source(bad)
  except (AssertionError,KeyError):negative.append(name)
  else:raise AssertionError(name)
 assert len(negative)==8 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();template=W/'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015/payload/retention_world_native_v8.py';raw=template.read_bytes();text=raw.decode();assert '[(1.0, 0.0), (-1.0, 0.0), (2.0, 0.0), (-2.0, 0.0)' in text
 report=dict(epoch=time.time(),CPU_source_guard_passed=True,actual_E2_closed112_source=dict(row,all17Adam651640=True),guard=proof,all8_bad_source_cases_rejected=negative,original_world_reader_template=dict(path=str(template),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()),original_world_low_yaw1_2_recipe_not_new_signed4_qualification=True,full_new_recipe_not_yet_materialized_or_GPU_dispatched=True,remaining_concrete_admission=['Create a separate source-specific single-actor35 adapter using this E2metadata guard; never invent E1_terrain_state or claim20kDR restored on3060.','Declare and freeze a new signed±4rad/s/worldV.5 direction recipe with15s/1500controls6000callbacks and88envs or another explicitly indexed balanced grouping; old±1/2 results are separate retained scopes.','Inspect originalbody_command/normal35/previousactualclip6/selectedreset and original world-cycle metrics; coordinate transform permitted, no liveheadingposition correction or terraintruth.','Audit actual source route/truncation, tile/ground and physical overlap before defining whole15s route; retain every original ordinary/truncation failedprefix, do not silently disable guard or award crossing viareset/teleport.','Freeze actual sources/recipe/SDK/resource/MSVCRT/ownunusedlease then newnative120/full1500 and independent saved-row CPU/query-contactCOMhardware audit; no old consumedTask/native replay.','Keep old originalS5 two-devseed/profile fair comparison and heldouts separate; do not use heldout61011/12 to tune this newsource or call new highyaw registered from oldlower-yaw totals.'],CPU_RNG_unchanged0CUDA0optimizer=True,no_new_GPU_lease_PPO_budget_or_actual_skill_claim=True);p=R/'E2_CLOSED112_FROZEN_SOURCE_GUARD_8NEGATIVE_AND_NEW_SIGNED4_SCOPE_CPU_PREPARED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(E2_source_guard_CPU_passed=True,bad_source_cases=8,full_signed4_native_or_full_eval=False)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E2_FROZEN_SOURCE_GUARD_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_target_GPU_or_budget_mutation=True),f,indent=2)
  raise
