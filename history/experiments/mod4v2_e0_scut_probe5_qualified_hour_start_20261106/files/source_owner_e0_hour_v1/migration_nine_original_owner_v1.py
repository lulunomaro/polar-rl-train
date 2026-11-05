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
ROLES={'E0','E2','E3','H1_normal','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'}
USD='7361b6930a7270e65f3b290cfa71c50f8e1f0beccaa9cab1fa8a994f03cb35b8';CONTRACT='f01ffcf0f967e1c1f8dc153c9e06d73a70ab3f78e17e8b479159c14a6cf63047'
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
 require(b.C.resolve()==C.resolve(),'Original canonical path only')
 require(plan['kind']=='MOD4V2_NINE_ORIGINAL_OWNER_SOURCE_PLAN_V1'and plan['H1_excluded']is False,'User authorized all9 migration including separate H1 candidate')
 entries=plan['entries'];require(len(entries)==1 and entries[0]['role']=='E0' and plan['native_asset_gate_role']=='E0','Human serial E0-only current window');require(1<=len(entries)<=9 and len({e['role']for e in entries})==len(entries)and all(e['role']in ROLES for e in entries),'Unique authorized roles')
 require(len({e['role_key']for e in entries})==len(entries),'Unique original charge keys')
 for e in entries:
  job=Path(e['job_root']);job.resolve().relative_to(B.resolve());require(not(job/'GO_PRODUCTION.json').exists(),'Unused own role')
  require(e['max_additional_updates']==1000000 and e['num_envs']==20000 and e['max_parent_seconds']==3900 and e['save_after_seconds']==3600 and e['exit_headroom_seconds']==300,'Original finite wall-clock hour')
  m=json.loads((job/e['manifest_file']).read_text());require(m['source_PT_copied']is False and m['native0PT_status']=='PENDING_ACTUAL_FRESH_V2_WORKER_INITIALIZATION','Source stage is not SDK or restore proof')
  for f in m['files']:
   p=job/f['relative'];p.resolve().relative_to(job.resolve());require(p.suffix.lower()not in('.pt','.pth','.ckpt','.safetensors','.onnx'),'No source model stat/hash');raw=p.read_bytes();require(len(raw)==f['bytes']and hashlib.sha256(raw).hexdigest()==f['SHA256'],'Exact staged own role input')
  for f in m['shared_files']:
   p=B/f['relative'];p.resolve().relative_to(B.resolve());require(p.suffix.lower()not in('.pt','.pth','.ckpt','.safetensors','.onnx'),'No shared model input');raw=p.read_bytes();require(len(raw)==f['bytes']and hashlib.sha256(raw).hexdigest()==f['SHA256'],'Exact shared V2 package/worker/close helpers')
  require(e['source_SHA']==m['source_SHA']and e['source_bytes']==m['source_bytes']and e['source_iteration']==m['source_iteration'],'Formal frozen metadata binding, no source-byte operation')
 require((B/'v2_package/assets/robot.usd').is_file()and hashlib.sha256((B/'v2_package/assets/robot.usd').read_bytes()).hexdigest()==USD,'Actual V2 asset identity')
 require(hashlib.sha256((B/'v2_package/assets/import_contract.json').read_bytes()).hexdigest()==CONTRACT,'Actual V2 contract identity')
 local=json.loads((B/'V2_LOCAL_VALIDATION.json').read_bytes());require(local['passed']is True and all(local['checks'].values()),'Local validation distinct from mandatory live worker native checks')

def task_and_go(e,uuid,c,run,global_fds,private,finite,resource):
 job=Path(e['job_root']);(job/'production').mkdir(exist_ok=True);now=time.time();bind=dict(canonical_path=str(C),authority_generation=c['authority_generation'],owner_run_id=run,owner_parent_pid=os.getpid(),one_original_writer=True)
 put(job/'ACTUAL_CANONICAL_READ.json',dict(canonical_SHA=hashlib.sha256(C.read_bytes()).hexdigest(),remaining_training_seconds=c['remaining_training_seconds'],charged_training_seconds=c['charged_training_seconds'],reserve_seconds=RESERVE,run_id=run,owner_parent_pid=os.getpid(),original_two_EX_locks_held=True))
 put(job/'ACTUAL_RESOURCE_LEASES.json',dict(GPU_UUID=uuid,parent_pid=os.getpid(),original_owner_EX_held=True,private_GPU_EX_held=True,finite_environment_SH_held=True,inherited_global_fds=global_fds,private_GPU_fd=private.fileno(),finite_fd=finite.fileno()))
 admission=dict(kind='ROOT_MOD4V2_NINE_MIGRATION_ACTUAL_ADMISSION_V1',run_id=run,role=e['role'],parent_pid=os.getpid(),GPU_UUID=uuid,num_envs=20000,canonical=bind,fresh_resource_checks=resource,USD_SHA=USD,contract_SHA=CONTRACT,original_two_EX_owner_locks_held=True,original_private_GPU_EX_held=True,original_shared_finite_environment_held=True,original_budget_currently_admitted=True,fullrestore_proof_reused_as_history_not_new_training_restore=True,new_V2_native0PT_passed=False,worker_native_before_source_read_required=True,v1_source_checkpoint_complete_history_only=True,new_budget_or_ledger=False)
 put(job/'ROOT_ADMISSION_ACTUAL.json',admission);ah=hashlib.sha256((job/'ROOT_ADMISSION_ACTUAL.json').read_bytes()).hexdigest();mh=hashlib.sha256((job/e['manifest_file']).read_bytes()).hexdigest();fds=global_fds+[private.fileno(),finite.fileno()]
 task=dict(e);task.update(kind='MOD4V2_EXPERT_ORIGINAL_PPO_MIGRATION_V1',run_id=run,GPU_UUID=uuid,canonical_path=str(C),canonical_binding=bind,owner_pid=os.getpid(),actual_parent_pid=os.getpid(),inherited_lock_fds=fds,root_admission_file=str(job/'ROOT_ADMISSION_ACTUAL.json'),root_admission_SHA=ah,source_manifest_SHA=mh,original_runtime_root=str(job),original_entry=e['entry'],original_run_manifest=str(job/e.get('original_run_manifest_relative','original_run_manifest.json')),v2_package=str(B/'v2_package'),helper_root=str(B/'helpers'),max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,max_additional_updates=1000000,num_envs=20000,window_mode='ORIGINAL_FINITE_WALL_CLOCK_HOUR',steps_per_env=e.get('steps_per_env',24),seed=20260928,stop_file=str(job/'STOP_AFTER_SAVE.json'),save_deadline=now+3600,nominal_end_epoch=now+3900,go_file=str(job/'GO_PRODUCTION.json'),job_root=str(job),output_dir=str(job/'production'),source_read_purpose='NEW_V2_'+e['role']+'_FULL20K_ORIGINAL_HOUR_'+run)
 go=dict(kind='MOD4V2_NINE_ORIGINAL_OWNER_GO_V1',max_parent_seconds=3900,run_id=run,role=e['role'],GPU_UUID=uuid,parent_pid=os.getpid(),source_SHA=e['source_SHA'],num_envs=20000,actor_obs=35,critic_obs=38,action_dim=6,physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,USD_SHA=USD,contract_SHA=CONTRACT,manifest_SHA=mh,root_admission_SHA=ah,canonical=bind,learning_started_epoch=now,save_deadline=now+3600,nominal_end_epoch=now+3900,exit_headroom_seconds=300,stop_file=str(job/'STOP_AFTER_SAVE.json'),native_validation_pending_not_false_claim=True)
 put(job/'TASK.json',task);return task,go

def qualify_v2_waited(job,e,final,pid,rc):
 errors=[];checks={};f=final or {}
 checks['actual_rc0']=rc==0;checks['actual_worker_and_parent']=f.get('worker_pid')==pid and f.get('parent_pid')==os.getpid()
 checks['execution_final']=f.get('passed_execution')is True and f.get('completed_requested_update_window')is True and f.get('error')is None and f.get('close_errors')==[]
 checks['finite_hour_actual']=type(f.get('completed_actual_updates'))is int and f['completed_actual_updates']>0 and f.get('window_mode')=='ORIGINAL_FINITE_WALL_CLOCK_HOUR' and f.get('requested_update_quota')is None and f.get('stop_reason')in('STOP_SAVE','save_deadline') and f.get('actual_optimizer_steps')==20*f['completed_actual_updates'] and f.get('actual_rollout_controls')==24*f['completed_actual_updates']
 checks['V2_asset']=f.get('target_asset_SHA')==USD and f.get('target_contract_SHA')==CONTRACT
 io=f.get('source_IO')or{};checks['source_once']=all(io.get(k)==1 for k in('physical_byte_opens','SHA_calculations','CPU_decodes'))
 checks['no_v1_env_applied']=f.get('source_env_state_applied')is False
 latest=f.get('latest_complete_save')or{};checks['complete_source_output']=bool(latest.get('path')and latest.get('bytes',0)>0 and len(latest.get('sha256',''))==64)
 checks['worker_error_absent']=not list((job/'production').glob('*ERROR*.json'))
 np=job/'production/V2_NATIVE_INITIALIZED.json';native=json.loads(np.read_bytes())if np.exists()else{}
 checks['fresh_V2_before_PT']=native.get('source_weights_opens')==native.get('source_decodes')==0 and native.get('num_envs')==20000 and native.get('explicit_new_environment_resets')==1 and native.get('old_physical_state_restores')==0 and native.get('pretraining_validation_controls')==1 and native.get('pretraining_validation_physics_steps')==8 and native.get('pretraining_validation_feedback_ticks')==2 and native.get('source_env_state_applied')is False
 ip=job/'production/V2_APP_CLOSE_INTENT.json'
 if ip.exists():
  intent=json.loads(ip.read_bytes());fp=job/e['final_file'];checks['intent_final_binding']=intent.get('final_sha256')==hashlib.sha256(fp.read_bytes()).hexdigest()and intent.get('worker_pid')==pid and intent.get('parent_pid')==os.getpid()and intent.get('error_before_close')is False and intent.get('env_close_returned')is True and intent.get('original_app_close_arguments')==[] and intent.get('original_fast_shutdown_unchanged')is True and (intent.get('original_bound_close')or{}).get('fast_shutdown')is True
 else:checks['intent_final_binding']=False
 return dict(kind='MOD4V2_MIGRATION_ACTUAL_CHILD_WAIT_QUALIFICATION_V1',role=e['role'],qualified=all(checks.values()),checks=checks,actual_child_wait_returned=True,actual_child_pid=pid,actual_parent_pid=os.getpid(),errors=errors,skill_graduated=False)

def main():
 require(not(B/'OWNER_STARTED.json').exists(),'Unused original owner once');plan=b.read(B/'OWNER_PLAN.json');run=plan['run_id'];verify_sources(plan);put(B/'OWNER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),run_id=run,H1_excluded=False,no_new_budget_ledger=True))
 locks=[];private={};finite=None;active=False;go={};rows={};slots={};errors=[];blocked_families=set();pending=list(plan['entries']);c=None;native_gate_role=plan.get('native_asset_gate_role');native_gate_ready=not bool(native_gate_role)
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
    require(c['remaining_training_seconds']>RESERVE+3900,'Original reserve plus initial one finite window')
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
    rc=p.wait();job=Path(e['job_root']);final=b.read(job/e['final_file']);rows[key]=dict(key=key,role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),final=final,original_error=bool(rc!=0),manifest_SHA=go[key]['manifest_SHA']);q=qualify_v2_waited(job,e,final,p.pid,rc);rows[key]['semantic_qualification']=q;rows[key]['original_error']=bool(rc!=0 or not q['qualified']);put(job/'PARENT_WAITED_ACTUAL.json',rows[key]);del slots[u];c=account(run,go,rows)
    if rc!=0 or not(final or {}).get('passed_execution',False) or not(final or {}).get('completed_requested_update_window',False)or not q['qualified']:
     completed=(final or {}).get(e.get('final_updates_key','completed_actual_updates'),0)
     if completed==0:blocked_families.add(e['source_family'])
     errors.append(dict(role=e['role'],reason='Original error retained; no unchanged startup-family replay when no complete update published',rc=rc,completed_updates_reported=completed,partial_optimizer_steps_not_assumed_zero=True))
   if not native_gate_ready:
    gate_entry=next(e for e in plan['entries']if e['role']==native_gate_role);gate_job=Path(gate_entry['job_root']);native=b.read(gate_job/'production/V2_NATIVE_INITIALIZED.json')
    if native is not None:
     require(native['role']==native_gate_role and native['run_id']==run and native['owner_pid']==os.getpid()and native['num_envs']==20000 and native['source_weights_opens']==native['source_decodes']==0 and native['pretraining_validation_controls']==1 and native['pretraining_validation_physics_steps']==8 and native['pretraining_validation_feedback_ticks']==2 and native['source_env_state_applied']is False,'Shared native D0 gate must be actual fresh V2 before source PT')
     native_gate_ready=True;put(B/'SHARED_V2_NATIVE_GATE_PASSED.json',dict(epoch=time.time(),role=native_gate_role,run_id=run,native_receipt_SHA=b.H(gate_job/'production/V2_NATIVE_INITIALIZED.json'),worker_pid=native['pid'],no_skill_claim=True))
    elif gate_entry['role_key']in rows:
     blocked_families.update(e['source_family']for e in pending);put(B/'SHARED_V2_NATIVE_GATE_FAILED.json',dict(epoch=time.time(),role=native_gate_role,all_following_roles_not_started=True,pending_roles=[e['role']for e in pending],no_unchanged_shared_asset_failure_replay=True));errors.append(dict(shared_native_gate_failed=native_gate_role,remaining_roles_not_started=True))
   for u in UUIDS:
    if u in slots:continue
    eligible=next((e for e in pending if e['source_family']not in blocked_families and(native_gate_ready or e['role']==native_gate_role)),None)
    if eligible is None:continue
    if c['remaining_training_seconds']<=RESERVE+3900*(len(slots)+1):break
    resource=gpu(u);e=eligible;job=Path(e['job_root']);task,g=task_and_go(e,u,c,run,[f.fileno()for f in locks],private[u],finite,resource)
    if not active:
     now=time.time();c=b.read(C);require(c['active_segment']is None,'Same original canonical owner admission');c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),owner_run_id=run,kind='Linux_MOD4V2_NINE_INCLUDING_H1_MIGRATION_'+run,started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='Original charge_values expertseconds: actual load learn save SDKclose childwait, no clamp/refund/uncharged tail');put(C,c);active=True
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
  put(B/'COHORT_FINAL.json',dict(run_id=run,rows=rows,go=go,original_cost_settled=not active,all_own_children_waited=not slots,pending_unstarted_roles=[e['role']for e in pending],errors=errors,H1_excluded=False,skill_qualification='PENDING_FROZEN_ORIGINAL_SCOPE_EVALUATION',no_automatic_extra_PPO_window=True))
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
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),run_id=run,original_cost_settled=not active,all_own_children_waited=waited,original_private_finite_authority_leases_released=waited,errors=errors,H1_excluded=False,no_new_budget_or_refund=True))
if __name__=='__main__':main()
