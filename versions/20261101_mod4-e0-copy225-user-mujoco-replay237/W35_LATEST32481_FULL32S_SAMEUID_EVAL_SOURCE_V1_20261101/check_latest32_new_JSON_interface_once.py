"""One NEW metadata/JSON/guard interface purpose;old observer/writer fixtures0."""
from pathlib import Path
from types import SimpleNamespace as NS
import ast,copy,hashlib,json,time,traceback
from contract_latest32 import *
from make_latest32_Task_SOURCE_ONLY import make_task,FILES
from guard_latest32 import install_before_main
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 assert metadata(R/'CPU_LATEST32_PURPOSE_FROZEN.json')[0]['executions']==1
 put(R/'CPU_LATEST32_ONCE_CONSUMED.json',dict(epoch=time.time(),old_fixture_replays=0))
 sources={p.name:p.read_text(encoding='utf8') for p in N.glob('*.py')};assert len(sources)==10
 for s in sources.values():ast.parse(s)
 d=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/D_BEFORE_USE_CWD_REPAIR_SOURCE/reports'
 closed,cr=metadata(d/'ROOT227D_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');cpu,qr=metadata(d/'ROOT227D_NEW_W35_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')
 qual=qualified(closed,cpu,qr['SHA']);assert qual['source_SHA']==SHA
 binding,br=metadata(T/'E2_ORIGINAL_WORLD_PPO_ADMISSION_FAILURE_V235_20261101/reports/KNOWN_ACTIVE235_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 rows=[]
 for name in FILES:
  b=(N/name).read_bytes();rows.append(dict(relative=name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
 task=make_task('SYNTHETIC_ONLY_NEW_CASE','ROOT_W35_LATEST32481_FULL32S_SYNTHETIC_ONLY','GPU-c27eecbd-6838-7290-1cd2-37e34522213d',binding,[cr,qr,br],'/ACTUAL_ROOT_PARAMETER_SDK_PYTHON_REQUIRED',rows)
 pending=json.loads(json.dumps(task));assert validate_task(pending)
 admitted=json.loads(json.dumps(dict(pending,actual_current_authority_private_shared_resources_admitted=True,original_eval_parent_holds_private_and_validation_EX=True)))
 assert validate_task(admitted,True)
 refused=0
 for key,val in [('model_SHA','343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'),('model_iteration',32404),('Adam17',649720),('actual_saved_LR',.00017085937500000009),('worker_seconds',1680),('planned_mimic_radians',.05)]:
  wrong=dict(admitted);wrong[key]=val
  try:validate_task(wrong,True)
  except AssertionError:refused+=1
  else:raise AssertionError('New Task refusal failed:'+key)
 c=dict(authority_generation=GENERATION,authorized_training_seconds=2268000,new_authority_budget_extensions=[],active_segment=dict(owner_parent_pid=binding['owner']['pid']))
 proc=dict(binding['owner'],running=True);identity=binding['owner'];current=dict(go=binding['go'])
 active=validate_authority(c,binding,identity,current,proc);assert active['mode']=='FRESH_EXACT235_ACTIVE'
 c['active_segment']=None
 closedproof=dict(cohort_final=dict(go=binding['go'],original_cost_settled=True,rows=dict(e2=dict(terminal_all_own_children_waited=True))),owner_exit=dict(original_cost_settled=True,own_original_two_fcntl_released_if_held=True))
 assert validate_authority(c,binding,identity,current,dict(running=False),closedproof)['mode']=='FRESH_CNONE_AFTER_MATCHING235_CLOSED'
 wrong=copy.deepcopy(binding);wrong['owner']['creation']+=1
 try:validate_authority(c,wrong,identity,current,dict(running=False),closedproof)
 except AssertionError:refused+=1
 else:raise AssertionError('Wrong owner creation must refuse')
 path=T/'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101/source/train_full214.py';src=path.read_text(encoding='utf8');assert hashlib.sha256(path.read_bytes()).hexdigest()==task['original_entry_SHA']
 build=next(x for x in ast.parse(src).body if isinstance(x,ast.FunctionDef) and x.name=='build_env')
 assert next(x.lineno for x in ast.walk(build) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='configure_intro')<next(x.lineno for x in ast.walk(build) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='Mod4Env')
 def cfg():return NS(scene=NS(num_envs=0),seed=0,terminations=NS(mimic=NS(params=dict(threshold=.05),func=None,time_out=False),closure=NS(params=dict(threshold=.002),func=None,time_out=False)))
 def old(cfg):return dict(original_configure_completed=True)
 old.__module__='config214_training';old.__name__='configure208'
 seen=[]
 def ctor(cfg):
  assert cfg.terminations.mimic.params['threshold']==.01 and cfg.terminations.closure.params['threshold']==.002;seen.append('constructed_after01')
  return NS(sim=NS(set_camera_view=lambda *a:None))
 env=dict(Mod4EnvCfg=cfg,args=NS(num_envs=20000,seed=20260928),mod4_task=NS(attach_rmuc2026_terrain=lambda x:False),configure_intro=old,Mod4Env=ctor,ManagerBasedRLEnv=object)
 exec(compile(ast.Module(body=[build],type_ignores=[]),'<actual train_full214 build_env only>','exec'),env)
 undo=install_before_main(env,R/'SYNTHETIC_NEW_BEFORE_CONSTRUCTOR_RECEIPT.json');env['build_env']();undo();assert seen==['constructed_after01'] and env['configure_intro'] is old
 b=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/B_LOSSLESS_EVAL_SOURCE'
 assert all((N/x).read_bytes()==(b/x).read_bytes() for x in ('rm70_intervals227.py','positional_rows227.py','decode227_positional.py'))
 worker=sources['evaluate_latest32481_full32s_ROOT_ONLY_once.py'];parent=sources['target_latest32_parent_ROOT_ONLY.py'];caller=sources['run_ROOT_latest32481_full32s_once.py']
 assert worker.index('guard_uninstall=install_before_main')<worker.index("ns['main']()")
 assert worker.index("put('SOURCE227_FINAL_READ_COUNTS.json'")<worker.index("ns['app'].close()")
 assert 'actual_mimic_radians=.01' in worker and 'actual_closure_m=.002' in worker and 'stochastic_output=False' in worker
 assert 'range(1600)' in worker and 'deadline=time.time()+3600' in worker and 'child.wait(timeout=3780)' in parent
 assert 'runner.alg.update=forbidden;runner.alg.optimizer.step=forbidden' in worker
 assert 'rc=child.wait()' in parent and "time.time()>=deadline" in worker and 'postclose_marker=True' in parent
 assert caller.index('d.code(client,d.PY72,AUTH')<caller.index('client.close();client=None')<caller.index('client=d.connect72(secret);secret=None')
 assert 'sys.version_info[:2]==(3,14)' in caller and "'wx'" in caller and "timeout=3900" in caller
 signalcalls=[]
 for name,s in sources.items():
  for x in ast.walk(ast.parse(s)):
   if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('kill','terminate','send_signal'):signalcalls.append(name)
 assert not signalcalls
 put(R/'CPU_LATEST32_NEW_INTERFACE_ACTUAL.json',dict(epoch=time.time(),passed=True,source_AST=10,
  new_JSON_pending_to_admitted_to_worker_contract_roundtrip=True,new_refusals=refused,new_active_and_natural_closed_authority_cases=2,
  actual_227D_saved_qualification_refs=[cr,qr],known235_binding_ref=br,actual_entry_SHA=task['original_entry_SHA'],
  actual_entry_AST_inmemory_construct_after01=True,observer_writer_decoder_byte_identical=True,old_fixture_replays=0,
  actual_authority_target_SDK_model_native='PENDING_ROOT_FRESH_ACTUAL_CASE',Torch_model_asset_raw_network_Git=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'CPU_LATEST32_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
