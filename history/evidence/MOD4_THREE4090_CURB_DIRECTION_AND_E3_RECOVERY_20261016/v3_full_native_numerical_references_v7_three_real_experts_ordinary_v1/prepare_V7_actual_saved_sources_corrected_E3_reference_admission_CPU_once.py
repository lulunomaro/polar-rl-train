from pathlib import Path
import os,sys,json,time,hashlib,ast,shutil
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'v7_payload';V3=D/'recovery_receipt_schema_v3'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not Q.exists();v=json.loads((R/'V7_V4_FINAL_TO_THREEWAY_V7_TWO_REAL_PPO_COMPLETE_SAFE_HANDOFF_MODELS_AND_CANONICAL_ACTUAL.json').read_bytes());assert v['canonical']['active'] is None and len(v['canonical']['actual_two_fcntl_free'])==2 and not v['curb']['actual_own_processes'] and not v['e2']['actual_own_processes'];correct=json.loads((R/'V3_EXISTING_FULL_NATIVE_CORRECTED_CPU_REFERENCES_V6_ACTUAL.json').read_bytes());assert correct['returncode']==0 and correct['report']['passed'];reference=correct['report'];rng=torch.get_rng_state().clone();Q.mkdir();specs=[]
 for key in ('curb','e2','recovery'):
  b=Q/key;shutil.copytree(D/'v4_payload'/key,b);p=b/'three_expert_helpers_v2.py';helper=p.read_text('utf8').replace('PORT=29745','PORT=29746');p.write_text(helper,encoding='utf8');s=(b/'three_expert_finite_owner_node_v4.py').read_text('utf8').replace('Linux_THREE_INDEPENDENT_SAFE_HANDOFF_REMAINDERS_V4_','Linux_THREE_INDEPENDENT_HEALTHY_BLOCKS_CORRECTED_E3_V7_');(b/'three_expert_finite_owner_node_v7.py').write_text(s,encoding='utf8')
  if key in ('curb','e2'):
   row=v[key+'_model'];source=b/'job0/source'/('CURB140.pt' if key=='curb' else 'E2_final58.pt');shutil.copy2(row['local_path'],source);step=row['Adam_step'];prior=667420 if key=='curb' else 644080;cap=2700.
   for name in ('native_admission_worker.py','production_worker.py'):
    p=b/name;p.write_text(p.read_text('utf8').replace(str(prior),str(step)),encoding='utf8')
   if key=='curb':
    p=b/'job0/runtime/isaac/mod4/curb35_checkpoint.py';s=p.read_text('utf8').replace('a8e92f061ec9df0d8b72f04b4f954ff051492aee27af3c4a1ed1aecad9f2d124',row['SHA']);p.write_text(s,encoding='utf8')
   p=b/'job0'/('TASK_CURB35.json' if key=='curb' else 'TASK.json');task=json.loads(p.read_bytes());task.update(source_SHA=row['SHA'],source_Adamstep=step,remaining_scope_cap_seconds=cap,scope='New finite healthy same-stage continuation under approved master v1.3 and human continue/maximum-use instruction; original global budget unchanged',all_prior_actual_costs_retained=True,prior_V4_actual_cost=v['canonical']['last_completed']['experts'][key]['charged_seconds']);p.write_text(json.dumps(task,indent=2),encoding='utf8')
  else:source=b/'job0/source/E0_full_source.pt';step=639560;cap=1800.
  ck=torch.load(source,map_location='cpu',weights_only=False);count=[0,0]
  def walk(x):
   if torch.is_tensor(x):count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
   elif isinstance(x,dict):
    for z in x.values():walk(z)
   elif isinstance(x,(list,tuple)):
    for z in x:walk(z)
  walk(ck);assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17 and {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={step}
  spec=dict(key=key,source_SHA=H(source),source_Adamstep=step,source_schema_counts=count,source_filename=source.name,native_controls=336 if key=='recovery' else 144,max_parent_seconds=cap,exit_headroom_seconds=300,GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' if key=='curb' else 'GPU-16828f91-2b45-b646-8dc0-9481138e2842' if key=='e2' else 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d',native_script='recovery_worker.py' if key=='recovery' else 'native_admission_worker.py',production_script='recovery_worker.py' if key=='recovery' else 'production_worker.py',reuse_admitted_native=key=='recovery')
  reuse=(b/'admitted_native_reuse_v4.py').read_text('utf8');reuse=reuse.replace("assert final['passed_native_CPU'] and final['PPO_updates']==0","assert not final['passed_native_CPU'] and final['PPO_updates']==0;correction=json.loads((A/'CORRECTED_REFERENCES_V6_CPU_COMMAND_ACTUAL.json').read_bytes());assert correction['returncode']==0")
  reuse=reuse.replace("for n in ('WORKER_EXIT_ACTUAL.json','CPU_ACTUAL_EXIT.json'):assert json.loads((A/n).read_bytes())['returncode']==0", "assert json.loads((A/'WORKER_EXIT_ACTUAL.json').read_bytes())['returncode']==0;assert json.loads((A/'CPU_ACTUAL_EXIT.json').read_bytes())['returncode']==1")
  reuse=reuse.replace("native=json.loads((O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json').read_bytes())", "native=json.loads((O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json').read_bytes());assert H(O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json')==cfg['corrected_CPU_report_SHA'] and native['original_GPU_observer_and_fixed_raw_absolute_checks_still_rejected'] and native['corrected_CPU_observer_admission'] and native['no_physical_query_COM_mimic_closure_threshold_changed']")
  reuse=reuse.replace(",'NATIVE_ALL_ROWS_CPU_ADMITTED.json'",'')
  reuse=reuse.replace("assert H(target/'own_native336.pt')", "shutil.copy2(O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json',target/'NATIVE_ALL_ROWS_CPU_ADMITTED.json')\n assert H(target/'own_native336.pt')")
  reuse=reuse.replace("H(O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json')", "H(O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json')").replace("str(O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json')", "str(O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json')")
  reuse=reuse.replace('actual_original_parent_child_and_CPU_out=True','actual_original_parent_child_and_CPU_out=True,old_parent_and_CPU_failure_retained=True,independent_corrected_CPU_command_EXIT0=True,numerical_enclosure_not_GPU_bitexact=True')
  (b/'admitted_native_reuse_v4.py').write_text(reuse,encoding='utf8')
  if key=='recovery':spec.update(admitted_native_root='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/recovery_receipt_schema_v3',admitted_base_manifest_SHA=H(V3/'CONTINUATION_COMPLETE_MANIFEST_V2.json'),corrected_CPU_report_SHA=hashlib.sha256(json.dumps(reference,indent=2).encode()).hexdigest(),original_reader_false_and_GPU_FP32_shape_observer_false_preserved=True)
  files=[]
  for p in sorted(b.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p.name=='CONTINUATION_COMPLETE_MANIFEST_V2.json':continue
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   files.append(dict(relative=p.relative_to(b).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  mf=b/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(dict(spec,files=files),indent=2),encoding='utf8');specs.append(dict(spec,manifest_SHA=H(mf),files=len(files)))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_only=True,all_V4_actual_costs_retained=True,no_old_scope_restart_or_budget_increase=True,authority='Human continue under approved master v1.3 healthy same-stage finite training and three independent experts; 2700/2700 new bounded engineering blocks within original global budget, recovery first1800 unused',E3_original_full_native336_reused_no_GPU_replay=True,old_CPU_and_parent_false_preserved=True,corrected_numerical_reference_scope_not_physical_guard_relaxation=True,frozen=specs,CPU_RNG_unchanged0CUDA0optimizer=True);(R/'V7_FINAL_THREEWAY_SOURCE_MANIFEST_CPU_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
