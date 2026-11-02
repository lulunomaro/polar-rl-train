"""Buildunusedgenericpairsource andstdlibmetadata tests, neverexecuteowner/SDK."""
from pathlib import Path
from itertools import combinations
import ast,copy,hashlib,json
import generic_eval_metadata as m
B=Path(__file__).resolve().parent;D=B.parent;T=D.parent;P=D/'PAIR1_RETENTION_EVAL_SOURCE_V3';E=T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR';H=lambda r:hashlib.sha256(r).hexdigest()
def info(p):
 r=p.read_bytes();return dict(path=str(p),bytes=len(r),SHA=H(r))
def put(name,value):
 p=B/name
 with p.open('x',encoding='utf-8')as f:json.dump(value,f,ensure_ascii=False,indent=2)
 return info(p)
source=P/'single_gpu_group_supervisor.py';raw=source.read_bytes();old=raw.decode('utf-8');new=old;delta=[]
changes=[('nineisolatedSDKworkers','twoisolatedSDKworkers_selected_from_plan'),("roles=plan['roles'];assert len(roles)==2 and {r['role']for r in roles}=={'E0','CURB_PROTECTED878'};","roles=plan['roles'];members=validate_plan_members(plan);"),("kind='ONEGPU_PAIR1_CANDIDATE_FRESH80_RETENTION_NO_LEARNING'","kind='ONEGPU_SELECTED_PAIR_CANDIDATE_FRESH80_RETENTION_NO_LEARNING',eval_members=members,pair_size=2"),("task['eval_members']=['E0','CURB_PROTECTED878']","task['eval_members']=members[:]"),("assert len(children)==2;ready_until","assert len(children)==len(members)==2;ready_until"),("if len(ready)==2:","if len(ready)==len(members) and set(ready)==set(members):"),("kind='ACTUAL_PAIR1_CANDIDATE_FRESH80_RETENTION'","kind='ACTUAL_SELECTED_PAIR_CANDIDATE_FRESH80_RETENTION',eval_members=members,pair_size=2")]
for a,b in changes:
 assert new.count(a)==1,(a,new.count(a));new=new.replace(a,b);delta.append(dict(old=a,new=b))
helper="""ALLOWED_EVAL_ROLES=('E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')
def validate_plan_members(plan):
 members=plan['eval_members'];roles=plan['roles']
 assert isinstance(members,list) and len(members)==2 and len(set(members))==2
 assert set(members)<=set(ALLOWED_EVAL_ROLES), 'TwooftheeightnonH1rolesonly'
 assert len(roles)==2 and len({r['role']for r in roles})==2 and {r['role']for r in roles}==set(members)
 return list(members)

"""
assert new.count('def main():')==1;new=new.replace('def main():',helper+'def main():');target=B/'single_gpu_group_supervisor.py'
with target.open('x',encoding='utf-8',newline='')as f:f.write(new)
ast.parse(new);checks=[]
def check(name,value):assert value,name;checks.append(dict(name=name,passed=True))
def fails(fn):
 try:fn()
 except (AssertionError,KeyError,ValueError,TypeError):return True
 return False
# Resourcegate,locks,boundedwait/SDKlaunchandoriginalclosewaitsourceunchanged.
a='   class BusyResource(Exception):pass';b='   deadline=time.time()+2400';check('oldresourceEXgate_wait1800andcanonicalread_byteexact',old[old.index(a):old.index(b)]==new[new.index(a):new.index(b)])
a='  finally:\n   waits=[]';check('originalownscope_close_wait_and2EXrelease_byteexact',old[old.index(a):]==new[new.index(a):])
check('noOldPairSourceModified',source.read_bytes()==raw)
check('passfds_andspawn_originalunchanged',"pass_fds=tuple(f.fileno()for f in locks),start_new_session=True"in new)
tr=ast.parse(new);nodes=[n for n in tr.body if (isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ALLOWED_EVAL_ROLES'for t in n.targets))or(isinstance(n,ast.FunctionDef)and n.name=='validate_plan_members')];ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'PURE_MEMBER_VALIDATOR_AST','exec'),ns)
for pair in combinations(m.ROLES,2):
 p=dict(eval_members=list(pair),roles=[dict(role=r)for r in pair]);check('supervisor_exact_pair_'+','.join(pair),ns['validate_plan_members'](p)==list(pair))
for label,plan in [('H1',dict(eval_members=['E2','H1_normal'],roles=[dict(role='E2'),dict(role='H1_normal')])),('duplicate',dict(eval_members=['E2','E2'],roles=[dict(role='E2'),dict(role='E2')])),('three',dict(eval_members=['E0','E2','E3'],roles=[dict(role=r)for r in('E0','E2','E3')])),('wrongrows',dict(eval_members=['E2','CURB_INDEPENDENT113'],roles=[dict(role='E0'),dict(role='CURB_INDEPENDENT113')])),('noevalmembers',dict(roles=[dict(role='E2'),dict(role='CURB_INDEPENDENT113')]))]:check('negative_member_'+label,fails(lambda plan=plan:ns['validate_plan_members'](plan)))
# Syntheticmetadataonly, notcandidatePT orrealtrainingpass.
finals={}
for i,role in enumerate(m.ROLES):
 path='MOCK_METADATA_ONLY_NOT_A_CHECKPOINT_'+role;sha=hex(i+1)[2:]*64
 if role in m.E1_ROLES:finals[role]=dict(completed_actual_updates=2,new_fullstate_checkpoint=dict(checkpoint=path,bytes=123456,SHA=sha,iteration=31,completed_actual_updates=2,atomic_final_published=True,live_core=dict(iteration=31,optimizer_LRs=[.00003125],actual_alg_LR=5.,Adam17_steps=[400]*17,STD6=[8.,.08,.09,.1,.11,.12])))
 elif role=='W35':finals[role]=dict(final=dict(path=path,bytes=123456,SHA=sha,saved_iteration=41,actual_saved_LR=.0000625,Adam_min=500,Adam_max=500,full_core_STD_optimizer_and_targetDR_saved=True))
 else:finals[role]=dict(final=dict(path=path,bytes=123456,SHA=sha,saved_iteration=51,actual_saved_LR=.000125,saved_17Adam=[600],full_live_core_STD_optimizer_DR_history_RNG_queue_verified=True))
baseline=json.loads((E/'ROLE_CONTRACTS.json').read_bytes());truth=copy.deepcopy(baseline)
for pair in combinations(m.ROLES,2):
 result=m.build_eval_metadata(list(pair),finals,baseline,provenance={'kind':'STDLIB_MOCK_NOT_REAL_FINAL'});check('producer_exact_pair_'+','.join(pair),result['eval_members']==list(pair)and len(result['roles'])==2 and result['actualTask_Ready_GO_or_resources_created']is False)
result=m.build_eval_metadata(['E2','CURB_INDEPENDENT113'],finals,baseline);check('E2withoutSTDmetadataAcceptedNoOldSTDFill','STD6'not in result['source_pins']['E2'] and 'source_STD6'not in result['task_source_patches']['E2'] and result['source_pins']['E2']['STD_metadata_available']is False)
check('E2uniqueAdamNot17FakeCopies',result['source_pins']['E2']['Adam17_unique']==[600]and'Adam17_steps'not in result['source_pins']['E2'])
check('Curb113ActualSTDAndSavedOptLR',result['ROLE_CONTRACTS']['CURB_INDEPENDENT113']['core']==dict(original_iteration=31,original_17Adam_step=400,original_LR=.00003125,original_STD6=[8.,.08,.09,.1,.11,.12]))
check('Curb113OldCoreRNGOnlyHistorical',result['ROLE_CONTRACTS']['CURB_INDEPENDENT113']['historical_baseline_source_contract']['core']==baseline['CURB_INDEPENDENT113']['core']and len(result['ROLE_CONTRACTS']['CURB_INDEPENDENT113']['core'])==4)
check('parentBaselineContractsUnchanged',baseline==truth)
check('E2andCurb113exactOriginalWindowCounts',result['roles'][0]['controls']==1200 and result['roles'][1]['controls']==750 and all(r['seed']==20260928 and r['num_envs']==80 for r in result['roles']))
check('W35NoMetadataSTDNeeded',m.pin_from_training_final('W35',finals['W35'])['STD_metadata_available']is False)
bad=copy.deepcopy(finals['E2']);bad['final']['saved_17Adam']=[600,601];check('nonuniformFormalAdamMetadataNotFlattened',fails(lambda:m.pin_from_training_final('E2',bad)))
bad=copy.deepcopy(finals['CURB_INDEPENDENT113']);bad['new_fullstate_checkpoint']['live_core'].pop('STD6');check('E1ActualLearnedSTDMetadataRequired',fails(lambda:m.pin_from_training_final('CURB_INDEPENDENT113',bad)))
check('oldE1inactiveRowsNotChanged',result['ROLE_CONTRACTS']['CURB_PROTECTED878']==baseline['CURB_PROTECTED878']and result['ROLE_CONTRACTS']['SLOPE135']==baseline['SLOPE135'])
# VerifyrosterconstantsagainstactualpreviousV8metadataonly,notrawtrajectories.
summary=json.loads((T/'reports/SINGLE_GPU_NINE_FINAL_SUMMARY_V1.json').read_bytes());by={r['role']:r for r in summary['rows']}
check('all8ProtocolCountsFromActualV8',all(m.CONTROLS[r]==by[r]['controls']for r in m.ROLES))
for f in B.glob('*.py'):compile(ast.parse(f.read_bytes()),str(f),'exec')
proof=put('GENERIC_PAIR_SOURCE_STDLIB_METADATA_PROOF_V1.json',dict(kind='SOURCE_ONLY_STDLIB_MEMBER_AND_PRODUCER_METADATA_TESTS_NOT_SDK_OR_PPO',tests=len(checks),passed=True,rows=checks,fixtures='SYNTHETIC_INMEMORY_METADATA_NOT_ACTUAL_FINAL',PT_model_stat_read_hash_Torch_SDK_SSH_GPU_C_GO_Git=0))
roster=put('EIGHT_ROLE_FROZEN_EVAL_ROSTER_SOURCE_V1.json',dict(kind='SOURCE_ROSTER_NOT_READY_OR_PLAN_DISPATCH',allowed_eval_members=list(m.ROLES),pair_size=2,rows=[m.roster_row(r)for r in m.ROLES],source_control_reference=info(T/'reports/SINGLE_GPU_NINE_FINAL_SUMMARY_V1.json')))
parent_safe=P/'parallel_eval_safe.py'
files=put('MINIMAL_SOURCE_FILE_MAP_AND_INTERFACES_V1.json',dict(supervisor_source=info(target),original_supervisor_reference=info(source),supervisor_changes=delta,inserted_pure_validator=helper,parallel_eval_safe_UNCHANGED_REFERENCE=info(parent_safe),metadata_producer=info(B/'generic_eval_metadata.py'),interface='build_eval_metadata(roles,actualtrainingfinalbyrole,baseline_contracts,baseline_roster=None,provenance=None)',fields_returned=['eval_members','roles','source_pins','task_source_patches','ROLE_CONTRACTS'],E2_schema='FINAL.final[path,SHA,bytes,saved_iteration,saved_17Adam(unique),actual_saved_LR]; STDnotrequiredorfabricated',E1_schema='FINAL.new_fullstate_checkpoint[path=checkpoint,SHA,bytes,live_core.iteration/optimizer_LRs[0]/Adam17_steps/STD6]',W35_schema='FINAL.final[path,SHA,bytes,saved_iteration,Adam_min,Adam_max,actual_saved_LR];STDfromsameCPUcache',old_physics_skill_DR_G4_root_MCI_seed_reset_unchanged=True,resource_gates_and_leases='ExactoldprivateEX+globalfiniteEX/freshcomputeempty+canonicalnoactiveowner/res23500Mutil0/RAM96Gdisk25G/wait1800/commonready900/window2400/ownscopeclosewaitunchanged',roster=roster,old_Task_contract_reference=info(T/'NINE_N80_PARALLEL_SOURCE_V8/task_contract.py'),runtime_parent_worker_reference=info(T/'NINE_N80_PARALLEL_SOURCE_V8/worker_five_original_n80.py'),runtime_E1_source_reference=str(E),candidate_PT_pre_read_for_missing_STD=False,source_error_lookup=dict(path=str(P/'worker_sources/parent/task_contract.py'),result='localflatpayloadpathnotfound',resolved=str(T/'NINE_N80_PARALLEL_SOURCE_V8/task_contract.py'),model_or_runtime_access=False)))
index=put('FINAL_GENERIC_TWO_MEMBER_EVAL_SOURCE_INDEX_V1.json',dict(kind='UNUSED_GENERIC_TWO_MEMBER_EVAL_SOURCE_NOT_ACTUAL_TASK_READY_OR_GO',supervisor=info(target),producer=info(B/'generic_eval_metadata.py'),proof=proof,roster=roster,filemap=files,files=[info(p)for p in sorted(B.rglob('*'))if p.is_file()],old_sources_or_running_workers_touched=False,no_current_resources_queried_or_waited=True,parent_archive_append_pending=True))
print(json.dumps(dict(index=index,supervisor=info(target),producer=info(B/'generic_eval_metadata.py'),proof=proof,tests=len(checks),model_SDK_GPU_operations=0),indent=2))
