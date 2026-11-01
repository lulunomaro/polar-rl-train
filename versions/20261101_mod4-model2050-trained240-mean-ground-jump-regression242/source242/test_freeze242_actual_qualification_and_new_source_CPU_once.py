"""New saved-JSON qualification join and new caller checks; no model/SDK/raw."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,time
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent
def read(p):return json.loads(Path(p).read_bytes())
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (N/'INDEX242_NEW240_MEAN_REGRESSION_FROZEN.json').exists()
p=N/'source/contract242.py';s=importlib.util.spec_from_file_location('new242_contract_CPU',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
C=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/reports'
closing=read(C/'ROOT240V2_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');cpu=read(C/'ROOT240V2_NEW_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')
q=m.qualified240(closing,cpu)
assert q['SHA']=='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'and q['iteration']==2135 and q['Adam17']==42940
rejected=0
for change in('passed','oldread','save','shape','hidden','finite_role','transfer','counter'):
 c=copy.deepcopy(closing);u=copy.deepcopy(cpu)
 if change=='passed':u['passed']=False
 if change=='oldread':u['old_model_reads']=1
 if change=='save':u['roles']['jump_72']['save_at_or_after_requested_deadline']=False
 if change=='shape':u['roles']['jump_72']['actor35_critic38_STD6']=False
 if change=='hidden':u['roles']['jump_72']['hidden']=[512,256,128]
 if change=='finite_role':u['roles']['jump_72']['passed']=False
 if change=='transfer':c['formals']['jump_72']['transfers']=2
 if change=='counter':u['roles']['jump_72']['Adam17_step']+=1
 try:m.qualified240(c,u)
 except AssertionError:rejected+=1
 else:raise AssertionError(change)
t=dict(kind=m.KIND,num_envs=10,controls_per_case_max=500,controls_max=2000,actual_closed240_qualification=q,model_SHA=q['SHA'],model_bytes=q['bytes'],model_path=q['path'],model_iteration=q['iteration'],actual_17Adam_step=q['Adam17'],source_parent_SHA=m.PARENT_SHA,source240_formal_CPU_actual_passed=True,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',current_authority_binding={'kind':'FRESH_CNONE'},model_byte_reads=1,model_decodes=1,model_copies=0,no_optimizer_or_training_or_budget_write=True,training_reward_changed=False,cases=[dict(name=n,env=e)for n,e in[('standing',0),('forward',0),('reverse',0),('literal_jump',1)]])
assert m.validate_task(t)
for key,value in [('model_copies',1),('model_decodes',2),('model_iteration',2050),('training_reward_changed',True),('policy_hz',100)]:
 bad=copy.deepcopy(t);bad[key]=value
 try:m.validate_task(bad)
 except AssertionError:rejected+=1
 else:raise AssertionError(key)
files=sorted((N/'source').glob('*.py'))+[N/'run_ROOT242_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:ast.parse(p.read_text('utf8'),filename=str(p))
w=(N/'source/evaluate242_NEW240_mean_regression_UNUSED_once.py').read_text('utf8');parent=(N/'source/target242_single_N1_parent_UNUSED.py').read_text('utf8');caller=(N/'run_ROOT242_NEW240_mean_regression_once.py').read_text('utf8')
assert "'evaluate242_NEW240_mean_regression_UNUSED_once.py'"in parent and "task['sdk_python']"in parent
assert 'Linear(35,128)'in w and 'Linear(128,64)'in w and 'Linear(64,32)'in w and 'Linear(32,6)'in w and 'import mixed240_sdk as sdk'in w
assert 'Adam('not in w and '.backward('not in w and 'model_candidate225.pt'not in w
assert 'MOD4_MODEL2050_TRAINED240_MEAN_REGRESSION242_'in caller and "'wx'"in caller
report=R/'ROOT242_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json'
put(report,dict(passed=True,epoch=time.time(),groups=3,AST_files=len(files),new_JSON_rejects=rejected,actual_qualified240_model_metadata=q,old_fixture_replays=0,models_raw_NPZ_USD_SDK_GPU_Torch_remote_reads=0,physics_or_training=0,scope='New saved qualification join, shape/counter/source guards and caller interface. Not actual SDK/model/physical skill.'))
paths=files+[report]
index=N/'INDEX242_NEW240_MEAN_REGRESSION_FROZEN.json'
put(index,dict(epoch=time.time(),kind='FROZEN_NEW_QUALIFIED240_MEAN_REGRESSION_SOURCE_ONLY',actual_qualified_model_metadata=q,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in paths],actual_model_or_SDK_execution=False,physical_purpose='Four controlled first episodes at most10s/500controls each; original rewards/400N50D0-D7 and guards; no learning/account/GO.',count_admission=dict(new_formal_GPU_byte_decode=1,old_models=0,raw_download_or_read=0,extra_PhysX_getters=0,already_loaded_geometry_queries=2)))
print(json.dumps(dict(passed=True,index_SHA=H(index),AST_files=len(files),new_JSON_rejects=rejected,model_or_SDK_or_remote_reads=0)))
