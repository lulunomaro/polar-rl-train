"""ShortSOURCE_ONLY compatibility proof; noPT/stat/hash/open/SDK/SSH/GPU.
Actualsourcecode/JSONmetadatareadable; syntheticinmemoryfixtureNOTcandidate.
"""
from pathlib import Path
from types import MappingProxyType
from collections import OrderedDict
import ast,copy,hashlib,io,json,time
from candidate_eval_metadata_producer import make_pair1_metadata,actual_pin_from_e1_final,normalize_actual_pin,MEMBERS
B=Path(__file__).resolve().parent;T=B.parents[2];E=T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR';P=T/'NINE_N80_PARALLEL_SOURCE_V8';H=lambda r:hashlib.sha256(r).hexdigest()
def info(p):
 r=p.read_bytes();return dict(path=str(p),bytes=len(r),SHA=H(r))
def put(name,v):
 p=B/name
 with p.open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2)
 return info(p)
old=json.loads((E/'ROLE_CONTRACTS.json').read_bytes());original=copy.deepcopy(old)
# Thesearearbitrarysyntheticmetadatafixtures,notPPOcomputedvaluesorReady.
pin=dict(path='MOCK_ONLY_METADATA_DO_NOT_OPEN',bytes=123456,SHA='a'*64,iteration=17,LR=.00003125,Adam17_steps=[41]*17,STD6=[7.,.08,.09,.1,.11,.12]);p0=dict(pin,path='MOCK_E0_METADATA_DO_NOT_OPEN',SHA='b'*64,iteration=23)
new=make_pair1_metadata(old,{'E0':p0,'CURB_PROTECTED878':pin},provenance={'kind':'STDLIB_MOCK_NOT_REAL_FINAL'});tests=[]
def check(n,v):assert v,n;tests.append(dict(name=n,passed=True))
check('baselineRoleContractsUnchanged',old==original)
check('onlyCandidateSourceCorePinChanged',new['ROLE_CONTRACTS']['CURB_PROTECTED878']['core']==dict(original_iteration=17,original_LR=.00003125,original_17Adam_step=41,original_STD6=pin['STD6']))
check('oldRNGHashMetadataOnlyHistorical',set(new['ROLE_CONTRACTS']['CURB_PROTECTED878']['core'])=={'original_iteration','original_LR','original_17Adam_step','original_STD6'}and new['ROLE_CONTRACTS']['CURB_PROTECTED878']['historical_baseline_source_contract']['core']==old['CURB_PROTECTED878']['core'])
check('otherE1rolesUnchanged',all(new['ROLE_CONTRACTS'][r]==old[r]for r in ('CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')))
check('sameOriginalFresh80Protocols',new['unchanged_protocol']['CURB_PROTECTED878']['controls']==750 and new['unchanged_protocol']['E0']['controls']==1000 and new['members']==MEMBERS)
try:normalize_actual_pin(dict(pin,Adam17_steps=[41]*16+[42]));nonuniform=False
except ValueError:nonuniform=True
check('nonuniformActualAdamNeverFlattenedOrGuessed',nonuniform)
try:normalize_actual_pin({k:v for k,v in pin.items()if k!='STD6'});missing=False
except AssertionError:missing=True
check('actualLearnedSTDRequiredNotOldSTD',missing)
final=dict(completed_actual_updates=3,new_fullstate_checkpoint=dict(checkpoint=pin['path'],bytes=pin['bytes'],SHA=pin['SHA'],atomic_final_published=True,completed_actual_updates=3,iteration=17,live_core=dict(iteration=17,optimizer_LRs=[pin['LR']],actual_alg_LR=9.,Adam17_steps=pin['Adam17_steps'],STD6=pin['STD6'])))
check('E1ActualFinalFormatterUsesSavedOptLRNotAlgLR',actual_pin_from_e1_final(final)==pin)
# ExerciseexactV5 cacheclasswithinmemorysyntheticfakeTensorNOTrealTorch.
class FT:
 def __init__(self,v,shape=()):self.v=v;self.shape=shape;self.dtype='MOCK_FLOAT32'
 def detach(self):return self
 def clone(self):return copy.deepcopy(self)
 def item(self):return self.v
 def tolist(self):return self.v
class FakeTorch:
 @staticmethod
 def is_tensor(x):return isinstance(x,FT)
 @staticmethod
 def equal(a,b):return a.v==b.v and a.shape==b.shape
 @staticmethod
 def load(*a,**kw):return copy.deepcopy(root)
actor=OrderedDict([('mlp.0.weight',FT(1,(256,35)))]+[('layer'+str(i),FT(i))for i in range(7)]+[('distribution.std_param',FT(pin['STD6'],(6,)))]);critic=OrderedDict([('mlp.0.weight',FT(1,(256,38)))]+[('layer'+str(i),FT(i))for i in range(7)]);root=dict(actor_state_dict=actor,critic_state_dict=critic,optimizer_state_dict=dict(state={i:dict(step=FT(41))for i in range(17)},param_groups=[dict(lr=pin['LR'])]),iter=17,unknown_full20k_history=dict(n=20000,fullTensor=FT('FULL20000_UNSLICED',(20000,4)),privateRNG=b'UNCHANGED_FULL_STREAM'))
tr=ast.parse((E/'e1_identity_cache.py').read_bytes());node=next(n for n in tr.body if isinstance(n,ast.ClassDef)and n.name=='WholeCheckpointIdentityCache');space=dict(Path=Path,MappingProxyType=MappingProxyType,hashlib=hashlib,io=io,PURPOSE='N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME');core_assign=next(n for n in tr.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CORE'for x in n.targets));exec(compile(ast.Module(body=[core_assign,node],type_ignores=[]),'ORIGINAL_V5_CACHE_CLASS_AST','exec'),space);cls=space['WholeCheckpointIdentityCache'];fixture=b'STDLIB_INMEMORY_MOCK_NOT_PT_OR_REAL_CANDIDATE';sha=H(fixture);expected=new['ROLE_CONTRACTS']['CURB_PROTECTED878']['core'];cache=cls('NEVEROPENED',FakeTorch(),expected_metadata=expected,expected_SHA=sha,expected_bytes=len(fixture),read_bytes=lambda _:fixture)
check('originalV5CacheAcceptsActualMetadataReformattedCandidate',cache.metadata['iteration']==17 and cache.metadata['STD6']==pin['STD6'] and cache.assert_entire_root_unchanged())
check('unknown20kHistoryPreservedWholeNoSlice',cache._root['unknown_full20k_history']['fullTensor'].shape==(20000,4) and cache.receipt()['saved20k_history_sliced']is False and cache.receipt()['saved20k_DR_physically_applied']is False)
try:cache.core('unknown_full20k_history');blocked=False
except ValueError:blocked=True
check('historyNotExposedToFreshEnv',blocked)
try:cls('NEVEROPENED',FakeTorch(),expected_metadata=old['CURB_PROTECTED878']['core'],expected_SHA=sha,expected_bytes=len(fixture),read_bytes=lambda _:fixture);stale=False
except AssertionError:stale=True
check('stale49fMetadataCannotBeReused',stale)
# Exactnewunusedparentbarriercopy: onlycardinalitycomparisonchanges.
raw=(P/'parallel_eval_safe.py').read_bytes();text=raw.decode('utf-8');needle="len(v['members'])==9";assert text.count(needle)==1;replacement="len(v['members'])==len(task['eval_members']) and set(v['members'])==set(task['eval_members'])";copytext=text.replace(needle,replacement);folder=B/'unused_parent_pair1_barrier';folder.mkdir(exist_ok=False);q=folder/'parallel_eval_safe.py'
with q.open('x',encoding='utf-8',newline='')as f:f.write(copytext)
ast.parse(copytext);check('parentUnusedBarrierOnly9toExactTaskMembersDelta',copytext.replace(replacement,needle)==text)
check('oldV8parentSourceUnchanged',(P/'parallel_eval_safe.py').read_bytes()==raw)
# OldE1taskvalidationacceptsnewcontract+Taskpinwithoutphysics/predicatechange.
sp=dict(Path=Path,json=json,os=__import__('os'),time=time);gt=ast.parse((E/'e1_group_scope.py').read_bytes());exec(compile(gt,'ORIGINAL_V5_GROUP_SCOPE','exec'),sp);task=dict(new['task_source_patches']['CURB_PROTECTED878'],role='CURB_PROTECTED878',num_envs=80,seed=20260928,fresh_fullDR_cohort=True,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],closure_m=.01,mimic_rad=.01,gas_N=400,stiffness_N_m=2000,asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',controls=750,physics_callbacks=6000,feedback_samples=1500,GPU_UUID='MOCK_GPU',group_id='MOCK_PAIR1',actual_group_admission=dict(group_id='MOCK_PAIR1',GPU_UUID='MOCK_GPU',source_SDK_admitted=True,private_GPU_EX_held=True,global_finite_EX_held=True,inherited_lock_fds=[90,91]),absolute_worker_deadline_epoch=time.time()+3600)
check('originalE1ValidatorAcceptsNewPinAndSameProtocol',sp['validate_group_task'](task,'CURB_PROTECTED878',B/'MOCK_GROUP',B/'MOCK_GROUP/CURB_PROTECTED878',new['ROLE_CONTRACTS'],environment={'CUDA_VISIBLE_DEVICES':'MOCK_GPU'},fd_check=lambda _:None))
proof=put('PAIR1_CANDIDATE_METADATA_SOURCE_MOCK_PROOF_V1.json',dict(kind='SOURCE_ONLY_STDLIB_INMEMORY_SYNTHETIC_NOT_REAL_CANDIDATE_OR_READY',tests=len(tests),passed=True,rows=tests,candidate_PT_reads_stats_hashes=0,Torch_SDK_GPU_SSH_orTrainingOperations=0,fixture_model_is_not_actual=True))
compat=put('PAIR1_CANDIDATE_EVAL_COMPATIBILITY_MAP_V1.json',dict(kind='SOURCE_METADATA_COMPATIBLE_NEW_UNUSED_PAIR1_NOT_READY',E1successSource=str(E),E0successSource=str(P),E1cache_code_change_required=False,E1hardbindings=[dict(path=str(E/'e1_group_scope.py'),lines=[15,16],fields=['task.source_SHA/bytes','task.source_iteration/Adam17/LR','contracts.source','contracts.core']),dict(path=str(E/'e1_identity_cache.py'),lines=[45,46,47],fields=['core.original_iteration','core.original_17Adam_step','core.original_LR','core.original_STD6'])],noeffect_dormant_constants='e1_identity_cache TYPED_SHA/TYPED_BYTES/STD6 areunusedbycache; do notpatchthemasifcurrenthardpins',E0hardbindings=dict(path=str(P/'parallel_eval_safe.py'),lines=[14,15],fields=['task.source_path/SHA/bytes/iteration/Adam17/LR'],STD='actualcachedactorSTDstrictloaded,notoldROLEmetadata'),source_formatter=info(B/'candidate_eval_metadata_producer.py'),parent_unused_barrier_copy=info(q),barrier_delta='OldE0wait_startL46hard9→exacttask.eval_members[E0,CURB_PROTECTED878]; oldE1barrieracceptspairalready. Noenvironment/skillcodechanges.',fd_scope='E0oldtask_argsL11requiresexact2evalleasefds(privateEX+globalfiniteEX), nottraining4fdTask',cohorts=new['unchanged_protocol'],parent_only='ActualfullsavebytesSHA/iter/17Adam/optLR/STDmetadata mustcomefromparentFINALcompleteproducer, notPPOcount. Parentfreshgroup_id/runtime/case/gpu/deadline/admission/leases, neithertheproducerormockcreatesReady/GO.',baseline=dict(CURB_PROTECTED878=dict(ascending=[22,27],descending=[27,27],stand_no_ordinary_failure=[26,26])),wholecache_scope='WholecandidateCPUcacheunknownRoot20khistory/RNG/queuespreserved; actoronlylivesinnew80env, noslicing/no20khistoryphysicalapply;critic/optimizercachednotlive',newRoleContractCore='Replaceonlyactive4metadatafields, preserveoldentirecoreasexplicitbaselinehistory; do notclaimoldRNGbytehashes/rootkeysarecurrent',actual_final_E1_path='new_fullstate_checkpoint.{checkpoint,bytes,SHA,live_core.iteration,live_core.optimizer_LRs[0],live_core.Adam17_steps,live_core.STD6}',skill_orphysicalpredicate_changed=False,oldsource_files_changed=False,proof=proof,source_refs=[info(E/'e1_identity_cache.py'),info(E/'e1_group_scope.py'),info(E/'e1_fresh_runtime_bridge.py'),info(E/'e1_parent_collector_metadata_contract.py'),info(E/'ROLE_CONTRACTS.json'),info(P/'parallel_eval_safe.py')],lookup_error=dict(path=str(P/'models.json'),result='notfound',classification='Unusedguess,noreadmodel; E0bindingactuallyinTask metadata',no_runtime_error=True)))
index=put('FINAL_PAIR1_CANDIDATE_EVAL_SOURCE_INDEX_V1.json',dict(compatibility=compat,proof=proof,files=[info(p)for p in sorted(B.rglob('*'))if p.is_file()],source_only=True,parent_archive_append_pending=True,no_actual_candidate_metadata_invented=True))
print(json.dumps(dict(index=index,compatibility=compat,proof=proof,tests=len(tests),candidate_PT_operations=0),indent=2))
