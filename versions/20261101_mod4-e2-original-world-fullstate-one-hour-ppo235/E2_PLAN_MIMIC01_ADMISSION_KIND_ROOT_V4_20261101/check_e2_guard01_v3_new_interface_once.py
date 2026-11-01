"""New guard/source-purpose ABI CPU only;no SDK/Torch/model/old fixture."""
from pathlib import Path
from types import SimpleNamespace as NS
import ast,copy,hashlib,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
sys.path.insert(0,str(T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101'))
from e2_guard01_before_constructor_v3 import enforce_before_constructor
from e2_guard01_repair_contract_v3 import prior_failed_closed,new_read_admission
from e2_solo_protocol_guard01_v3 import validate_schedule,flat_go_fields
from e2_solo_contract import SHA,KIND,ITER,ADAM,LR
def ref(p):
 b=p.read_bytes();return json.loads(b),dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 assert ref(R/'CPU_GUARD01_V3_PURPOSE_FROZEN.json')[0]['executions']==1
 put(R/'CPU_GUARD01_V3_ONCE_CONSUMED.json',dict(epoch=time.time(),old_fixture_replays=0))
 sources={p.name:p.read_text(encoding='utf8') for p in N.glob('*.py')};assert len(sources)==14
 for s in sources.values():ast.parse(s)
 original=T/'OLD_EXPERTS_NORMALIZATION_NEXT_READY_SOURCE_V213_20261101/source/train_e2_213.py'
 old=original.read_text(encoding='utf8');new=sources['train_e2_213_guard01_v3.py']
 block="    from e2_guard01_before_constructor_v3 import enforce_before_constructor\n    enforce_before_constructor(cfg, os.environ['MOD4_E2_GUARD01_RECEIPT_PATH'])\n"
 assert new.replace(block,'')==old
 assert new.index('cfg.seed = args.seed')<new.index('    enforce_before_constructor(')<new.index('    env = Mod4Env(cfg=cfg)')
 install,_=ref(R/'INSTALL_E2_GUARD01_V3.json')
 m=next(x for x in install['files'] if x['relative']=='runtime/isaac/mod4/mod4_task.py')
 tasksource=Path(m['local_path']);b=tasksource.read_bytes();assert hashlib.sha256(b).hexdigest()==m['SHA']=='30ce41126a1a9b78a1c2b446281b28f4555c28052bfaa7c0e9a76079cf561fc5'
 tree=ast.parse(b);tc=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='TerminationsCfg')
 def threshold(name):
  a=next(x for x in tc.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id==name for y in x.targets))
  return ast.literal_eval(next(k.value for k in a.value.keywords if k.arg=='params'))['threshold']
 assert threshold('mimic')==.05 and threshold('closure')==.002
 f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='mimic_broken');assert ast.literal_eval(f.args.defaults[0])==.05
 def cfg(mimic=.05,closure=.002):
  return NS(terminations=NS(mimic=NS(params=dict(threshold=mimic),func=None,time_out=False),
   closure=NS(params=dict(threshold=closure),func=None,time_out=False),bad_orientation=NS(params=dict(limit_angle=.75),func=None,time_out=False)))
 c=cfg();row=enforce_before_constructor(c,R/'SYNTHETIC_ONLY_BEFORE_CONSTRUCTOR_GUARD01.json')
 assert c.terminations.mimic.params['threshold']==.01 and row['all_other_termination_params_unchanged'] and row['closure_m']==.002
 refusals=0
 for value in [cfg(mimic=.01),cfg(mimic=.06),cfg(closure=.003)]:
  try:enforce_before_constructor(value,R/'SYNTHETIC_REJECT_MUST_NOT_WRITE.json')
  except AssertionError:refusals+=1
  else:raise AssertionError('New guard refusal failed')
 closed,cref=ref(T/'E2_ORIGINAL_WORLD_PPO_ADMISSION_FAILURE_V235_20261101/reports/ROOT235_ZERO_PPO_COMPLETE_FAILURE_COLLECTION_ACTUAL.json')
 order,oref=ref(T/'E2_ORIGINAL_WORLD_PPO_ADMISSION_FAILURE_V235_20261101/reports/CURRENT_ACTUAL235V2_GUARD_REJECTION_CLOSED_AND_NEXT_V3_SOURCE_SCOPE.json')
 scope=prior_failed_closed(closed,order);purpose='ROOT_E2_MIMIC01_V3_SYNTHETIC_INTERFACE_ONLY';repair=new_read_admission(scope,purpose,'SYNTHETIC_NEW_V3_RUN')
 assert repair['prior_selected_source_read_and_decode_consumed'] and scope['source_cache']['source_physical_byte_opens']==scope['source_cache']['source_decodes']==1
 for bad_id,bad_run in [('OLD_PURPOSE','SYNTHETIC_NEW_V3_RUN'),(purpose,scope['run_id'])]:
  try:new_read_admission(scope,bad_id,bad_run)
  except AssertionError:refusals+=1
  else:raise AssertionError('New necessary purpose must reject legacy reuse')
 spec=dict(key='e2',execution_backend='target72',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',num_envs=20000,
  source_SHA=SHA,source_iteration=ITER,source_Adamstep=ADAM,source_LR=LR,source_kind=KIND,max_parent_seconds=3900,exit_headroom_seconds=300,
  no_physics_change=False,no_other_physics_change=True,explicit_mimic_guard_tightening=True,original_inherited_mimic_threshold_radians=.05,
  planned_mimic_threshold_radians=.01,closure_threshold_m=.002,guard_entry_SHA=install['guard_entry_SHA'],new_selected_source_read_purpose_id=purpose,
  manifest_SHA='a'*64,launch_evidence_SHA='b'*64,prelaunch_control_snapshot_id='SYNTHETIC_ONLY')
 schedule=dict(experts=dict(e2=spec),deferred_experts=[]);assert validate_schedule(schedule)
 g=flat_go_fields(spec);assert g['planned_mimic_threshold_radians']==.01 and g['guard_entry_SHA']==install['guard_entry_SHA']
 bad=copy.deepcopy(schedule);bad['experts']['e2']['no_physics_change']=True
 try:validate_schedule(bad)
 except AssertionError:refusals+=1
 else:raise AssertionError('Must not claim all physics unchanged')
 worker=sources['worker_e2_original_fullPPO.py'];finite=(T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SAVE_FINITE_V2_20261101/worker_e2_original_fullPPO.py').read_text(encoding='utf8')
 def finitefn(s):return ast.dump(next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='validate_finite_tree'))
 assert finitefn(worker)==finitefn(finite) and "validate_finite_tree(torch,state,'complete_save')" in worker and "validate_finite_tree(torch,losses,'PPO_losses')" in worker
 assert worker.index('validate_repair_task(task')<worker.index('cache=PinnedSource213')
 assert worker.index("put('E2_SOURCE_SELECTED_FINAL_READ_COUNTS.json'")<worker.index("ns['app'].close()")
 generator=sources['prepare_e2_solo_Task_manifest_Ready_GUARD01_V3.py']
 assert 'prior_failed_closed(closed,order)' in generator and "admission['checked_epoch']>=prior['closed_epoch']" in generator
 assert 'manifest.update(' in generator and 'ready.update(' in generator and "guard_entry_SHA=names['runtime/isaac/mod4/train_e2_213.py']['SHA']" in generator
 launch=sources['launch_e2_solo_install_FIRST_ROOT_ONLY_once.py'];normal=sources['collect_e2_solo_original_formal_cost_normal900_ROOT_ONLY_once.py'];cpu=sources['review_e2_solo_NEW_formal_initial_whole_CPU_ROOT_ONLY_once.py']
 assert "sys.version_info[:2] == (3,14)" in launch and "sys.version_info[:2] == (3,14)" in normal
 assert 'prepare_e2_solo_Task_manifest_Ready_GUARD01_V3.py' in launch and "'--new-source-read-purpose-id'" in launch and 'INSTALL_E2_GUARD01_V3.json' in launch
 assert "'wx'" in launch and launch.count('expected_control_cwd=CONTROL_CWD')==2
 assert 'planned_mimic_threshold_radians' in cpu and "os.environ['CUDA_VISIBLE_DEVICES']=''" in cpu and 'weights_only=False' in cpu
 controls,_=ref(R/'CONTROL_E2_GUARD01_V3_FROZEN_BINDINGS.json');oldcontrols,_=ref(T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101/reports/CONTROL_E2_SOLO_FROZEN_BINDINGS.json')
 before={x['relative']:x for x in oldcontrols['files']};after={x['relative']:x for x in controls['files']}
 assert all(before[k]['SHA']==after[k]['SHA'] for k in before if k!='e2_solo_protocol.py')
 put(R/'CPU_E2_GUARD01_V3_NEW_INTERFACE_ACTUAL.json',dict(epoch=time.time(),passed=True,source_AST=14,
  groups=['actual_original05_source_cfg_and_entry_before_constructor','new_guard_projection_one_positive_three_refusals','actual235_closed_read_consumed_and_NEWpurpose','typed_Task_manifest_Ready_GO_and_Py314_threecallers_finiteV2_retained'],
  new_refusals=refusals,actual235_failed_closed_ref=cref,actual235_work_order_ref=oref,prior_worker_source_read_and_decode=[1,1],prior_PPO_updates=0,
  actual_source_proof=dict(mod4_task_SHA=m['SHA'],mimic_default_line=f.lineno,DoneTerm_mimic_line=next(x.lineno for x in tc.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='mimic' for y in x.targets)),old_threshold=.05,new_threshold=.01,closure=.002),
  selected_new_entry_SHA=install['guard_entry_SHA'],original_control_HMAC_twofcntl_charge_unchanged=True,
  actual_V3_SDK_model_native24_FIRST='PENDING_ROOT_NEW_ADMISSION',model_assets_raw_Torch_SDK_network_Git=0,old_fixture_replays=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'CPU_GUARD01_V3_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
