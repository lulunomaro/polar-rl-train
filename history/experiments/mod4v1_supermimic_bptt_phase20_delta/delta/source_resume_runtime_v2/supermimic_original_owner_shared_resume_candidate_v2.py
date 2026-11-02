"""Finite original-canonical two-GPU SuperMimic BPTT owner, not a new ledger.
Original charge_values/authority locks/privateGPU EX/finiteSH/resource gates.
Worker algorithm changes are explicitly newhuman requested, not PPO20 relabel.
"""
from pathlib import Path
import os,sys,time,json,hashlib,fcntl,subprocess,traceback,shutil
import three_slot_common_v1 as b
from resume_runtime_contracts_v2 import evaluate_waited_worker,bind_future_task_extensions
from single_writer72_authority_V85M_source import authority_tracking_schema_admitted,authority_original_extension_count,authority_budget_GO_allowed
B=Path(__file__).resolve().parent;C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');UUIDS=('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d');ROLES={'E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'};RESERVE=86412.86069250107;put=b.put;KIND='MOD4V1_SUPERMIMIC_BPTT_TASK_V1'
def require(v,msg):
 if not v:raise RuntimeError(msg)
def gpu(uuid):
 from shared_gpu_admission_v1 import admit_shared_gpu
 return admit_shared_gpu(uuid,B)
def account(run,go,rows,end=False):
 c=b.read(C);a=c['active_segment'];require(a and a['owner_parent_pid']==os.getpid()and a['owner_run_id']==run,'Only current original owner may account');c,a=b.charge_values(c,a,go,rows,time.time());c['active_segment']=a
 if end:
  require(set(go)==set(rows)and all(b.terminal(r)for r in rows.values()),'Actual allstarted childwait before settle');a['ended_epoch']=time.time();a['actual_terminal_rows']=rows;c['completed_segments'].append(a);c['active_segment']=None
 put(C,c);return c
def environment(job,uuid):
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for n in('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(n,None)
 for n,r in{'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():p=job/'private_train'/r;p.mkdir(parents=True,exist_ok=True);env[n]=str(p)
 return env

def verify_sources(plan):
 require(b.C.resolve()==C.resolve()and plan['H1_excluded']and 1<=len(plan['entries'])<=8,'OriginalC only/eight nonH1');require(len({e['role']for e in plan['entries']})==len(plan['entries'])and{e['role']for e in plan['entries']}<=ROLES,'Unique exactroles')
 for e in plan['entries']:
  J=Path(e['job_root']);require(J.resolve().is_relative_to(B/'roles')and not(J/'GO_PRODUCTION.json').exists(),'New unused ownjob');require(e['target_bptt_steps']>=3000 and e['num_envs']in(512,1024,2048),'TrueBPTTtarget/newexplicitbatch');m=b.read(J/'INSTALL_MANIFEST.json');require(m['source_PT_copied']is False,'Noselectedmodelcopy')
  for f in m['files']:
   p=J/f['relative'];require(p.resolve().is_relative_to(J)and p.suffix.lower()not in('.pt','.pth','.ckpt'),'OnlynonPTsource/assets');require(p.stat().st_size==f['bytes']and b.H(p)==f['SHA'],'Pinnedownsoftware')
  require(e['teacher']['SHA']and e['teacher']['bytes']>10000000,'Pinnedwholeteacher metadata');require(m['asset_USD_SHA']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'and m['asset_contract_SHA']=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755','MOD4v1only')

def admit(e,u,c,run,locks,private,finite,resource):
 J=Path(e['job_root']);now=time.time();binding=dict(path=str(C),generation=c['authority_generation'],owner_run_id=run,owner_parent_pid=os.getpid(),one_original_writer=True);allfds=[f.fileno()for f in locks]+[private.fileno(),finite.fileno()];ad=dict(kind=KIND,epoch=now,role=e['role'],run_id=run,GPU_UUID=u,canonical_binding=binding,actual_original_authority_EX_private_GPU_EX_finite_SH=True,original_canonical_owner_admitted=True,actual_resource=resource,inherited_lock_fds=allfds,new_BPTT_algorithm_not_PPO20=True);put(J/'ROOT_ADMISSION_ACTUAL.json',ad);put(J/'ACTUAL_RESOURCE_LEASES.json',dict(**resource,inherited_lock_fds=allfds,owner_parent_pid=os.getpid(),authority_two_EX=True,private_GPU_EX=True,finite_SH=True));put(J/'ACTUAL_CANONICAL_READ.json',dict(epoch=now,path=str(C),SHA=b.H(C),remaining_seconds=c['remaining_training_seconds'],charged_seconds=c['charged_training_seconds'],strict_reserve_seconds=RESERVE,binding=binding))
 task=dict(kind=KIND,role=e['role'],family=e['family'],run_id=run,role_key=e['role_key'],GPU_UUID=u,owner_parent_pid=os.getpid(),inherited_lock_fds=allfds,root_admission_SHA=b.H(J/'ROOT_ADMISSION_ACTUAL.json'),manifest_SHA=b.H(J/'INSTALL_MANIFEST.json'),num_envs=e['num_envs'],target_bptt_steps=e['target_bptt_steps'],seed=e['seed'],teacher_path=e['teacher']['path'],teacher_SHA=e['teacher']['SHA'],teacher_bytes=e['teacher']['bytes'],asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',original_protocol=plan_protocol())
 go=dict(kind=KIND,role=e['role'],run_id=run,role_key=e['role_key'],GPU_UUID=u,learning_started_epoch=now,max_parent_seconds=3900,save_deadline=now+3600,nominal_end_epoch=now+3900,exit_headroom_seconds=300,max_actual_BPTT_policy_updates=e['target_bptt_steps'],canonical_binding=binding,teacher_SHA=e['teacher']['SHA']);put(J/'TASK.json',task);return task,go

def plan_protocol():return dict(physics_dt=.0025,policy_hz=50,feedback_hz=100,TGS=[32,4],gas_N=400,stiffness_N_m=2000,damping_Ns_m=3,closure_m=.01,mimic_rad=.01,full_D0_D7=True,reward_task_unchanged=True,BPTT='Learnedworldmodeltemporalactorgradient_not_PhysXautograd',new_explicit_fresh_training_cohort_not_N80_slice=True)
def main():
 plan=b.read(B/'OWNER_PLAN.json');verify_sources(plan);require(not(B/'OWNER_STARTED.json').exists(),'Unusedowneronce');run=plan['run_id'];put(B/'OWNER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),run_id=run,H1_excluded=True));locks=[];private={};finite=None;active=False;go={};rows={};slots={};errors=[];pending=list(plan['entries']);blocked=False;c=None
 def stop(slot,reason):put(Path(slot['entry']['job_root'])/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason=reason,complete_full_own_save_thenclose=True))
 try:
  until=time.monotonic()+1800
  while True:
   try:
    for path in b.LOCKS:f=path.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    c=b.read(C);require(c['active_segment']is None and authority_tracking_schema_admitted(c)and authority_original_extension_count(c)==9 and authority_budget_GO_allowed(c)and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return','Originalauthoritynotavailable');require(c['remaining_training_seconds']>RESERVE+7800,'Originalreserveandtwo3900windows')
    for u in UUIDS:f=(C.parent.parent/('three_expert_v2_'+u+'.lock')).open('rb+');private[u]=f;fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);gpu(u)
    finite=(C.parent.parent/'finite_environment_validation.lock').open('rb+');fcntl.flock(finite,fcntl.LOCK_SH|fcntl.LOCK_NB);break
   except BlockingIOError as busy:
    for f in[*private.values(),finite,*reversed(locks)]:
     if f is not None:fcntl.flock(f,fcntl.LOCK_UN);f.close()
    locks=[];private={};finite=None;put(B/'PREGO_RESOURCE_WAIT.json',dict(epoch=time.time(),reason=str(busy),partial_locks_held=0,PT_SDK_GO_Cwrites=False))
    if time.monotonic()>=until:raise TimeoutError('Original preGOresourcewait1800expired')
    time.sleep(30)
  while pending or slots:
   if active:c=account(run,go,rows)
   for u,slot in list(slots.items()):
    p=slot['p'];e=slot['entry'];key=e['role_key']
    if p.poll()is None:
     if time.time()>=go[key]['save_deadline']or c['remaining_training_seconds']<=RESERVE+300*len(slots):stop(slot,'Original save deadline/reserve')
     continue
    rc=p.wait();J=Path(e['job_root']);semantic=evaluate_waited_worker(J,rc,e,run);final=semantic['final'];rows[key]=dict(key=key,role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),final=final,original_error=semantic['original_error'],semantic_result=semantic);put(J/'PARENT_WAITED_ACTUAL.json',rows[key]);del slots[u];c=account(run,go,rows)
    if semantic['original_error']:
     errors.append(dict(role=e['role'],returncode=rc,reason='Realerrorpreservednoautomaticunchangedretry',semantic_reasons=semantic['reasons']));blocked=True
   for u in UUIDS:
    if u in slots or blocked or not pending:continue
    if c['remaining_training_seconds']<=RESERVE+3900*(len(slots)+1):break
    e=pending[0];resource=gpu(u);J=Path(e['job_root']);task,g=admit(e,u,c,run,locks,private[u],finite,resource);task=bind_future_task_extensions(task,e);put(J/'TASK.json',task)
    if not active:
     now=time.time();c=b.read(C);require(c['active_segment']is None,'Originaluniqueowner');c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),owner_run_id=run,kind='Linux_MOD4V1_SUPERMIMIC_BPTT_'+run,started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='Originalcharge_valuesexpertsecondsactualGOthroughload-model-WM-BPTT-fullsave-SDKclose-parentwait; noclamprefundextension');put(C,c);active=True
    key=e['role_key'];require(not(J/'GO_PRODUCTION.json').exists(),'UnusedworkerGO');go[key]=g;put(J/'GO_PRODUCTION.json',g);log=(J/'SUPERMIMIC_FULL_STDOUT_STDERR.log').open('xb')
    try:p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(J/'worker_sources/worker_supermimic_bptt_resume_candidate_v2.py'),'--job-root',str(J)],cwd=J,env=environment(J,u),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=tuple(task['inherited_lock_fds']),start_new_session=True)
    except BaseException:log.close();rows[key]=dict(key=key,role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=1,owner_received_terminal_epoch=time.time(),original_error=True);raise
    log.close();slots[u]=dict(p=p,entry=e);pending.pop(0);put(J/'WORKER_IDENTITY_ACTUAL.json',b.ident(p.pid));c=account(run,go,rows)
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),run_id=run,workers={u:dict(role=s['entry']['role'],identity=b.ident(s['p'].pid))for u,s in slots.items()},terminal_roles=[r['role']for r in rows.values()],pending_roles=[e['role']for e in pending],blocked_after_real_error=blocked,canonical_remaining_seconds=c['remaining_training_seconds'],target_per_expert=3000,final_skill_goal=.9,not_yet_skill_pass_claim=True))
   if not slots and(blocked or not pending or c['remaining_training_seconds']<=RESERVE+3900):break
   if slots:time.sleep(3)
  if active:account(run,go,rows,True);active=False
  put(B/'COHORT_FINAL.json',dict(run_id=run,rows=rows,go=go,pending_unstarted_roles=[e['role']for e in pending],all_own_children_waited=not slots,original_cost_settled=not active,errors=errors,H1_excluded=True,original_skill_evaluation='PENDING_FROZEN_ACCEPTANCE_NOT_LOSS',newledger_or_extension=False))
 except BaseException:
  errors.append(dict(parent_error=traceback.format_exc()));put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),errors=errors,active_not_falsely_cleared=active))
  for slot in slots.values():stop(slot,'Ownoriginalownerexception')
  while slots:
   for u,s in list(slots.items()):
    if s['p'].poll()is not None:e=s['entry'];rc=s['p'].wait();semantic=evaluate_waited_worker(Path(e['job_root']),rc,e,run);rows[e['role_key']]=dict(key=e['role_key'],role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),original_error=True,final=semantic['final'],semantic_result=semantic);del slots[u]
   if active:account(run,go,rows)
   if slots:time.sleep(3)
  if active:account(run,go,rows,True);active=False
 finally:
  if not slots:
   for f in[finite,*private.values(),*reversed(locks)]:
    if f is not None:fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),run_id=run,all_own_children_waited=not slots,original_cost_settled=not active,original_leases_released=not slots,errors=errors,H1_excluded=True,no_newbudget_refund_or_extension=True))
if __name__=='__main__':main()
