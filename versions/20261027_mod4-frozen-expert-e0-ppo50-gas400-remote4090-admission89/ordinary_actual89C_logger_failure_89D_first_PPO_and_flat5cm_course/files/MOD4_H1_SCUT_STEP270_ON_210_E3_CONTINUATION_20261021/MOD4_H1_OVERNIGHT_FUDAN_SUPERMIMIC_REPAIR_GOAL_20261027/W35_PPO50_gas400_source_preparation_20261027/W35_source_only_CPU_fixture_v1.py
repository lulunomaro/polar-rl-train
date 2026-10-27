"""One source/synthetic CPU fixture; never opens any model, bank, USD or ledger."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,sys,time,traceback,warnings
os.environ['CUDA_VISIBLE_DEVICES']=''
HERE=Path(__file__).resolve().parent
WORKER=HERE/'W35_PPO50_gas400_finite_worker_v1.py'
ADMISSION=HERE/'W35_target_source_SDK_CPU_admission_v1.py'
RUNTIME=HERE/'runtime_candidate_v1'
REPORT=HERE/'W35_SOURCE_ONLY_CPU_FIXTURE_ACTUAL_V1.json'

def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def reject(fn):
 try:fn()
 except (AssertionError,RuntimeError) as e:return dict(type=type(e).__name__,message=str(e))
 raise AssertionError('Negative fixture incorrectly accepted')

def main():
 assert not REPORT.exists();events=[]
 with warnings.catch_warnings(record=True) as caught:
  warnings.simplefilter('always')
  for p in RUNTIME.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
  worker_tree=ast.parse(WORKER.read_bytes());ast.parse(ADMISSION.read_bytes())
  syntax_warnings=[dict(category=w.category.__name__,message=str(w.message),filename=w.filename,line=w.lineno) for w in caught]
 worker=load('W35_worker_source_fixture',WORKER);admission=load('W35_admission_source_fixture',ADMISSION)
 now=time.time();task=dict(role='W35',source_SHA=worker.SOURCE_SHA,original_source_SHA=worker.ORIGINAL_SHA,
  original_run_manifest_SHA=worker.MANIFEST_SHA,num_envs=20000,source_qualification_kind=worker.KIND,
  canonical_authority_path=worker.AUTHORITY,authority_generation=worker.GENERATION,source_CPU_SHA='synthetic-fixture-only',
  GPU_UUID='synthetic-UUID-not-a-device',actual_USD_gas400_composition_passed=True,run_id='SOURCE_ONLY_FIXTURE',
  actual_resource_admission=dict(compute_UUID_only_rows=0,GPU_UUID='synthetic-UUID-not-a-device',GPU_name='NVIDIA GeForce RTX 4090'))
 go=dict(source_SHA=worker.SOURCE_SHA,source_qualification_kind=worker.KIND,max_parent_seconds=3900,exit_headroom_seconds=300,
  original_owner_pid=1,source_CPU_SHA=task['source_CPU_SHA'],learning_started_epoch=now,save_deadline=now+3600,
  nominal_end_epoch=now+3900,GPU_UUID=task['GPU_UUID'],authority_generation=worker.GENERATION,run_id=task['run_id'])
 worker.guard_task_go(task,go)
 negatives={}
 for name,field,value in [('E0_same_observation_width_source_rejected','source_SHA','54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371'),
  ('E0_original_source_rejected','original_source_SHA','b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'),
  ('E0_role_rejected','role','E0'),('different_population_rejected','num_envs',4096)]:
  bad=copy.deepcopy(task);bad[field]=value;negatives[name]=reject(lambda:worker.guard_task_go(bad,go))
 bad=copy.deepcopy(task);bad['actual_resource_admission']['compute_UUID_only_rows']=1
 negatives['occupied_selected_GPU_rejected']=reject(lambda:worker.guard_task_go(bad,go))
 badgo=dict(go,save_deadline=now+3599)
 negatives['changed_save_cap_rejected']=reject(lambda:worker.guard_task_go(task,badgo))
 # Exercise the exact first statement with the old failure behavior, without RSL.
 work=next(n for n in ast.walk(worker_tree) if isinstance(n,ast.FunctionDef) and n.name=='work')
 assignment=work.body[0];assert ast.unparse(assignment)=='runner.logger.writer = None'
 class FakeLogger:
  def save_model(self):return self.writer
 class FakeRunner:
  def __init__(self):self.logger=FakeLogger()
  def save(self):return self.logger.save_model()
 runner=FakeRunner()
 try:runner.save()
 except AttributeError as e:old_error=dict(type=type(e).__name__,message=str(e))
 else:raise AssertionError('old logger failure not reproduced')
 scope=dict(runner=runner);exec(compile(ast.Module(body=[assignment],type_ignores=[]),'<exact first work statement>','exec'),scope)
 assert runner.save() is None;writer=object();runner.logger.writer=writer;assert runner.save() is writer
 cli=next(n.value for n in ast.walk(worker_tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='sys' and t.attr=='argv' for t in n.targets))
 lr_index=next(i for i,n in enumerate(cli.elts) if isinstance(n,ast.Constant) and n.value=='--learning_rate')
 assert cli.elts[lr_index+1].value=='.00001'
 text=WORKER.read_text('utf8');entry=(RUNTIME/'isaac/mod4/train_e1_retention_named_owned_resume_ppo.py').read_text('utf8')
 for value in ['train_e1_retention_named_owned_resume_ppo.py','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json',
  "real.command_manager.get_term('twist')._dt==.02", "runner.alg.learning_rate==full['optimizer_state_dict']['param_groups'][0]['lr']==.00001"]:assert value in text
 assert 'learning_rate=args.learning_rate' in entry and 'gamma=0.9801' in entry and 'lam=0.9025' in entry
 assert 'from retention_checkpoint import resume_e1_new_episode' in entry and 'env.write_retention_trace(log_dir)' in entry
 original=json.loads((HERE/'W35_original_run_manifest_frozen_v1.json').read_bytes())
 assert H(HERE/'W35_original_run_manifest_frozen_v1.json')==worker.MANIFEST_SHA and original['env']['RM_KEEP_STD']=='1'
 sys.path.insert(0,str(RUNTIME/'isaac/mod4'))
 import torch
 from action_delay_physics_queue import PhysicsActionQueue
 rng=torch.get_rng_state().clone();queue=PhysicsActionQueue(3,'cpu',20260928,control_us=20000)
 synthetic=queue.state_dict();synthetic['rng']={key:torch.arange(16,dtype=torch.uint8) for key in synthetic['rng']}
 # These 16 bytes are explicitly synthetic, not a real CUDA RNG restore proof.
 real_validator_error=reject(lambda:queue.validate_state(synthetic))
 proof=admission.validate_original_CUDA_queue_structure_CPU(queue,synthetic)
 for label,mutate in [('wrong_control_period',lambda s:s.update(control_us=10000)),
  ('wrong_CUDA_rng_byte_width',lambda s:s['rng'].update(legs=torch.arange(15,dtype=torch.uint8))),
  ('wrong_CUDA_rng_dtype',lambda s:s['rng'].update(legs=torch.arange(16,dtype=torch.int64)))]:
  bad=copy.deepcopy(synthetic);mutate(bad);negatives[label]=reject(lambda:admission.validate_original_CUDA_queue_structure_CPU(queue,bad))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 freeze=json.loads((RUNTIME/'reports/SOURCE_FREEZE.json').read_bytes())['sha256']
 assert all(H(RUNTIME/p)==sha for p,sha in freeze.items())
 value=dict(attempt_id='W35_SOURCE_ONLY_CPU_FIXTURE_20261027_V1',epoch=time.time(),passed=True,
  worker=dict(path=str(WORKER),bytes=WORKER.stat().st_size,SHA=H(WORKER)),admission=dict(path=str(ADMISSION),bytes=ADMISSION.stat().st_size,SHA=H(ADMISSION)),
  runtime_freeze_mapping_checked=len(freeze),runtime_all_Python_AST_passed=True,inherited_syntax_warnings=syntax_warnings,
  W35_typed_guard_positive=True,negative_rejections=negatives,logger_original_error_reproduced=old_error,
  logger_first_work_statement_before_any_save=True,later_initialized_writer_retained=True,
  constructor_LR_literal_and_preupdate_algorithm_optimizer_guard=.00001,original_manifest_RM_STD_and_W35_entry_retention_trace_preserved=True,
  synthetic_queue_structure_proof=proof,unadapted_CPU_generator_rejection=real_validator_error,
  synthetic_not_actual_CUDA_rng_proof=True,no_original_checkpoint_or_normalizer_or_NPZ_or_binary_read=True,
  no_SDK_scene_GPU_remote_spawn_or_ledger_read_or_write=True,actual_target_source_SDK_CPU_pending=True,
  actual_CUDA_fullrestore_native24_first_PPO_pending=True,WM_transition_collection_executed=False,
  original_reader_and_invocation_errors=[dict(tool_chunk='c5181b',error='Second explicit Get-Content omitted W35 source-preparation directory; path absent, corrected in 277779; no runtime/model operation.'),
   dict(tool_chunk='e7dbe6',error='WindowsApps python alias returned exit1 with no stdout during AST-only invocation; use existing workspace .venv interpreter; no script main/model operation.')],
  Git_status='ordinary_supplement_existing89trial_pending_root')
 with REPORT.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
 print(json.dumps(dict(report=str(REPORT),SHA=H(REPORT),passed=True,worker_SHA=H(WORKER),admission_SHA=H(ADMISSION))))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=HERE/('W35_SOURCE_ONLY_CPU_FIXTURE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
  p.write_text(json.dumps(dict(traceback=traceback.format_exc(),no_GPU_remote_or_model_read=True),indent=2),encoding='utf8');raise
