from pathlib import Path
import os,json,time,shutil,hashlib,ast,sys
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
P=Path(__file__).resolve().parent;W=P.parent;D=W/'MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016';N=W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017';Q=N/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 prior=json.loads((P/'reports/HOURLY0044_V9_FINAL152_90_CURB275_FIRST_REAL_PPO_EXACT_COST_CPU_ACTUAL_V2.json').read_bytes());assert prior['passed'] and not N.exists();N.mkdir();(N/'reports').mkdir();Q.mkdir();rng=torch.get_rng_state().clone();specs=[]
 for key in ('e2','recovery'):
  b=Q/key;shutil.copytree(D/'v9_payload'/key,b);m=json.loads((b/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());row=prior['experts'][key];source=b/'job0/source'/m['source_filename'];shutil.copy2(row['local_path'],source);step=row['all17Adam_after'];ck=torch.load(source,map_location='cpu',weights_only=False);counts=[0,0]
  def walk(x):
   if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
   elif isinstance(x,dict):
    for z in x.values():walk(z)
   elif isinstance(x,(tuple,list)):
    for z in x:walk(z)
  walk(ck);assert counts==([175,98] if key=='e2' else [173,96]) and {int(s['step']) for s in ck['optimizer_state_dict']['state'].values()}=={step}
  oldstep=m['source_Adamstep'];allowed=[]
  for name in ('native_admission_worker.py','production_worker.py','recovery_worker.py','native_CPU.py'):
   p=b/name
   if p.exists():
    old=p.read_text('utf8');new=old.replace(str(oldstep),str(step))
    if new!=old:p.write_text(new,encoding='utf8');allowed.append(name)
  p=b/'three_expert_helpers_v2.py';s=p.read_text('utf8');assert 'PORT=29748' in s;s=s.replace('PORT=29748','PORT=29752');p.write_text(s,encoding='utf8');allowed.append(p.name)
  task=b/'job0/TASK.json';t=json.loads(task.read_bytes());t.update(id='TWO72_'+key.upper()+'_SAVED152_90_HEALTHY_SAME_SCOPE_20261017',source_SHA=H(source),source_Adamstep=step,max_parent_seconds=3600,remaining_scope_cap_seconds=3600,exit_headroom_seconds=300,continuation_same_task_math_DR_geometry_hardware=True,no_new_budget=True,template_approved_GPU=False,approved_for_PPO=False);task.write_text(json.dumps(t,indent=2),encoding='utf8');allowed+=['job0/TASK.json','job0/source/'+m['source_filename']]
  for r in m['files']:
   if r['relative'] not in allowed:assert H(b/r['relative'])==r['SHA'],r['relative']
  files=[]
  for p in sorted(b.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p.name=='CONTINUATION_COMPLETE_MANIFEST_V2.json':continue
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   files.append(dict(relative=p.relative_to(b).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  spec={k:m[k] for k in ('key','source_filename','native_controls','GPU_UUID','native_script','production_script')};spec.update(source_SHA=H(source),source_Adamstep=step,source_schema_counts=counts,max_parent_seconds=3600,exit_headroom_seconds=300,reuse_admitted_native=False)
  mf=b/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(dict(spec,files=files),indent=2),encoding='utf8');spec.update(manifest_SHA=H(mf),files=len(files),prior_exact_final=row['path']);specs.append(spec)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_only=True,actual_closed_source152_and90_allfinite=True,source_actor9_STD_critic8_17Adam_not_reset=True,all_original_runtime_assets_physics_DR_reward_command_and_hardguards_byteexact=True,only_new_source_step_cap_and_control_port=True,each_unused_native144_or336_then_independent_CPU_gate_required=True,original_single_writer_must_wait_CURB275_actual_exit_canonicalNone_twofcntl_before_any_PPO=True,new_engineering_blocks_each3600_not_global_budget_extension=True,prior_all_costs_and_false_retained=True,not_frozen_skill_qualification=True,specs=specs);(N/'reports/TWO72_CLOSED_SOURCE_FULL_CPU_MANIFEST_HEALTHY_NEXTBLOCK_PREPARED_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
if __name__=='__main__':main()
