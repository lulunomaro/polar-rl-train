"""PurestdlibAST/schema/saveordering proof. NOrealTorch/SDK/models imported.
SyntheticfixtureJSON hashes/stats areNOTPT/modeloperations orSDKacceptance.
"""
from pathlib import Path
from collections import OrderedDict
from types import SimpleNamespace
import ast,copy,hashlib,json
import e1_posttrain_contract as c
import e1_posttrain_state_tools as s
B=Path(__file__).resolve().parent;tests=[]
def check(label,fn):
 fn();tests.append(dict(name=label,passed=True))
def yes(value):assert value

def rejected(fn):
 try:fn()
 except (AssertionError,KeyError,TypeError,ValueError):return
 raise AssertionError('Expectedsourcecontractnegativecase')

for template in sorted((B/'UNUSED_TASK_TEMPLATES_V1').glob('*_SOURCE_ONLY_NOT_READY.json')):
 task=json.loads(template.read_bytes());role=task['canonical'];task.update(run_id='MOCK_ONLY_'+role,GPU_UUID='MOCK_GPU_UUID',canonical_path='ORIGINAL_CANONICAL_PATH_METADATA_ONLY_NEVER_OPENED',owner_parent_pid=777,inherited_lock_fds=[100,101],root_admission_SHA='MOCK_SOURCE_RECEIPT_SHA');admission={k:task[k] for k in ('run_id','role_key','GPU_UUID','source_SHA','asset_USD_SHA','asset_contract_SHA')};admission.update(kind=c.ADMISSION_KIND,actual_original_private_GPU_EX_held_by_original_parent=True,actual_original_shared_finite_env_SH_held=True,actual_current_canonical_owner_and_budget_admission_passed=True,canonical_binding=dict(path=task['canonical_path'],generation=c.GENERATION,owner_run_id=task['run_id'],owner_parent_pid=777,one_original_writer=True));go={k:task[k] for k in ('run_id','role_key','GPU_UUID','asset_USD_SHA','asset_contract_SHA','num_envs','policy_hz','feedback_hz','physics_dt','TGS','source_iteration','max_parent_seconds')};go.update(source_model_SHA=task['source_SHA'],one_original_writer=True,original_owner_pid=777,root_admission_SHA=task['root_admission_SHA'],input_Adam=c.source_Adam(task),save_deadline=200,nominal_end_epoch=500,exit_headroom_seconds=300)
 call=lambda t=task,a=admission,g=go:c.require_source_admission(t,a,g,now=100,environ={'CUDA_VISIBLE_DEVICES':'MOCK_GPU_UUID'},fd_check=lambda fd:fd)
 check(role+':parentactualschema_positive_fixture_NOT_AUTHORITY',call)
 for name,mutation in [('H1excluded',lambda t:t.update(canonical='H1_normal')),('N80nottraining',lambda t:t.update(num_envs=80)),('20updatecap',lambda t:t.update(additional_updates=21)),('noN80capacity',lambda t:t.update(training_capacity_scope='N80_SMALL_CAPACITY')),('source20kslicingforbidden',lambda t:t.update(state_slicing_or_projection=True)),('missingparentreceipt',lambda t:t.pop('root_admission_SHA')),('STDresetnotintroduced',lambda t:t.update(retype_checkpoint=True))]:
  t=copy.deepcopy(task);mutation(t);check(role+':negative_'+name,lambda t=t:rejected(lambda:call(t=t)))
 for k in ('actual_original_private_GPU_EX_held_by_original_parent','actual_original_shared_finite_env_SH_held','actual_current_canonical_owner_and_budget_admission_passed'):
  a=copy.deepcopy(admission);a[k]=False;check(role+':negative_'+k,lambda a=a:rejected(lambda:call(a=a)))
 g=copy.deepcopy(go);g['source_model_SHA']='WRONG';check(role+':negative_GOsource',lambda:rejected(lambda:call(g=g)))
 a=copy.deepcopy(admission);a['canonical_binding']['owner_parent_pid']=778;check(role+':negative_secondowner',lambda:rejected(lambda:call(a=a)))
 g=copy.deepcopy(go);g['save_deadline']=99;check(role+':negative_expiredBeforeModel',lambda:rejected(lambda:call(g=g)))

# OrderedDict and unknownnestedlistsemantics, currentknownvaluesmustwin.
old=OrderedDict(actor=OrderedDict(weight=1,unknown_nested={'x':[{'source_unknown':9}]}),optimizer={'param_groups':[{'lr':.01,'old_group_key':7}]},unknown_root={'opaque':float('nan')});cur=OrderedDict(actor=OrderedDict(weight=2),optimizer={'param_groups':[{'lr':.02}]});frozen=copy.deepcopy(old);merged=s.preserve_unknown(old,cur)
check('unknownRoot_nestedOrdered_currentweights_wins',lambda:yes(type(merged)==OrderedDict and type(merged['actor'])==OrderedDict and merged['actor']['weight']==2 and merged['optimizer']['param_groups'][0]['lr']==.02 and merged['optimizer']['param_groups'][0]['old_group_key']==7 and merged['actor']['unknown_nested']['x'][0]['source_unknown']==9))
check('unknownNaN_retained_andsourceunmodified',lambda:yes(merged['unknown_root']['opaque']!=merged['unknown_root']['opaque'] and old['actor']['weight']==1 and 'old_group_key' in old['optimizer']['param_groups'][0]))
check('allOriginalNestedKeysRetained',lambda:yes(not s.keys_preserved(old,merged)))

class FT:
 def __init__(self,v):self.v=v;self.dtype='MOCK_FLOAT32';self.shape=(len(v),) if isinstance(v,list) else ()
 def detach(self):return self
 def cpu(self):return self
 def item(self):return self.v
 def tolist(self):return self.v
class FakeTorch:
 @staticmethod
 def is_tensor(x):return isinstance(x,FT)
 @staticmethod
 def equal(a,b):return a.v==b.v
 @staticmethod
 def save(value,path):store[str(path)]=copy.deepcopy(value)
t=FakeTorch();store={};cache=SimpleNamespace(state=None,physical_byte_reads=1,source_SHA_calculations=1,source_decodes=1,SHA='MOCK_SELECTED_SOURCE_ID');selected=B/'MOCK_FIXTURES/SELECTED_SOURCE_METADATA_ONLY.fixture.json';cache.owns=lambda p:Path(p).resolve()==selected.resolve();cache.load=lambda path,**kw:copy.deepcopy(store[str(path)])
class SavedStop(Exception):pass
fixture=B/'MOCK_FIXTURES';fixture.mkdir(exist_ok=False)
for ix,role in enumerate(c.ROLES):
 actor=OrderedDict([('layer'+str(i),FT(i+1)) for i in range(8)]+[('distribution.std_param',FT([.1]*6))]);critic=OrderedDict(('layer'+str(i),FT(i+1)) for i in range(8));opt=dict(state={i:dict(step=FT(100),exp_avg=FT(.1),exp_avg_sq=FT(.2)) for i in range(17)},param_groups=[dict(lr=.01,params=list(range(17)))])
 source=dict(actor_state_dict=copy.deepcopy(actor),critic_state_dict=copy.deepcopy(critic),optimizer_state_dict=copy.deepcopy(opt),iter=5,independent_terrain_expert='E1_SLOPE' if 'SLOPE' in role else 'E1_CURB',spring_pressure_state=dict(n=20000),physical_action_delay_state=dict(n=20000,physics_us=2500,control_us=20000),spring_pressure_recipe=dict(nominal_stiffness_N_m=2000),feedback_delay_recipe=dict(control_period_us=10000),opaque_original_root=dict(history={'unknown':[1,2,3]}))
 source['actor_state_dict']['layer0'].v=-1;cache.state=copy.deepcopy(source)
 actor_owner=SimpleNamespace(state_dict=lambda:copy.deepcopy(actor));critic_owner=SimpleNamespace(state_dict=lambda:copy.deepcopy(critic));optimizer=SimpleNamespace(state_dict=lambda:copy.deepcopy(opt));runner=SimpleNamespace(alg=SimpleNamespace(actor=actor_owner,critic=critic_owner,optimizer=optimizer,learning_rate=.01),current_learning_iteration=6)
 current=copy.deepcopy(source);current.pop('opaque_original_root');current.update(actor_state_dict=actor,critic_state_dict=critic,optimizer_state_dict=opt,iter=6)
 def base_save(path,*a,**k):store[str(path)]=copy.deepcopy(current)
 runner.save=base_save;records=s.install_complete_unknown_merge(runner,None,cache,t,fixture)
 full=runner.save
 def fake_atomic(path,*a,**k):
  temp=str(path)+'.partial';full(temp,*a,**k);Path(path).write_text(json.dumps({'kind':'PURESTDLIB_SYNTHETIC_JSON_FIXTURE_NOT_A_MODEL'}),encoding='utf-8');store[str(Path(path).resolve())]=copy.deepcopy(store[str(Path(temp).resolve())])
  if ix==0:raise SavedStop('MOCKSTOP_AFTERPUBLICATION')
 runner.save=fake_atomic;outcomes=[]
 def put(name,row):outcomes.append((name,row))
 published=s.install_published_save_receipts(runner,None,cache,t,fixture,records,SavedStop,put,[20]);path=fixture/(role+'_NEW_OUTPUT.fixture.json')
 try:runner.save(str(path))
 except SavedStop:pass
 check(role+':fullsaveUnknownMergeNotOldWeights',lambda:yes(len(records)==1 and store[str(path.resolve())]['actor_state_dict']['layer0'].v==1 and store[str(path.resolve())]['opaque_original_root']['history']['unknown']==[1,2,3]))
 check(role+':originalAtomicThenPublishedReceiptIncludingSavedStop',lambda:yes(len(published)==len(outcomes)==1 and published[0]['atomic_final_published'] and published[0]['completed_actual_updates']==20 and published[0]['live_core']['iteration']==6))
 check(role+':saveCore17AdamActualNotArithmetic',lambda:yes(published[0]['live_core']['Adam17_steps']==[100]*17 and published[0]['live_core']['STD6']==[.1]*6))

# Originalpinnedcacheload/scopeAST, worstcaseCPUstepalias, norealTorch.
from contextlib import contextmanager
import os
inventory=json.loads((B/'FOUR_E1_POSTTRAIN_TRAINER_RESTORE_SAVE_INTERFACE_INVENTORY_V1.json').read_bytes());alias_sources=[]
for case in inventory['cases']:
 p=Path(case['local_runtime_source_root'])/'runtime/isaac/mod4/e1_pinned_source_v1.py';raw=p.read_bytes();tr=ast.parse(raw);nodes=[n for n in tr.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))];space=dict(Path=Path,copy=copy,os=os,contextmanager=contextmanager,ACTIVE=None);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),space)
 cls=space['PinnedSourceE1'];q=cls.__new__(cls);q.path=(fixture/(case['role']+'_SOURCE_METADATA.fixture.json')).resolve();q.state=dict(optimizer_state_dict=dict(state={i:dict(step=FT(100)) for i in range(17)}),opaque_original_history={'n':20000,'RNG':['FULL_ORIGINAL']});q.logical_purposes=[];q.own_or_other_artifact_loads=[];ft=SimpleNamespace(load=lambda *a,**kw:(_ for _ in ()).throw(AssertionError('NoactualsourceI/Oallowed')));q.torch=ft;q.original_load=ft.load
 with space['selected_source'](q):
  with space['runner_source_load_scope']():working=ft.load(str(q.path),map_location='cpu',weights_only=False)
  # WorstcaseloaderretainstheexactCPUstepfromworking, thenstepin-place.
  live_optim=working['optimizer_state_dict'];live_optim['state'][0]['step'].v+=1
 check(case['role']+':ORIGINALcacheWorkingClone_CPUstepAliasCannotMutateTruth',lambda q=q,w=working:yes(q.state['optimizer_state_dict']['state'][0]['step'].v==100 and w['optimizer_state_dict']['state'][0]['step'].v==101 and q.state['opaque_original_history']==w['opaque_original_history'] and q.state is not w))
 unsafe=copy.deepcopy(q.state);aliased=unsafe;aliased['optimizer_state_dict']['state'][0]['step'].v+=1
 check(case['role']+':negativeUnsafeTruthAliasMutationIsDetected',lambda unsafe=unsafe:yes(unsafe['optimizer_state_dict']['state'][0]['step'].v!=100))
 alias_sources.append(dict(role=case['role'],path=str(p),SHA=hashlib.sha256(raw).hexdigest(),clone_return_line=27,runner_scope_cached_load_line=58,sourcebyte_reads_hashes_decodes=0,actualTorch_alias_test=False))

# Staticcallgraph/order invariants; nostatementexecutesmain/SDK.
worker=(B/'worker_e1_posttrain_full20k_original_ppo_v1.py').read_text(encoding='utf-8');tree=ast.parse(worker)
readcall=next(n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='read_parent_receipts');torchimport=next(n.lineno for n in ast.walk(tree) if isinstance(n,ast.Import) and any(x.name=='torch' for x in n.names));cachecall=next(n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='PinnedSourceE1')
check('actualRootGOpreflightBeforeTorchSDKorModel',lambda:yes(readcall<torchimport<cachecall))
learn=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and ast.unparse(n.func)=='runner.learn'];check('originalFiniteRunnerLearnSignature',lambda:yes(len(learn)==1 and {k.arg:ast.unparse(k.value) for k in learn[0].keywords}==dict(num_learning_iterations="task['additional_updates']",init_at_random_ep_len='True')))
check('noFrozenMeanActorLoopOrSTDfreeze',lambda:yes('inference_mode' not in worker and '.eval()' not in worker and 'requires_grad_(False)' not in worker and 'stochastic_output=False' not in worker))
check('noTinyN80PhysicsCapacityOverride',lambda:yes('gpu_max_rigid_contact_count' not in worker and 'gpu_found_lost_pairs_capacity' not in worker))
check('parentOnlyOriginalCanonicalAccounting',lambda:yes('charge_values(' not in worker and 'bind_training_window' not in worker and 'fcntl' not in worker))
for p in sorted(B.glob('*.py')):
 tr=ast.parse(p.read_bytes(),filename=str(p));compile(tr,str(p),'exec');check('AST_compile_'+p.name,lambda:None)
result=dict(kind='PURESTDLIB_AST_SCHEMA_SAVE_ORDERING_MOCK_NOT_SDK_OR_PPO',tests=len(tests),passed=all(x['passed'] for x in tests),rows=tests,roles=4,H1_excluded=True,physical_model_byte_stat_hash_decode=0,Torch_SDK_imports=0,GPU_SSH_canonical_GO_PPO_Git_operations=0,numericgeometry_ororiginalRSL_execution=False,synthetic_fixture_files='MOCK_FIXTURES/*.fixture.json; simpleliteralmarker_NOTmodelweights',source_only_no_actual_admission=True,source_cache_CPUstep_alias_AST_proof=alias_sources,actual_Torchalias_execution=False)
p=B/'FOUR_E1_POSTTRAIN_AST_SCHEMA_STDLIB_MOCK_PROOF_V1.json'
with p.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(path=str(p),bytes=len(p.read_bytes()),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),tests=len(tests),passed=True,PT_SDK_operations=0),indent=2))
