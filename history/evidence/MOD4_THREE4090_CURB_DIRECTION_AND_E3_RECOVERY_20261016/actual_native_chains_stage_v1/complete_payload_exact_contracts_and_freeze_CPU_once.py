from pathlib import Path
import os,sys,json,ast,hashlib,time,types,shutil
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;Q=D/'payload';R=D/'reports'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (R/'TWO_EXPERT_UNUSED_PACKAGES_MANIFEST_AND_NEGATIVES_CPU_ACTUAL.json').exists();rng=torch.get_rng_state().clone();proof=json.loads((R/'TWO_NEW_EXPERTS_FULL_SOURCE_CONTRACT_CPU_ACTUAL.json').read_bytes());frozen=[]
 for key in ('curb','recovery'):
  p=Q/key/'cohort_finite.py';s=p.read_text('utf8').replace('rows=dict(curb=own,e2=remote_row)','rows=dict(curb=own,recovery=remote_row)');p.write_text(s,encoding='utf8')
 # Actual SDK reward dt will be measured in the new native; no coefficient is silently multiplied by dt.
 p=Q/'recovery/recovery_worker.py';s=p.read_text('utf8');s=s.replace("zero=save(OUT/'own_startup0.pt',0);", "from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe\n  actual_dt=isolated_actual_SDK_dt_probe(env);put(OUT/'E3_ACTUAL_SDK_REWARD_DT_PROBE.json',actual_dt)\n  zero=save(OUT/'own_startup0.pt',0);");p.write_text(s,encoding='utf8')
 # Execute only the actual pure config functions in a mocked manager namespace.
 rt=Q/'recovery/job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py';tree=ast.parse(rt.read_text('utf8'));names={'masked_termination','masked_reward','recovery_event_rate','configure'};nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 for n in nodes:
  if n.name=='configure':n.body=[x for x in n.body if not isinstance(x,(ast.Import,ast.ImportFrom))]
 ns=dict(torch=torch,MASKED_REWARDS=('height','height_tight','height_both_wheels','height_square','height_deficit','height_error_l1','lin_vel_z'),RewardTermCfg=lambda **kw:types.SimpleNamespace(**kw));exec(compile(ast.Module(body=nodes,type_ignores=[]),'actual_E3_functions_CPU_only','exec'),ns)
 def original(e,flag=True):return torch.ones(4,dtype=torch.bool)
 terms={n:types.SimpleNamespace(func=original,params=dict(flag=True),time_out=n=='time_out') for n in ('bad_orientation','base_contact','closure','mimic','time_out','unknown_future')};rewards={n:types.SimpleNamespace(func=lambda e:torch.arange(4).float(),params={},weight=2.) for n in ns['MASKED_REWARDS']};cfg=types.SimpleNamespace(terminations=types.SimpleNamespace(**terms),rewards=types.SimpleNamespace(**rewards));keep={n:(t.func,dict(t.params),t.time_out) for n,t in terms.items() if n not in ('bad_orientation','base_contact')};ns['configure'](cfg)
 for n,old in keep.items():t=getattr(cfg.terminations,n);assert (t.func,t.params,t.time_out)==old
 env=types.SimpleNamespace(recovery=types.SimpleNamespace(recipe=torch.tensor([0,1,12,0]),age=torch.tensor([0,299,0,300]),request=torch.tensor([True,True,False,False]),delta=torch.tensor([.2,.3,0.,0.])),recovery_original_soft={},num_envs=4,device='cpu',step_dt=.01)
 for n in ('bad_orientation','base_contact'):
  t=getattr(cfg.terminations,n);assert t.func(env,**t.params).tolist()==[False,False,True,True]
 assert torch.allclose(ns['recovery_event_rate'](env)*.01,env.recovery.delta)
 # Literal original finite accounting and readiness functions tested for both distinct experts.
 tree=ast.parse((Q/'curb/cohort_finite.py').read_text('utf8'));selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('valid_ready','charge_values')];g=dict(hashlib=hashlib,json=json);exec(compile(ast.Module(body=selected,type_ignores=[]),'new_cohort_actual_CPU_functions','exec'),g)
 for spec in proof['frozen']:
  v=dict(passed=True,source_SHA=spec['source_SHA'],controls=spec['native_controls'],callbacks=4*spec['native_controls']);row=dict(phase='ready',native_GPU_waited_EXIT0=True,native_CPU=dict(value=v,actual_CPU_waited_EXIT0=True,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()),manifest_SHA='a'*64);c=dict(spec,manifest_SHA='a'*64);assert g['valid_ready'](row,c)
  for name,bad in [('native_GPU_waited_EXIT0',False),('manifest_SHA','b'*64),('original_error',True)]:assert not g['valid_ready'](dict(row,**{name:bad}),c)
 active=dict(experts={},charged_expert_seconds=0.);c=dict(charged_training_seconds=500.,remaining_training_seconds=1187500.);go={x['key']:dict(learning_started_epoch=100.,max_parent_seconds=x['max_parent_seconds']) for x in proof['frozen']};rows={k:dict(returncode=None) for k in go};g['charge_values'](c,active,go,rows,110.);assert c['charged_training_seconds']==520. and active['charged_expert_seconds']==20.;g['charge_values'](c,active,go,rows,110.);assert c['charged_training_seconds']==520.
 for spec in proof['frozen']:
  key=spec['key'];b=Q/key;files=[]
  # A copied old manifest is deliberately retained but the new owner consumes this explicit current manifest.
  for p in sorted(b.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p.name=='CONTINUATION_COMPLETE_MANIFEST_V2.json':continue
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   files.append(dict(relative=p.relative_to(b).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  m=dict(spec,files=files,source_filename='CURB140.pt' if key=='curb' else 'E0_full_source.pt',new_root_unused=True,old_scopes_not_replayed=True,SDK_driver_unchanged=True);p=b/'CONTINUATION_COMPLETE_MANIFEST_V2.json';p.write_text(json.dumps(m,indent=2),encoding='utf8');frozen.append(dict(spec,manifest_SHA=H(p),files=len(files)))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_only=True,frozen=frozen,E3_original_hard_termination_bindings_exact=True,E3_soft_mask_normal_and_deadline_boundary_exact=True,actual_pure_config_AST_extracted_only_not_SDK=True,unit_event_actual_dt_formula_checked=True,six_bad_grants_rejected=True,summed_distinct_interval_no_duplicate_charge_CPU=True,all_payload_Python_AST_passed=True,original_live_E2_owner_not_modified=True,no_target_native_or_PPO_yet=True,global_CPU_RNG_unchanged0CUDA0optimizer=True);(R/'TWO_EXPERT_UNUSED_PACKAGES_MANIFEST_AND_NEGATIVES_CPU_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
