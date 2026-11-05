"""Finite original-canonical E3 Fudan-sequence PPO owner, not a new ledger.
Original charge_values/authority locks/privateGPU EX/finiteSH/resource gates.
Fresh N20000 Fudan learner; only original1cd actor/critic MLP warm start; timeout8.
"""
from pathlib import Path
import os,sys,time,json,hashlib,fcntl,subprocess,traceback,shutil
import three_slot_common_v1 as b
from single_writer72_authority_V85M_source import authority_tracking_schema_admitted,authority_original_extension_count,authority_budget_GO_allowed
B=Path(__file__).resolve().parent;C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');UUIDS=('GPU-16828f91-2b45-b646-8dc0-9481138e2842',);ROLES={'E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'};RESERVE=86412.86069250107;put=b.put;KIND='MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1'
PINNED_MOTHER={'path':'/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt','SHA':'1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8','bytes':14715029,'iteration':43090}
def require(v,msg):
 if not v:raise RuntimeError(msg)
def gpu(uuid):
 import psutil
 raw=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip()for x in raw.split(',')];apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);require(a[0]==uuid and a[1]=='NVIDIA GeForce RTX 4090','Exact authorized4090')
 if not(int(a[2])>15669 and int(a[3])<=30 and uuid not in apps and psutil.virtual_memory().available>64*1024**3 and shutil.disk_usage(B).free>50*1024**3):raise BlockingIOError('Original GPU/host light admission not ready')
 return dict(epoch=time.time(),GPU_UUID=uuid,GPU_line=raw,compute_empty=True,RAM_available=psutil.virtual_memory().available,disk_free=shutil.disk_usage(B).free)
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
 require(b.C.resolve()==C.resolve() and plan['H1_excluded'] and len(plan['entries'])==1 and plan['entries'][0]['role']=='E3','Original canonical and exactly one E3 warm branch')
 for e in plan['entries']:
  J=Path(e['job_root']);require(J.resolve().is_relative_to(B/'roles')and not(J/'GO_PRODUCTION.json').exists(),'Unused own job')
  require(e['num_envs']==20000 and e['steps_per_env']==48 and 1<=e['max_iterations']<=300,'Declared finite N20000 Fudan PPO cohort')
  m=b.read(J/'INSTALL_MANIFEST.json');require(m['source_PT_copied']is False and m['kind']==KIND,'Only sealed sources/assets, not a copied selected model')
  for f in m['files']:
   p=J/f['path'];require(p.resolve().is_relative_to(J)and p.suffix.lower()not in('.pt','.pth','.ckpt','.onnx','.safetensors'),'No selected weights in install verification')
   require(p.stat().st_size==f['bytes']and b.H(p)==f['sha256'],'Pinned own source dependency')
  require(e['teacher']['SHA']=='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'and e['teacher']['bytes']==14715029,'Selected E3 mother mean/value warm start only')
  require(e.get('source_kind')=='fdn_fresh_mlp_warm_1cd_n20000_timeout8_lowstd005_lrscale001'and e['teacher']==PINNED_MOTHER and e['max_iterations']==25 and 'learner_source'not in e,'Fresh original1cd MLP warm-only25 pilot; no PT read here');require(m['asset_USD_SHA']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'and m['asset_contract_SHA']=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755','Unchanged native asset identity')

def admit(e,u,c,run,locks,private,finite,resource):
 J=Path(e['job_root']);now=time.time();binding=dict(path=str(C),generation=c['authority_generation'],owner_run_id=run,owner_parent_pid=os.getpid(),one_original_writer=True);fds=[f.fileno()for f in locks]+[private.fileno(),finite.fileno()]
 ad=dict(kind=KIND,epoch=now,role='E3',role_key=e['role_key'],run_id=run,parent_pid=os.getpid(),owner_parent_pid=os.getpid(),gpu_uuid=u,GPU_UUID=u,canonical_binding=binding,inherited_lock_fds=fds,actual_original_authority_EX_private_GPU_EX_finite_SH=True,original_canonical_owner_admitted=True,authority_two_EX=True,private_GPU_EX=True,finite_SH=True,actual_resource=resource)
 put(J/'ROOT_ADMISSION_ACTUAL.json',ad);put(J/'ACTUAL_RESOURCE_LEASES.json',dict(**resource,inherited_lock_fds=fds,owner_parent_pid=os.getpid(),authority_two_EX=True,private_GPU_EX=True,finite_SH=True));put(J/'ACTUAL_CANONICAL_READ.json',dict(epoch=now,path=str(C),SHA=b.H(C),remaining_seconds=c['remaining_training_seconds'],charged_seconds=c['charged_training_seconds'],strict_reserve_seconds=RESERVE,binding=binding))
 task=dict(kind=KIND,role='E3',family='e0_e2_e3',run_id=run,role_key=e['role_key'],gpu_uuid=u,num_envs=e['num_envs'],seed=e['seed'],max_iterations=e['max_iterations'],steps_per_env=48,teacher=e['teacher']['path'],teacher_sha256=e['teacher']['SHA'],teacher_bytes=e['teacher']['bytes'],teacher_iter=43090,owner_parent_pid=os.getpid(),inherited_lock_fds=fds,root_admission_sha256=b.H(J/'ROOT_ADMISSION_ACTUAL.json'),install_manifest_sha256=b.H(J/'INSTALL_MANIFEST.json'),original_protocol=plan_protocol(),asset_sha256='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_sha256='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755')
 task.update(source_kind=e['source_kind'],warm_start_only=True,full_learner_resume=False,inherited_old_iterations=0,teacher_metadata_is_ancestral_only=False);put(J/'TASK.json',task)
 go=dict(kind=KIND,role='E3',run_id=run,role_key=e['role_key'],gpu_uuid=u,learning_started_epoch=now,max_parent_seconds=3900,save_deadline=now+3600,save_deadline_epoch=now+3600,nominal_end_epoch=now+3900,shutdown_headroom_seconds=300,exit_headroom_seconds=300,task_sha256=b.H(J/'TASK.json'),root_admission_sha256=task['root_admission_sha256'],install_manifest_sha256=task['install_manifest_sha256'],canonical_binding=binding,teacher_sha256=e['teacher']['SHA'])
 return task,go

def plan_protocol():return dict(physics_dt=.0025,policy_hz=50,feedback_hz=100,TGS=[32,4],gas_N=400,stiffness_N_m=2000,damping_Ns_m=3,closure_m=.01,mimic_rad=.01,full_D0_D7=True,algorithm='PPO_plus_five_frame_supervised_velocity_encoder',warm_start_only=True,full_fdn_learner_continuation=False,fresh_Fudan_learner=True,inherited_old_iterations=0,source_environment_DR_history_queues_not_resumed=True,source_envs=20000,new_envs=20000,stream_cut=True,lowrise_episode_timeout_s=8.0,initial_policy_gaussian_std=.05,main_optimizer_LR_schedule_scale=.01,main_initial_learning_rate=1e-5,main_min_learning_rate=1e-7,main_max_learning_rate=1e-4,tracking_heightgate_enabled=False,original_global_episode_length_unchanged=True,new_lowrise_curriculum=True,original_frozen_74_grader_unchanged=True,whole_leg_same_end_video_pose_covered=False)
def qualify_waited(J,rc,final):
 # Actual child.wait has occurred before this hook. New FDN metadata is never sent to a SM gate.
 sys.path.insert(0,str(J/'worker_sources'))
 from fudan_worker_close_contract_v1 import qualify_actual_wait
 return bool(qualify_actual_wait(J,rc,final))

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
    rc=p.wait();J=Path(e['job_root']);final=b.read(J/'production/FDN_FINAL.json');qualified=qualify_waited(J,rc,final);rows[key]=dict(key=key,role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),final=final,original_error=not qualified);put(J/'PARENT_WAITED_ACTUAL.json',rows[key]);del slots[u];c=account(run,go,rows)
    if not qualified:
     errors.append(dict(role=e['role'],returncode=rc,reason='Realerrorpreservednoautomaticunchangedretry'));blocked=True
   for u in UUIDS:
    if u in slots or blocked or not pending:continue
    if c['remaining_training_seconds']<=RESERVE+3900*(len(slots)+1):break
    e=pending[0];resource=gpu(u);J=Path(e['job_root']);task,g=admit(e,u,c,run,locks,private[u],finite,resource)
    if not active:
     now=time.time();c=b.read(C);require(c['active_segment']is None,'Originaluniqueowner');c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),owner_run_id=run,kind='Linux_MOD4V1_E3_FUDAN_SEQUENCE_PPO_'+run,started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='Originalcharge_valuesexpertsecondsactualGOthroughload-single1cd-MLP-warm-freshFDN-sequence-PPO-fullsave-SDKclose-parentwait; noclamprefundextension');put(C,c);active=True
    key=e['role_key'];require(not(J/'GO_PRODUCTION.json').exists(),'UnusedworkerGO');go[key]=g;put(J/'GO_PRODUCTION.json',g);log=(J/'FDN_FULL_STDOUT_STDERR.log').open('xb')
    try:p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(J/'worker_sources/worker_fudan_sequence_ppo_native_v1.py'),'--job-root',str(J)],cwd=J,env=environment(J,u),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=tuple(task['inherited_lock_fds']),start_new_session=True)
    except BaseException:log.close();rows[key]=dict(key=key,role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=1,owner_received_terminal_epoch=time.time(),original_error=True);raise
    log.close();slots[u]=dict(p=p,entry=e);pending.pop(0);put(J/'WORKER_IDENTITY_ACTUAL.json',b.ident(p.pid));c=account(run,go,rows)
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),run_id=run,workers={u:dict(role=s['entry']['role'],identity=b.ident(s['p'].pid))for u,s in slots.items()},terminal_roles=[r['role']for r in rows.values()],pending_roles=[e['role']for e in pending],blocked_after_real_error=blocked,canonical_remaining_seconds=c['remaining_training_seconds'],max_new_policy_iterations=300,training_num_envs=20000,final_skill_goal=.9,not_yet_skill_pass_claim=True))
   if not slots and(blocked or not pending or c['remaining_training_seconds']<=RESERVE+3900):break
   if slots:time.sleep(3)
  if active:account(run,go,rows,True);active=False
  put(B/'COHORT_FINAL.json',dict(run_id=run,rows=rows,go=go,pending_unstarted_roles=[e['role']for e in pending],all_own_children_waited=not slots,original_cost_settled=not active,errors=errors,H1_excluded=True,original_skill_evaluation='PENDING_FROZEN_ACCEPTANCE_NOT_LOSS',newledger_or_extension=False))
 except BaseException:
  errors.append(dict(parent_error=traceback.format_exc()));put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),errors=errors,active_not_falsely_cleared=active))
  for slot in slots.values():stop(slot,'Ownoriginalownerexception')
  while slots:
   for u,s in list(slots.items()):
    if s['p'].poll()is not None:e=s['entry'];rc=s['p'].wait();rows[e['role_key']]=dict(key=e['role_key'],role=e['role'],phase='terminal',terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time(),original_error=True,final=b.read(Path(e['job_root'])/'production/FDN_FINAL.json'));del slots[u]
   if active:account(run,go,rows)
   if slots:time.sleep(3)
  if active:account(run,go,rows,True);active=False
 finally:
  if not slots:
   for f in[finite,*private.values(),*reversed(locks)]:
    if f is not None:fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),run_id=run,all_own_children_waited=not slots,original_cost_settled=not active,original_leases_released=not slots,errors=errors,H1_excluded=True,no_newbudget_refund_or_extension=True))
if __name__=='__main__':main()
