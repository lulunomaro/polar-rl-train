from pathlib import Path
import os,json,time,hashlib,ast,shutil
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'v8_payload'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not Q.exists();v=json.loads((R/'V7_THREE_FINAL_MODELS_EXACT_UPDATES_COST_EXIT_LOCAL_CPU_ACTUAL.json').read_bytes());assert v['passed'];actual=json.loads((R/'HOURLY2223_V7_THREE_ACTUAL_FINAL_MODELS_COST_EXIT_RESOURCES_READONLY_ACTUAL.json').read_bytes());assert actual['canonical']['active'] is None and all(not x['actual_held'] for x in actual['canonical']['actual_two_fcntl']);rng=torch.get_rng_state().clone();Q.mkdir();specs=[]
 for key in ('curb','e2','recovery'):
  b=Q/key;shutil.copytree(D/'v7_payload'/key,b);row=v['experts'][key];old=json.loads((b/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());source=b/'job0/source'/old['source_filename'];shutil.copy2(row['local_path'],source);step=row['all17Adam_after'];cap=3600. if key=='recovery' else 5400.;helper=b/'three_expert_helpers_v2.py';helper.write_text(helper.read_text('utf8').replace('PORT=29746','PORT=29747'),encoding='utf8');s=(b/'three_expert_finite_owner_node_v7.py').read_text('utf8').replace('Linux_THREE_INDEPENDENT_HEALTHY_BLOCKS_CORRECTED_E3_V7_','Linux_THREE_INDEPENDENT_V7_FINAL_SOURCES_HEALTHY_BLOCKS_V8_');(b/'three_expert_finite_owner_node_v8.py').write_text(s,encoding='utf8')
  for name in (('recovery_worker.py',) if key=='recovery' else ('native_admission_worker.py','production_worker.py')):
   p=b/name;s=p.read_text('utf8').replace(str(old['source_Adamstep']),str(step))
   if key=='recovery':s=s.replace("go['max_parent_seconds']==1800","go['max_parent_seconds']==task['max_parent_seconds']")
   p.write_text(s,encoding='utf8')
  if key=='curb':
   p=b/'job0/runtime/isaac/mod4/curb35_checkpoint.py';s=p.read_text('utf8');assert old['source_SHA'] in s;s=s.replace(old['source_SHA'],row['SHA']);p.write_text(s,encoding='utf8')
  if key=='recovery':
   s=(D/'native_CPU_corrected_references_v6.py').read_text('utf8').replace('639560',str(step)).replace('NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json','NATIVE_ALL_ROWS_CPU_ADMITTED.json').replace('original_GPU_observer_and_fixed_raw_absolute_checks_still_rejected=True','legacy_absolute_checks_reported_separately=True,same_corrected_CPU_reference_protocol_as_V6=True').replace('original_FP32_rejection_retained=True','saved_V3_original_FP32_rejection_preserved_as_history=True');(b/'native_CPU.py').write_text(s,encoding='utf8')
  p=b/'job0'/('TASK_CURB35.json' if key=='curb' else 'TASK.json');task=json.loads(p.read_bytes());task.update(source_SHA=row['SHA'],source_Adamstep=step,max_parent_seconds=cap,remaining_scope_cap_seconds=cap,scope='New finite healthy continuation after real V7 FINAL/CPU/cost/exit closure, approved master same-stage overlap and human maximum-use instruction',prior_V7_actual_cost_seconds=row['actual_charged_seconds'],prior_costs_not_refunded_or_reused=True,skill_qualification_not_inferred=True);p.write_text(json.dumps(task,indent=2),encoding='utf8');ck=torch.load(source,map_location='cpu',weights_only=False);counts=[0,0]
  def walk(x):
   if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
   elif isinstance(x,dict):
    for z in x.values():walk(z)
   elif isinstance(x,(list,tuple)):
    for z in x:walk(z)
  walk(ck);assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17 and {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={step};spec={k:old[k] for k in ('key','source_filename','native_controls','GPU_UUID','native_script','production_script')};spec.update(source_SHA=H(source),source_Adamstep=step,source_schema_counts=counts,max_parent_seconds=cap,exit_headroom_seconds=300,reuse_admitted_native=False,all_native_new_weights_source_scope=True)
  files=[]
  for p in sorted(b.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p.name=='CONTINUATION_COMPLETE_MANIFEST_V2.json':continue
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   files.append(dict(relative=p.relative_to(b).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  mf=b/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(dict(spec,files=files),indent=2),encoding='utf8');specs.append(dict(spec,manifest_SHA=H(mf),files=len(files)))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_only=True,authority='Approved master v1.3 healthy same-stage finite blocks <=2h, human continue original plan and maximum meaningful three4090 utilization',CURB_E2_90min_E3_60min_engineering_caps_not_new_budget=True,all_prior_V7_6478point6810648441315_actual_seconds_retained=True,original_global_budget1188000_and7extensions_unchanged=True,each_source_new_native_CPU_required_before_PPO=True,no_new_terrain_speed_reward_DR_hardware_or_native_replay=True,E3_same_disclosed_corrected_numerical_reference_protocol=True,E3_actual_new_old_absolute_differences_reported_not_forced_false=True,learning_not_skill_qualification=True,frozen=specs,CPU_RNG_unchanged0CUDA0optimizer=True);p=R/'V8_FINAL_THREEWAY_SOURCE_MANIFEST_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
