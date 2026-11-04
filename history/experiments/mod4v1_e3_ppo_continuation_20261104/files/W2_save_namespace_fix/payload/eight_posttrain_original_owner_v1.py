"""Original single canonical writer, two original GPU slots, eight finite PPO jobs.
H1 excluded. Uses exact original b.charge_values and original owner locks.
SOURCE until an exact staged OWNER_PLAN+worker contracts+originalproofs exist.
Never reads a selected PT or SDK. No new ledger/refund/extension/foreign action.
"""
from pathlib import Path
import os,sys,time,json,hashlib,fcntl,subprocess,traceback,shutil,signal
import three_slot_common_v1 as b
from single_writer72_authority_V85M_source import authority_tracking_schema_admitted,authority_original_extension_count,authority_budget_GO_allowed
B=Path(__file__).resolve().parent
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
UUIDS=('GPU-16828f91-2b45-b646-8dc0-9481138e2842',)
ROLES={'E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'}
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3';CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
RESERVE=86412.86069250107
put=b.put

def require(v,msg):
 if not v:raise RuntimeError(msg)

def gpu(uuid):
 import psutil
 raw=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip()for x in raw.split(',')]
 apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
 require(a[0]==uuid and a[1]=='NVIDIA GeForce RTX 4090','Exact authorized4090')
 if not(int(a[2])>15669 and int(a[3])<=30 and uuid not in apps and psutil.virtual_memory().available>64*1024**3 and shutil.disk_usage(B).free>50*1024**3):raise BlockingIOError('Original GPU/host light admission not ready')
 return dict(epoch=time.time(),GPU_UUID=uuid,GPU_line=raw,compute_empty=True,RAM_available=psutil.virtual_memory().available,disk_free=shutil.disk_usage(B).free)

def account(run,go,rows,end=False):
 c=b.read(C);a=c['active_segment'];require(a and a['owner_parent_pid']==os.getpid()and a['owner_run_id']==run,'Only current original owner may account');c,a=b.charge_values(c,a,go,rows,time.time());c['active_segment']=a
 if end:
  require(set(go)==set(rows)and all(b.terminal(r)for r in rows.values()),'All started own children terminal before settle')
  a['ended_epoch']=time.time();a['actual_terminal_rows']=rows;c['completed_segments'].append(a);c['active_segment']=None
 put(C,c);return c

def environment(job,uuid):
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for name in('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(name,None)
 for name,rel in{'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
  p=job/'private_train'/rel;p.mkdir(parents=True,exist_ok=True);env[name]=str(p)
 return env

def verify_sources(plan):
 require(b.C.resolve()==C.resolve()and plan['H1_excluded']is True,'Original canonical only; noH1')
 require(1<=len(plan['entries'])<=8 and {x['role']for x in plan['entries']}<=ROLES and len({x['role']for x in plan['entries']})==len(plan['entries']),'Only unconsumed subset of eight roles; noH1')
 require(len({x['role_key']for x in plan['entries']})==len(plan['entries']),'Unique original charge keys')
 for e in plan['entries']:
  job=Path(e['job_root']).resolve();require(job.is_relative_to(B),'Only newgroup owned job roots');require(not(job/'GO_PRODUCTION.json').exists(),'New unused role GO')
  require(e['max_additional_updates']==20 and e['num_envs']==20000 and e['max_parent_seconds']==3900 and e['save_after_seconds']==3600 and e['exit_headroom_seconds']==300,'Finite20 original bounds')
  m=b.read(job/e['manifest_file']);require(m['source_PT_copied']is False,'Original frozen sources not copied')
  for f in m['files']:
   p=job/f['relative'];require(p.resolve().is_relative_to(job)and p.suffix.lower()not in('.pt','.pth','.ckpt'),'Source/assets/install only no model stat/hash')
   require(p.stat().st_size==f['bytes']and b.H(p)==f['SHA'],'Exact staged own source/asset')
  proof=b.read(job/e['actual_prior_full20k_proof_file']);require(proof['actual_not_mock']and proof['source_SHA']==e['source_SHA']and proof['asset_USD_SHA']==USD and proof['asset_contract_SHA']==CONTRACT and proof['num_envs']==20000 and proof['producer_input_whole20k_restore_passed']and proof['candidate_full_live20k_save_verified']and proof['producer_actual_PPO_updates']==20 and proof['producer_saved_17Adam']==[866460]and proof['all_own_children_waited'],'Actual complete20k GPU producer-save history; fresh candidate fullrestore still mandatory in worker')
  require(e['source_contract_AST_MOCK_passed']and e['source_contract_not_SDK_pass_claim'],'Source-only contract distinguished')

def task_and_go(e,uuid,c,run,global_fds,private,finite,resource):
 job=Path(e['job_root']);key=e['role_key'];now=time.time();canonical=dict(path=str(C),generation=c['authority_generation'],owner_run_id=run,owner_parent_pid=os.getpid(),one_original_writer=True)
 receipt=dict(kind='ACTUAL_EIGHT_POSTTRAIN_ORIGINAL_CANONICAL_READ',epoch=now,path=str(C),SHA=b.H(C),remaining_seconds=c['remaining_training_seconds'],charged_seconds=c['charged_training_seconds'],owner_pid=os.getpid(),run_id=run,strict_reserve_seconds=RESERVE,original_two_EX_held=True)
 put(job/'ACTUAL_CANONICAL_READ.json',receipt);put(job/'ACTUAL_RESOURCE_LEASES.json',dict(**resource,owner_parent_pid=os.getpid(),original_private_GPU_EX_held=True,original_finite_env_SH_held=True,original_owner_EX_fds=global_fds,private_GPU_EX_fd=private.fileno(),finite_env_SH_fd=finite.fileno()))
 admission=dict(kind='ROOT_MOD4V1_EIGHT_POSTTRAIN_ACTUAL_ADMISSION_V1',run_id=run,role_key=key,role=e['role'],GPU_UUID=uuid,source_SHA=e['source_SHA'],asset_USD_SHA=USD,asset_contract_SHA=CONTRACT,actual_original_private_GPU_EX_held_by_original_parent=True,actual_private_GPU_EX_held_by_original_parent=True,actual_original_shared_finite_env_SH_held=True,actual_fresh_GPU_and_host_resources_admitted=True,actual_current_canonical_owner_and_budget_admission_passed=True,actual_target_source_and_SDK_admitted=True,prior_full20k_proof_reused_not_currenttraining_alreadyrestored=True,canonical_binding=canonical,actual_canonical_read_receipt_SHA=b.H(job/'ACTUAL_CANONICAL_READ.json'),actual_lock_and_resource_receipt_SHA=b.H(job/'ACTUAL_RESOURCE_LEASES.json'),actual_prior_full20k_proof_SHA=b.H(job/e['actual_prior_full20k_proof_file']),original_owner_EX_fds=global_fds,private_GPU_EX_fd=private.fileno(),finite_env_SH_fd=finite.fileno())
 native=b.read(job/e['native0pt_evidence_file']);require(native['passed'],'Actual original asset native0PT proof')
 admission.update(new_asset_native0PT_passed=True,new_asset_native0PT_receipt_SHA=b.H(job/e['native0pt_evidence_file']),target_source_SDK_receipt_SHA=b.H(job/e['target_source_SDK_receipt_file']),prior_full20k_restore_proof_reused_as_history_only=True,historical_RM70_geometry_and_shared_material_proofs_exactly_reused=True,historical_RM70_scope_reuse_receipt_SHA=b.H(job/e['historical_geometry_evidence_file']))
 put(job/'ROOT_ADMISSION_ACTUAL.json',admission);ash=b.H(job/'ROOT_ADMISSION_ACTUAL.json');mh=b.H(job/e['manifest_file']);task=dict(e['task_template']);task.update(run_id=run,role=e['role'],role_key=key,GPU_UUID=uuid,canonical_path=str(C),original_canonical_generation=c['authority_generation'],canonical_binding=canonical,root_admission_file=str(job/'ROOT_ADMISSION_ACTUAL.json'),root_admission_SHA=ash,manifest_file=e['manifest_file'],manifest_SHA=mh,max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,max_additional_updates=20,original_owner_EX_fds=global_fds,private_GPU_EX_fd=private.fileno(),finite_env_SH_fd=finite.fileno(),actual_parent_pid=os.getpid(),stop_file=str(job/'STOP_AFTER_SAVE.json'),save_deadline=now+3600)
 go=dict(e['go_template']);go.update(run_id=run,role=e['role'],role_key=key,GPU_UUID=uuid,one_original_writer=True,original_owner_pid=os.getpid(),canonical_binding=canonical,source_model_SHA=e['source_SHA'],num_envs=20000,actor_obs=35,critic_obs=38,action_dim=6,physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,asset_USD_SHA=USD,asset_contract_SHA=CONTRACT,manifest_SHA=mh,root_admission_SHA=ash,learning_started_epoch=now,max_parent_seconds=3900,save_deadline=now+3600,nominal_end_epoch=now+3900,exit_headroom_seconds=300,max_additional_updates=20,stop_file=str(job/'STOP_AFTER_SAVE.json'))
 allfds=global_fds+[private.fileno(),finite.fileno()];task.update(owner_parent_pid=os.getpid(),inherited_lock_fds=allfds,go_file=str(job/'GO_PRODUCTION.json'),rescue_stop_file=str(job/'STOP_AFTER_SAVE.json'),additional_updates=20,save_interval=5,source_read_purpose='NEW_'+e['role']+'_FULL20K_POSTTRAIN20_'+run)
 if e['source_family']=='e1':
  sys.path.insert(0,str(job));from e1_posttrain_make_task import make_task
  parent_fields={k:task[k]for k in('run_id','role_key','GPU_UUID','canonical_path','owner_parent_pid','inherited_lock_fds','root_admission_file','root_admission_SHA','go_file','rescue_stop_file','asset_dir','source_read_purpose','additional_updates','save_interval','seed','exit_headroom_seconds','max_parent_seconds')}
  task=make_task(e['task_template'],parent_fields,admission,go,now=now,environ={'CUDA_VISIBLE_DEVICES':uuid},fd_check=os.fstat)
 if e['source_family']=='w35':
  ready=dict(passed=True,kind=task['kind'],source_SHA=e['source_SHA'],source_iteration=task['source_iteration'],Adam_step=task['source_Adam_step'],source_LR=task['source_LR'],source_GPU_fullrestore_proof_SHA=task['source_GPU_fullrestore_proof_SHA'],asset_USD_SHA=USD,asset_contract_SHA=CONTRACT,root_admission_SHA=ash,manifest_SHA=mh,evidence_scope='Historical exact source actual full20k proof and fresh original owner/resource/budget admission; not a new live training pass')
  put(job/task['ready_file'],ready);go['source_CPU_SHA']=hashlib.sha256(json.dumps(ready,indent=2).encode()).hexdigest()
 put(job/'TASK.json',task);return task,go

def main():
 require(not(B/'OWNER_STARTED.json').exists(),'Unused original owner once');plan=b.read(B/'OWNER_PLAN.json');run=plan['run_id'];verify_sources(plan);put(B/'OWNER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),run_id=run,H1_excluded=True,no_new_budget_ledger=True))
 locks=[];private={};finite=None;active=False;go={};rows={};slots={};errors=[];blocked_families=set();pending=list(plan['entries']);c=None
 def stop(slot,reason):
  e=slot['entry'];job=Path(e['job_root']);dest=job/e.get('stop_relative','STOP_AFTER_SAVE.json');value=dict(epoch=time.time(),reason=reason,complete_own_save_and_exit_only=True)
  if dest.parent.exists():put(dest,value)
  else:put(job/'PENDING_PARENT_STOP.json',value)
 try:
  wait_until=time.monotonic()+1800
  while True:
   try:
    for path in b.LOCKS:
     f=path.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    c=b.read(C);require(c['active_segment']is None and authority_tracking_schema_admitted(c)and authority_original_extension_count(c)==9 and authority_budget_GO_allowed(c)and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return','Original finite authority not admitted')
    require(c['remaining_training_seconds']>RESERVE+7800,'Original reserve plus initial two finite windows')
    for u in UUIDS:
     f=(C.parent.parent/('three_expert_v2_'+u+'.lock')).open('rb+');private[u]=f;fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);gpu(u)
    finite=(C.parent.parent/'finite_environment_validation.lock').open('rb+');fcntl.flock(finite,fcntl.LOCK_SH|fcntl.LOCK_NB);break
   except BlockingIOError as busy:
    for f in[*private.values(),finite,*reversed(locks)]:
     if f is not None:fcntl.flock(f,fcntl.LOCK_UN);f.close()
    private={};finite=None;locks=[];put(B/'PREGO_RESOURCE_WAIT.json',dict(epoch=time.time(),reason=str(busy),partial_locks_held=0,SDK_PT_GO_or_canonical_writes=False))
    if time.monotonic()>=wait_until:raise TimeoutError('Original resource wait1800 expired before any GO')
    time.sleep(30)
  while pending or slots:
   if active:c=account(run,go,rows)
   for u,slot in list(slots.items()):
    p=slot['p'];e=slot['entry'];key=e['role_key']
    if p.poll()is None:
     if time.time()>=go[key]['save_deadline']or c['remaining_training_seconds']<=RESERVE+300*len(slots):stop(slot,'Original finite save deadline/reserve with save headroom')
     continue
    rc=p.wait();job=Path(e['job_root']);final=b.read(job/e['final_file']);rows[key]=dict(key=key,role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),final=final,original_error=bool(rc!=0),manifest_SHA=go[key]['manifest_SHA']);put(job/'PARENT_WAITED_ACTUAL.json',rows[key]);del slots[u];c=account(run,go,rows)
    if rc!=0:
     completed=(final or {}).get(e.get('final_updates_key','completed_actual_updates'),0)
     if completed==0:blocked_families.add(e['source_family'])
     errors.append(dict(role=e['role'],reason='Original error retained; no unchanged startup-family replay when no complete update published',rc=rc,completed_updates_reported=completed,partial_optimizer_steps_not_assumed_zero=True))
   for u in UUIDS:
    if u in slots:continue
    eligible=next((e for e in pending if e['source_family']not in blocked_families),None)
    if eligible is None:continue
    if c['remaining_training_seconds']<=RESERVE+3900*(len(slots)+1):break
    resource=gpu(u);e=eligible;job=Path(e['job_root']);task,g=task_and_go(e,u,c,run,[f.fileno()for f in locks],private[u],finite,resource)
    if not active:
     now=time.time();c=b.read(C);require(c['active_segment']is None,'Same original canonical owner admission');c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),owner_run_id=run,kind='Linux_MOD4V1_EIGHT_EXCLUDING_H1_POSTTRAIN_'+run,started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='Original charge_values expertseconds: actual load learn save SDKclose childwait, no clamp/refund/uncharged tail');put(C,c);active=True
    require(not(job/'GO_PRODUCTION.json').exists(),'Unused role GO');go[e['role_key']]=g;put(job/'GO_PRODUCTION.json',g);argv=[str(x).replace('{JOB}',str(job)).replace('{RUN}',run)for x in e['worker_argv']];log=(job/'PPO_FULL_STDOUT_STDERR.log').open('xb')
    try:p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',*argv],cwd=job,env=environment(job,u),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=tuple(f.fileno()for f in locks)+(private[u].fileno(),finite.fileno()),start_new_session=True)
    except BaseException:
     log.close();rows[e['role_key']]=dict(key=e['role_key'],role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=1,owner_received_terminal_epoch=time.time(),original_error=True,spawn_error=traceback.format_exc());raise
    log.close();slots[u]=dict(p=p,entry=e);pending.remove(e);put(job/'WORKER_IDENTITY_ACTUAL.json',b.ident(p.pid));c=account(run,go,rows)
   if pending and not slots and all(e['source_family']in blocked_families for e in pending):break
   if pending and not slots and c['remaining_training_seconds']<=RESERVE+3900:break
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),run_id=run,workers={u:dict(role=s['entry']['role'],identity=b.ident(s['p'].pid))for u,s in slots.items()},terminal_roles=[r['role']for r in rows.values()],pending_roles=[e['role']for e in pending],blocked_families=sorted(blocked_families),canonical_remaining_seconds=c['remaining_training_seconds'],original_one_writer=True))
   if slots:time.sleep(3)
  if active:c=account(run,go,rows,True);active=False
  put(B/'COHORT_FINAL.json',dict(run_id=run,rows=rows,go=go,original_cost_settled=not active,all_own_children_waited=not slots,pending_unstarted_roles=[e['role']for e in pending],errors=errors,H1_excluded=True,skill_qualification='PENDING_FROZEN_ORIGINAL_SCOPE_EVALUATION',no_automatic_extra_PPO_window=True))
 except BaseException:
  errors.append(dict(parent_error=traceback.format_exc()));put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),errors=errors,active_not_falsely_cleared=active))
  for slot in slots.values():stop(slot,'Original owner exception; complete full own save and exit, no force kill')
  while slots:
   for u,slot in list(slots.items()):
    p=slot['p']
    if p.poll()is not None:
     e=slot['entry'];rc=p.wait();rows[e['role_key']]=dict(key=e['role_key'],role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),original_error=True,final=b.read(Path(e['job_root'])/e['final_file']));del slots[u]
   if active:c=account(run,go,rows)
   if slots:time.sleep(3)
  if active:account(run,go,rows,True);active=False
 finally:
  waited=not slots
  if waited:
   for f in[finite,*private.values(),*reversed(locks)]:
    if f is not None:fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),run_id=run,original_cost_settled=not active,all_own_children_waited=waited,original_private_finite_authority_leases_released=waited,errors=errors,H1_excluded=True,no_new_budget_or_refund=True))
if __name__=='__main__':main()
