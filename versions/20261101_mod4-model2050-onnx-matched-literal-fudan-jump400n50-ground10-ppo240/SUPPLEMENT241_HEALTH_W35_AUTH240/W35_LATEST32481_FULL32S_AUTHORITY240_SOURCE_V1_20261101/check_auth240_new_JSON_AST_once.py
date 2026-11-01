"""New authority240 JSON/AST purpose only;no original32s/off/runtime fixtures."""
from pathlib import Path
import ast,copy,hashlib,json,time,traceback
import contract_latest32 as c
from make_latest32_Task_SOURCE_ONLY import make_task,FILES
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
B=T/'W35_LATEST32481_FULL32S_SAMEUID_EVAL_SOURCE_V1_20261101'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 assert json.loads((R/'CPU_AUTH240_PURPOSE_FROZEN.json').read_bytes())['executions']==1
 put(R/'CPU_AUTH240_ONCE_CONSUMED.json',dict(epoch=time.time(),old_fixtures=0))
 names=['contract_latest32.py','evaluate_latest32481_full32s_ROOT_ONLY_once.py','target_latest32_parent_ROOT_ONLY.py','guard_latest32.py','rm70_intervals227.py','positional_rows227.py','decode227_positional.py','make_latest32_Task_SOURCE_ONLY.py','run_ROOT_latest32481_full32s_once.py','derive_authority240_source.py','check_auth240_new_JSON_AST_once.py']
 sources={x:(N/x).read_text(encoding='utf8') for x in names}
 for s in sources.values():ast.parse(s)
 unchanged=['evaluate_latest32481_full32s_ROOT_ONLY_once.py','target_latest32_parent_ROOT_ONLY.py','guard_latest32.py','rm70_intervals227.py','positional_rows227.py','decode227_positional.py']
 assert all((N/x).read_bytes()==(B/x).read_bytes() for x in unchanged)
 def func(s,name):return ast.dump(next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name==name))
 old=(B/'contract_latest32.py').read_text(encoding='utf8')
 assert all(func(sources['contract_latest32.py'],k)==func(old,k) for k in ('metadata','qualified','validate_task'))
 a=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/reports'
 launch,lr=c.metadata(a/'ROOT240_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json');state,sr=c.metadata(a/'ROOT240_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json');binding,br=c.metadata(a/'KNOWN_ACTIVE240_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 assert launch['owner']==binding['owner']==c.EXPECTED_OWNER and state['current']['go']==binding['go']==c.EXPECTED_GO
 owner=binding['owner'];identity=dict(pid=owner['pid'],creation=owner['creation'],root=owner['cwd'])
 current=dict(go=copy.deepcopy(binding['go']));process=dict(copy.deepcopy(owner),running=True)
 active=dict(authority_generation=c.GENERATION,authorized_training_seconds=2268000,new_authority_budget_extensions=[],active_segment=dict(owner_parent_pid=owner['pid'],experts={c.KNOWN_ROLE:dict(started_epoch=binding['go'][c.KNOWN_ROLE]['learning_started_epoch'])}))
 out=c.validate_authority(json.loads(json.dumps(active)),json.loads(json.dumps(binding)),identity,current,process)
 assert out['mode']=='FRESH_EXACT240_ACTIVE' and out['active_GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 none=dict(active,active_segment=None)
 closed=dict(cohort_final=dict(go=copy.deepcopy(binding['go']),original_cost_settled=True,rows={c.KNOWN_ROLE:dict(terminal_all_own_children_waited=True)}),owner_exit=dict(original_cost_settled=True,own_original_two_fcntl_released_if_held=True))
 assert c.validate_authority(none,binding,identity,current,dict(running=False),closed)['mode']=='FRESH_CNONE_AFTER_MATCHING240_CLOSED'
 negatives=[]
 for key,val in [('kind','KNOWN_ACTIVE235_EXACT_ORIGINAL_E2_SOLO_AUTHORITY_BINDING'),('run_id','E2_B3AE_WORLD_MIMIC01_PPO235V4_20261101_0937')]:
  bad=copy.deepcopy(binding);bad[key]=val;negatives.append((active,bad,identity,current,process,None))
 for key,val in [('pid',1014881),('creation',1793496943.07),('exe','/wrong/exe'),('argv',['wrong']),('cwd',owner['root'])]:
  bad=copy.deepcopy(binding);bad['owner'][key]=val;negatives.append((active,bad,identity,current,process,None))
 bad=copy.deepcopy(binding);bad['go'][c.KNOWN_ROLE]['manifest_SHA']='0'*64;negatives.append((active,bad,identity,current,process,None))
 bad=copy.deepcopy(active);bad['active_segment']['owner_parent_pid']=1014881;negatives.append((bad,binding,identity,current,process,None))
 bad=copy.deepcopy(active);bad['active_segment']['experts'][c.KNOWN_ROLE]['started_epoch']+=1;negatives.append((bad,binding,identity,current,process,None))
 negatives.append((none,binding,identity,current,dict(running=False),None));negatives.append((none,binding,identity,current,process,closed))
 rejected=0
 for values in negatives:
  try:c.validate_authority(*values)
  except (AssertionError,KeyError):rejected+=1
  else:raise AssertionError('New authority240 negative not rejected')
 assert rejected==12
 rows=[]
 for name in FILES:
  b=(N/name).read_bytes();rows.append(dict(relative=name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
 task=make_task('SYNTHETIC_ONLY_AUTH240_NEW_CASE','ROOT_W35_LATEST32481_FULL32S_AUTH240_SYNTHETIC','GPU-c27eecbd-6838-7290-1cd2-37e34522213d',binding,[lr,sr,br],'/ROOT_ACTUAL_SDK_PYTHON_REQUIRED',rows)
 task=json.loads(json.dumps(task));assert c.validate_task(task) and task['current_authority_binding']['go']==c.EXPECTED_GO
 assert task['model_SHA']==c.SHA=='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b' and task['model_iteration']==32481
 caller=sources['run_ROOT_latest32481_full32s_once.py'];builder=sources['make_latest32_Task_SOURCE_ONLY.py']
 assert "INDEX='INDEX_W35_LATEST32481_AUTH240_FROZEN.json'" in caller and 'CPU_AUTH240_NEW_JSON_INTERFACE_ACTUAL.json' in caller
 assert 'binding[\'run_id\']==KNOWN_ACTIVE_RUN' in caller and 'binding[\'kind\']==KNOWN_BINDING_KIND' in builder
 assert 'ROOT_LATEST32_FRESH72_EXACT240_OR_CLOSED_CNONE_THEN_CLOSE72.json' in caller
 assert "worker_seconds=3600,parent_seconds=3780" in builder and 'timeout=3900' in caller
 assert 'source_CPU_SHA' in json.dumps(c.EXPECTED_GO) and c.EXPECTED_GO['jump_72']['source_CPU_SHA']=='50069ee3616fa3a5a7a20f7aa258d8c5f6bba6809150268080c43aa46729836c'
 put(R/'CPU_AUTH240_NEW_JSON_INTERFACE_ACTUAL.json',dict(epoch=time.time(),passed=True,source_AST=11,byte_unchanged_payload_files=unchanged,
  actual_saved_metadata_refs=[lr,sr,br],new_synthetic_active_and_closed_cases=2,new_refusals=rejected,new_Task_JSON_join=1,
  b_ident_root_as_cwd_not_taskroot=True,old_metadata_schema_kind_not_replaced=True,whole_READY_CPU_SHA_not_model_CPU_SHA=True,
  actual_target_metadata_or_SDK_GPU_model_raw_SSH_GO_Git=0,old_fixture_or_once_reexecutions=0,status='SOURCE_ONLY_ROOT_FRESH_ACTUAL_AUTHORITY_AND_CASE_PENDING'))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'CPU_AUTH240_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
