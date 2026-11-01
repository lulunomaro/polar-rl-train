"""One NEW10mm Task/guard JSON interface purpose;no old fixture/runtime calls."""
from pathlib import Path
from types import SimpleNamespace as NS
import ast,copy,hashlib,json,time,traceback
import contract_latest32 as c
from make_latest32_Task_SOURCE_ONLY import make_task,FILES
from guard_latest32 import enforce_before_constructor
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
B=T/'W35_LATEST32481_FULL32S_AUTHORITY240_SOURCE_V2_20261101'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 assert json.loads((R/'CPU_CLOSURE10MM_PURPOSE_FROZEN.json').read_bytes())['executions']==1
 put(R/'CPU_CLOSURE10MM_ONCE_CONSUMED.json',dict(epoch=time.time(),old_fixtures=0))
 names=['contract_latest32.py','guard_latest32.py','evaluate_latest32481_full32s_ROOT_ONLY_once.py','target_latest32_parent_ROOT_ONLY.py','rm70_intervals227.py','positional_rows227.py','decode227_positional.py','make_latest32_Task_SOURCE_ONLY.py','run_ROOT_latest32481_full32s_once.py','derive_closure10mm_source.py','check_new_closure10mm_Task_interface_once.py']
 sources={x:(N/x).read_text(encoding='utf8') for x in names}
 for s in sources.values():ast.parse(s)
 for name in ('target_latest32_parent_ROOT_ONLY.py','rm70_intervals227.py','positional_rows227.py','decode227_positional.py'):assert (N/name).read_bytes()==(B/name).read_bytes()
 def func(s,name):return ast.dump(next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name==name))
 old=(B/'contract_latest32.py').read_text(encoding='utf8')
 assert all(func(sources['contract_latest32.py'],k)==func(old,k) for k in ('metadata','qualified','validate_authority'))
 rows=[]
 for name in FILES:
  b=(N/name).read_bytes();rows.append(dict(relative=name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
 binding=dict(kind=c.KNOWN_BINDING_KIND,run_id=c.KNOWN_ACTIVE_RUN,owner=copy.deepcopy(c.EXPECTED_OWNER),go=copy.deepcopy(c.EXPECTED_GO))
 task=make_task('SYNTHETIC_ONLY_10MM_TASK','ROOT_W35_LATEST32481_FULL32S_CLOSURE10MM_SYNTHETIC','GPU-c27eecbd-6838-7290-1cd2-37e34522213d',binding,[], '/ROOT_ACTUAL_SDK_PYTHON_REQUIRED',rows)
 task=json.loads(json.dumps(task));assert c.validate_task(task) and task['closure_m']==.01 and task['previous_closure_m']==.002 and task['user_authorized_closure10mm']
 admitted=dict(task,actual_current_authority_private_shared_resources_admitted=True,original_eval_parent_holds_private_and_validation_EX=True);assert c.validate_task(json.loads(json.dumps(admitted)),True)
 rejected=0
 for key,value in [('kind','W35_LATEST32481_32S_SAMEUID_RM70_MIMIC01_EVAL_ONLY_V1'),('closure_m',.002),('previous_closure_m',.005),('user_authorized_closure10mm',False),('planned_mimic_radians',.05),('no_new_learning_or_GO',False)]:
  bad=dict(admitted);bad[key]=value
  try:c.validate_task(bad,True)
  except AssertionError:rejected+=1
  else:raise AssertionError('New10mm Task refusal failed:'+key)
 def cfg(closure=.002,mimic=.05):
  return NS(terminations=NS(closure=NS(params=dict(threshold=closure),func=None,time_out=False),mimic=NS(params=dict(threshold=mimic),func=None,time_out=False),bad_orientation=NS(params=dict(limit_angle=.75),func=None,time_out=False)))
 value=cfg();receipt=enforce_before_constructor(value,R/'SYNTHETIC_ONLY_USER10MM_BEFORE_CONSTRUCTOR.json')
 assert value.terminations.closure.params['threshold']==.01 and value.terminations.mimic.params['threshold']==.01
 assert receipt['previous_closure_m']==.002 and receipt['closure_m']==.01 and receipt['all_other_termination_params_unchanged']
 assert receipt['before_termination_projection']['bad_orientation']==receipt['after_termination_projection']['bad_orientation']
 for value in (cfg(closure=.005),cfg(mimic=.02)):
  try:enforce_before_constructor(value,R/'SYNTHETIC_REJECT_MUST_NOT_WRITE.json')
  except AssertionError:rejected+=1
  else:raise AssertionError('Wrong legacy source should refuse before constructor')
 worker=sources['evaluate_latest32481_full32s_ROOT_ONLY_once.py']
 assert "real.physics_dt==.0025" in worker and "real.step_dt==.02" in worker and 'real.cfg.decimation==8' in worker
 assert "closure.params['threshold']==.01" in worker and "mimic.params['threshold']==.01" in worker
 assert worker.count('actual_closure_m=.01')==3 and 'actual_closure_m=.002' not in worker
 assert '400N50D0-D7/CAD70 peak-valley/user closure10mm' in worker
 assert 'range(1600)' in worker and 'deadline=time.time()+3600' in worker and 'stochastic_output=False' in worker
 assert 'runner.alg.update=forbidden;runner.alg.optimizer.step=forbidden' in worker
 caller=sources['run_ROOT_latest32481_full32s_once.py']
 assert "INDEX='INDEX_W35_LATEST32481_CLOSURE10MM_FROZEN.json'" in caller and 'CPU_CLOSURE10MM_NEW_TASK_INTERFACE_ACTUAL.json' in caller and 'timeout=3900' in caller
 assert "worker_seconds=3600,parent_seconds=3780" in sources['make_latest32_Task_SOURCE_ONLY.py']
 assert c.SHA=='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b' and c.ITER==32481 and c.ADAM==651260
 put(R/'CPU_CLOSURE10MM_NEW_TASK_INTERFACE_ACTUAL.json',dict(epoch=time.time(),passed=True,source_AST=11,new_pending_admitted_Task_JSON_join=True,
  new_user10mm_cfg_positive=1,new_refusals=rejected,source_guard_transition_m=[.002,.01],mimic_rad=.01,
  authority240_closed_CNone_and_qualification_functions_unchanged=True,observer_writer_decoder_target_parent_byte_unchanged=True,
  actual_target_case='PENDING_ROOT_FRESH_ADMISSION',old_fixture_replays=0,model_raw_asset_Torch_SDK_remote_Git_GO=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'CPU_CLOSURE10MM_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
