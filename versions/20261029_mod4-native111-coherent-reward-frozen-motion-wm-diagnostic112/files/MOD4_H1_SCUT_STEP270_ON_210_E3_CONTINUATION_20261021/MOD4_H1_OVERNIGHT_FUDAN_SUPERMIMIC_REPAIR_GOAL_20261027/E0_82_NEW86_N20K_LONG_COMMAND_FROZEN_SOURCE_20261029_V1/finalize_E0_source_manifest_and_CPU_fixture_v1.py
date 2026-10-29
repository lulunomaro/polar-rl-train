"""LOCAL final source/API checks, fresh CPU only. NO source PT/binary open/stat."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
OLD=L/'E0_210_N20K_MEAN_FROZEN_REGRESSION_SOURCE_V1'
E2=L/'E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4'
MODEL='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
WORKER='evaluate_E0_adapted82_new86_frozen1000_once_v1.py'
def H(raw):return hashlib.sha256(raw).hexdigest()
def write(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def mod(n,p):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);sys.modules[n]=m;spec.loader.exec_module(m);return m
def replace_file(n,changes):
 p=B/n;s=p.read_text(encoding='utf8')
 for a,b in changes:
  assert a in s,(n,a);s=s.replace(a,b)
 p.write_text(s,encoding='utf8',newline='\n')
def main():
 # Repair only derivation metadata placeholders; originals remain in saved template source references.
 replace_file(WORKER,[('source/E0_ADAPTED82_FINAL92.pt','source/E0_ADAPTED89D_FINAL82.pt'),('frozen_E0_original93_restore_config','frozen_E0_original82_restore_config'),
 (" assert H(__file__)==task['worker_SHA']"," assert H(__file__)==task['worker_SHA']\n assert H(job/'e0_long_command_domain_telemetry_v1.py')==task['telemetry_component_SHA']\n assert H(job/'GROUND_PROVIDER_SOURCE_CONTRACT.json')==task['ground_provider_contract_SHA']"),
 ("  assert not cmd.manual_evaluation_mode and cmd._dt==.02 and cmd.progress_goal==.5 and cmd.pure_max==4*__import__('math').pi", "  assert not cmd.manual_evaluation_mode and cmd._dt==.02 and cmd.progress_goal==.5 and cmd.pure_max==4*__import__('math').pi\n  assert real.cfg.episode_length_s==20 and tuple(cmd.cfg.resampling_time_range)==(12.,16.)\n  assert H(mod/'directional_spin_runtime.py')=='8fed717b0d2ba77491c252b183f9462f49457402d96927cc441c88ecd36b1cd8'")])
 replace_file('E0_new86_target_source_SDK_metadata_admission_v1.py',[("r['Adam_states17']","r['Adam_states']")])
 replace_file('remote_E0_new86_long_command_install_and_detach_v1.py',[("qualified E2 fixed93 final92","qualified E0 adapted89D final82")])
 # One source manifest: original binary rows retained verbatim, never opened here.
 oldpath=OLD/'E0_FROZEN_CASE_COMPLETE_INPUT_MANIFEST_V2.json';old=json.loads(oldpath.read_bytes())
 rows=[dict(r) for r in old['files'] if r['relative']!='evaluate_E0_adapted40050_originalN20K_mean_frozen_once_v1.py']
 runtime_py={r['relative']:Path(r['local_path']) for r in rows if r['relative'].endswith('.py')}
 witness=next(r for r in rows if r['relative']=='E0_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json');wv=json.loads(Path(witness['local_path']).read_bytes())
 assert H(Path(witness['local_path']).read_bytes())==witness['SHA']
 assert wv['passed'] and wv['model']['SHA']==MODEL and wv['review']['Adam_step']==641200 and wv['review']['Adam_states']==17
 original=next(r for r in rows if r['relative']=='original_run_manifest.json');originalv=json.loads(Path(original['local_path']).read_bytes());env=originalv['env']
 assert env['RM_HEIGHT_MIN']==env['RM_HEIGHT_MAX']==env['RM_NOMINAL_HEIGHT']=='0.25' or all(float(env[k])==.25 for k in ('RM_HEIGHT_MIN','RM_HEIGHT_MAX','RM_NOMINAL_HEIGHT'))
 assert float(env['RM_SPIN_WORLD_PROGRESS_M_S'])==.5 and float(env['RM_PURE_SPIN_FRACTION'])==.3 and float(env['RM_MOVING_SPIN_FRACTION'])==.2
 cmd=runtime_py['runtime/isaac/mod4/directional_spin_runtime.py'];cmdraw=cmd.read_bytes();tree=ast.parse(cmdraw)
 assert H(cmdraw)=='8fed717b0d2ba77491c252b183f9462f49457402d96927cc441c88ecd36b1cd8'
 rate=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='rate' for x in n.targets));assert ast.unparse(rate)=='torch.where(moving, 1 + u[:, 1], 1 + (self.pure_max - 1) * u[:, 1])'
 model=next(r for r in rows if r['relative']=='source/E0_ADAPTED89D_FINAL82.pt');assert model['SHA']==MODEL and model['bytes']==14031973
 launch=next(r for r in rows if r['relative']=='lib/zonglin2_app_launcher.py');assert launch['SHA']=='9178b2f8c67255d4f6d0a862fae0264bc326e11a8a91befbb9731f54e816773d'
 # All new executable components (including readonly CODE) form the installed dependency closure.
 exclude={'build_E0_long_window_source_v1.py','integrate_E0_lifetimes_and_selected_closure_v1.py',Path(__file__).name}
 own=[p for p in B.iterdir() if p.is_file() and (p.suffix=='.py' and p.name not in exclude or p.name=='GROUND_PROVIDER_SOURCE_CONTRACT.json')]
 for p in own:
  raw=p.read_bytes();rows.append(dict(relative=p.name,local_path=str(p),bytes=len(raw),SHA=H(raw),index_kind='new_source_bytes_only_no_old_binary_read'))
 assert len({r['relative'] for r in rows})==len(rows)
 manifest=dict(kind='MOD4_E0_ADAPTED82_NEW86_N20K_FROZEN_LONG_COMMAND_INPUT_V1',files=rows,RSL_sources=old['RSL_sources'],SDK_math_SHA=old['SDK_math_SHA'],qualified_formal_CPU_witness_SHA=witness['SHA'],typed_source_SHA=MODEL,new_model_CPU_not_performed_for_source_prep=True,optimizer_learning_steps=0,num_envs=20000,requested_controls=1000,warmup_controls=100,steady_controls=900,maximum_worker_seconds=1680,parent_exact_own_handle_wait_seconds=1800,original_episode_s=20,original_command_resampling_s=[12,16],source_model_num_envs=20000,no_checkpoint_population_projection=True,skill_graduation=False,complete_WM_dataset=False)
 write('E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json',manifest)
 allpaths={r['relative']:Path(r['local_path']) for r in rows}
 closure=mod('e0_declared_entry_receipt_cli_contract_v1',B/'e0_declared_entry_receipt_cli_contract_v1.py')
 cli=closure.validate_entry_cli_learn_hook(allpaths[closure.ENTRY].read_bytes(),(B/WORKER).read_bytes())
 receipts=closure.selected_receipt_graph((B/WORKER).read_bytes(),(B/closure.SUP).read_bytes(),(B/closure.CODE).read_bytes())
 deps=closure.declared_import_closure(manifest,lambda relative:allpaths[relative].read_bytes())
 guard=mod('e0_frozen_worker_call_guard_v1',B/'e0_frozen_worker_call_guard_v1.py');actualtree=ast.parse((B/WORKER).read_bytes());guardproof=guard.validate_frozen_worker_calls(actualtree)
 rejected=[]
 for source in ('runner.alg.update()','optimizer.step()','actor.train()','runner.learn(1)','loss.backward()','optimizer.zero_grad()','env.update(SECRET=1)'):
  try:guard.validate_frozen_worker_calls(ast.parse((B/WORKER).read_bytes()+b'\n'+source.encode()))
  except AssertionError:rejected.append(source)
  else:raise AssertionError('Forbidden actual source suffix accepted: '+source)
 # Fail real writer/sup/reader receipt mismatch, never a hand-constructed matching pair.
 bad=(B/WORKER).read_bytes().replace(b'ACTUAL_NATIVE24_E0_',b'ACTUAL_NATIVE34_E0_')
 try:closure.selected_receipt_graph(bad,(B/closure.SUP).read_bytes(),(B/closure.CODE).read_bytes())
 except AssertionError:rejected.append('real selected writer native34 vs readers native24')
 else:raise AssertionError('Receipt mismatch accepted')
 for p in B.glob('*.py'):
  ast.parse(p.read_bytes(),filename=str(p))
  if p.name.endswith('_CODE_v1.py'):
   container=ast.parse(p.read_bytes());code=next(ast.literal_eval(n.value) for n in container.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CODE' for x in n.targets));ast.parse(code)
 import torch
 assert not torch.cuda.is_initialized();sys.path.insert(0,str(B))
 fixture=mod('selected_telemetry_constructor_API_fixture_v1',B/'selected_telemetry_constructor_API_fixture_v1.py')
 proof=fixture.run_selected_constructor_fixture(B,'E0',torch,source_path=allpaths['runtime/isaac/mod4/mod4_task.py'],output=B/'reports/FRESH_CPU_SELECTED_CONSTRUCTOR_OUTPUT')
 # Real selected instance accumulator: initial-left censor, known lifetime, reset and end.
 catalog=mod('e0_original_profile_catalog_v1',B/'e0_original_profile_catalog_v1.py');life=mod('e0_observed_command_instances_v1',B/'e0_observed_command_instances_v1.py');n=10;t=torch
 k=t.arange(n);z=t.zeros(n);context=dict(key=k,episode=t.zeros(n,dtype=t.long),command_uid=t.zeros(n,dtype=t.long),command=t.zeros(n,3),direction=z,signed_yaw=t.where(k%2==0,-t.ones(n),t.ones(n)),written_phase_valid=t.ones(n,dtype=t.bool),written_phase=z)
 book=life.CommandInstances(t,n,'cpu');after=dict(errors=[t.ones(n),2*t.ones(n),3*t.ones(n)])
 rng=t.get_rng_state().clone();book.control=1;book.observe(context,after);book.close(t.arange(n),'resample')
 context['command_uid']+=1;book.open(t.arange(n),context,True)
 for i in range(600):
  context['written_phase']=t.full((n,),i*.02);book.control=i+2;book.observe(context,after)
 book.close(t.arange(5),'resample');book.close(t.arange(5,8),'reset');summary=book.finish(B/'reports/FRESH_CPU_INSTANCE_OUTPUT') if False else None
 out=B/'reports/FRESH_CPU_INSTANCE_OUTPUT';out.mkdir();summary=book.finish(out)
 assert sum(x['fully_observed_resample_to_resample_instance_events'] for x in summary['profiles'])==5
 assert sum(x['left_censored_instance_events'] for x in summary['profiles'])==10
 assert sum(x['reset_ended_instance_events'] for x in summary['profiles'])==3
 assert sum(x['window_end_right_censored_instance_events'] for x in summary['profiles'])==2
 assert t.equal(rng,t.get_rng_state())
 # Actual source transition algebra, only selected pure function AST; no SDK import.
 fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='transition_yaw');scope={'torch':t};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(cmd),'exec'),scope)
 ages=t.tensor([0.,1.,4.,5.,6.,7.,10.,11.,12.]);expected=t.tensor([0.,1.,1.,0.,0.,-1.,-1.,0.,0.]);assert t.equal(scope['transition_yaw'](ages,t.ones_like(ages)),expected)
 write('reports/LOCAL_SELECTED_SOURCE_AST_CONSTRUCTOR_INSTANCE_CPU_ACTUAL.json',dict(passed=True,scope='LOCAL SOURCE / fresh CPU synthetic ONLY, not target API/GPU',epoch=time.time(),versions=dict(torch=torch.__version__,tensordict=__import__('importlib.metadata',fromlist=['version']).version('tensordict')),actual_target_versions_pending=dict(torch='2.10.0+cu128',tensordict='0.14.1'),actual_entry_CLI_learn_hook=cli,real_writer_supervisor_readers_receipt_graph=receipts,declared_source_dependency_closure=deps,selected_worker_exact_AST_guard=guardproof,negative_cases=rejected,actual_selected_constructor_lifecycle=proof,instance_fixture=dict(initial_left_censored10=True,known_resample_complete5=True,reset_incomplete3=True,terminal_right_censored2=True,no_rng_draw=True),original_transition_pure_function_CPU=True,original20k_D1_D7_guards_unmodified=True,old_PT_raw_USD_NPZ_reads=0,remote_SDK_GPU_calls=0,full_runtime_admission_still_required=True))
 print(json.dumps(dict(passed=True,files=len(rows),entry=cli['declared_original_entry'],native=receipts['writer_native'],fresh_CPU_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=B/'reports'/('LOCAL_ORIGINAL_SOURCE_OR_CPU_FIXTURE_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(traceback=traceback.format_exc(),no_model_remote_SDK_GPU_reads=True),indent=2),encoding='utf8');raise
