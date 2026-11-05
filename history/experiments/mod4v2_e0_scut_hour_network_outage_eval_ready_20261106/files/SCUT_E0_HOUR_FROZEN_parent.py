"""Original complete supervisor specialized to one E0 worker; actual waits, durable intent qualification and original resource gates. No learner/GO/ledgerwrite."""
from pathlib import Path
import os,sys,json,time,hashlib,fcntl,subprocess,traceback,signal,shutil
import psutil
import math
B=Path(__file__).resolve().parent;OWN=Path('/home/lc01/Zonglin Li/zonglin2')
def put(n,v):
 p=B/n;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2,allow_nan=False));q.replace(p)
def nvidia(uuid):
 raw=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();x=[v.strip()for v in raw.split(',')];return dict(GPU_UUID=x[0],name=x[1],total_MiB=int(x[2]),free_MiB=int(x[3]),utilization_percent=int(x[4]))

def require(value, message):
 if not value:raise RuntimeError(message)

def own_json(path):
 p=Path(path);require(p.suffix.lower()=='.json' and p.resolve().is_relative_to(B.resolve()),'Own eval JSON only');return json.loads(p.read_bytes())

def make_task(r,plan,deadline,fds):
 require(r['role']=='E0' and len(fds)==2,'Single E0 and original two EX descriptors')
 ad=own_json(B/'ACTUAL_GROUP_ADMISSION.json');receipt=dict(plan['migration_close'])
 require(receipt['roles']==['E0'] and all(receipt[k] is True for k in ('all_closed','actual_wait_complete','resources_released','original_cost_settled','semantic_qualified')),'Actual training close gate')
 require(ad['epoch']>=receipt['closed_epoch'] and ad['selected_card_compute_processes']==[] and ad['resource']['free_MiB']>=23500 and ad['resource']['utilization_percent']==0,'Actual post-close empty-card observation')
 # GPU_settled is derived only NOW, under the two successfully acquired EXs.
 receipt.update(GPU_settled=True,GPU_settle_evidence=dict(epoch=ad['epoch'],GPU_UUID=plan['GPU_UUID'],resource=ad['resource'],compute_processes=[],private_GPU_EX_held=True,global_finite_EX_held=True))
 out=B/'cases/E0';task=dict(plan['task_template'])
 task.update(kind='MOD4V2_N80_FRESH_FULLDR_FROZEN_FINITE_NOT_GRADUATION',role='E0',num_envs=80,controls=1000,seed=20260928,eval_members=['E0'],run_id=plan['group_id'],group_id=plan['group_id'],group_root=str(B),output_dir=str(out),job_root=str(out),owner_pid=os.getpid(),GPU_UUID=plan['GPU_UUID'],absolute_worker_deadline_epoch=deadline,max_additional_updates=1,steps_per_env=24,helper_root=str(B/'helpers'),v8_helper_root=str(B/'worker_sources/parent'),e1_helper_root=str(B/'worker_sources/e1'),migration_cohort_close_receipt=receipt,eval_admission=dict(group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],private_GPU_EX_held=True,global_finite_EX_held=True,inherited_lock_fds=list(fds),admitted_epoch=ad['epoch']),source_read_purpose='NEW_SCUT_E0_HOUR_FROZEN_N80_'+plan['group_id'])
 return task

def qualify_waited_e0(out,pid,rc,plan):
 # Called only AFTER the actual child p.wait() has returned.
 checks={};detail={};f={};intent={};ready={};started={};pre={};envclose={}
 try:
  fp=out/'V2_FROZEN_EVAL_FINAL.json';raw=fp.read_bytes();f=json.loads(raw)
  intent=own_json(out/'V2_FROZEN_EVAL_APP_CLOSE_INTENT.json');ready=own_json(out/'WORKER_SCENE_READY.json');started=own_json(out/'WORKER_EVAL_STARTED.json');pre=own_json(out/'PRE_CLOSE.json');envclose=own_json(out/'ENV_CLOSE_RETURNED.json');task_raw=(out/'task.json').read_bytes();task=json.loads(task_raw);expect=plan['task_template']
  checks['actual_child_wait_RC0']=rc==0
  checks['actual_worker_parent_identity']=f.get('worker_pid')==pid and f.get('parent_pid')==os.getpid() and intent.get('worker_pid')==pid and intent.get('parent_pid')==os.getpid()
  checks['single_E0_new_purpose']=f.get('role')==intent.get('role')=='E0' and f.get('run_id')==intent.get('run_id')==f.get('group_id')==plan['group_id'] and f.get('GPU_UUID')==plan['GPU_UUID']
  checks['task_binding']=f.get('task_sha256')==intent.get('task_sha256')==hashlib.sha256(task_raw).hexdigest()
  checks['finite_execution']=f.get('execution') is True and f.get('passed_execution') is True and f.get('error') is None
  checks['original_finite_scope']=f.get('num_envs')==80 and f.get('seed')==20260928 and f.get('controls')==1000 and f.get('seconds')==20. and f.get('physics_callbacks')==8000 and f.get('feedback_samples')==2000 and f.get('delay_calls')==dict(legs=8000,wheels=8000)
  checks['ready_zero_precontrols']=ready.get('worker_pid')==pid and ready.get('role')=='E0' and ready.get('group_id')==plan['group_id'] and ready.get('GPU_UUID')==plan['GPU_UUID'] and ready.get('zero_controls_before_barrier') is True and ready.get('precontrols')==ready.get('actor_calls')==0 and ready.get('explicit_fresh_resets')==1 and started.get('zero_precontrols') is True and started.get('group_id')==plan['group_id']
  cache=f.get('source_cache') or {};checks['whole_candidate_once_CPU']=all(cache.get(k)==1 for k in ('physical_byte_opens','SHA_calculations','decodes')) and cache.get('all_original_root_and_nested_cached') is True and cache.get('wholecachedidentity_passed') is True and cache.get('live_actor_STD_strict') is True
  checks['actual_new_candidate_metadata']=cache.get('source_path')==expect['checkpoint_path'] and cache.get('source_SHA')==expect['checkpoint_SHA'] and cache.get('source_iteration')==expect['checkpoint_iteration'] and cache.get('source_Adam17')==expect['checkpoint_Adam_step'] and cache.get('source_LR')==expect['checkpoint_LR']
  checks['no_optimizer_or_saved20k_application']=f.get('optimizer_updates')==0 and f.get('live_critic_optimizer_created') is False and f.get('source_saved20k_DR_history_applied') is False and f.get('source20k_DR_sliced') is False and f.get('whole_saved20k_resume') is False and cache.get('live_critic_optimizer_created') is False and cache.get('source20k_DR_history_applied') is False and cache.get('source20k_state_sliced') is False
  checks['fresh_N80_D0_D7_before_after']=all(isinstance(f.get(k),dict) and f[k].get('fresh_N80_D0_D7_enabled') is True and f[k].get('one_explicit_fresh_reset')==1 and f[k].get('saved20k_history_physically_applied') is False and f[k].get('new_constructor_nominals_preserved') is True and (f[k].get('actual_parameters') or {}).get('actual_parameters_pass') is True for k in ('fresh_fullDR_before','fresh_fullDR_after'))
  actor=f.get('actor') or {};checks['strict_frozen_original_actor']=actor.get('strict_actor_and_embedded_learned_normalizer') is True and actor.get('no_live_critic_or_optimizer') is True and actor.get('normalization_updated') is False and actor.get('mean_only') is True and f.get('original_RSL_clip_actions')==6.
  binding=f.get('actual_V2_binding') or {};checks['actual_V2_asset_binding']=binding.get('asset_sha256')==expect['asset_SHA'] and binding.get('contract_sha256')==expect['contract_SHA'] and ready.get('actual_V2_binding')==binding
  native=f.get('actual_native_static') or {};rows=native.get('actual_native_mechanical_limits');checks['actual_fresh_N80_native_readback']=isinstance(rows,list) and bool(rows) and all(x.get('actual_all_N80_verified') is True for x in rows) and native.get('no_precontrol') is True and native.get('not_N20000_native_admission_replay') is True and ready.get('actual_native_static')==native
  scut=f.get('actual_SCUT_binding') or {};scut_after=f.get('actual_SCUT_binding_after') or {};candidate=f.get('candidate_SCUT_cache_binding') or {};source=f.get('migration_worker_source') or {}
  checks['explicit_actual_SCUT_hour_worker']=task['migration_worker']==expect['migration_worker']==source.get('path') and source.get('SHA')==expect['migration_worker_SHA']
  checks['qualified_SCUT_hour_U000_exact7_gate']=task['training_window_mode']==scut.get('mode')==scut_after.get('mode')=='SCUT_V14_ORIGINAL_FINITE_WALL_CLOCK_HOUR' and task['migration_cohort_close_receipt'].get('U000_exact7') is True and task['migration_cohort_close_receipt'].get('training_window_mode')==task['training_window_mode']
  checks['actual_SCUT_cmd_done_reward_binding']=ready.get('actual_SCUT_binding')==scut and all(x.get('task')=='Robotics-Wheelbipe-V14-Flat-v0' and x.get('command_done_bound') is True and x.get('reward_configured') is True and x.get('reward_bound') is True and x.get('real_candidate_iteration')==expect['checkpoint_iteration'] and x.get('cached_sensor_read_only') is True and x.get('no_extra_reset_observation_RNG_or_precontrol') is True and x.get('reward_and_cached_sensor_algorithms_unmodified') is True for x in (scut,scut_after)) and scut.get('controls')==0 and scut_after.get('controls')==scut_after.get('reward_last_step')==1000 and scut.get('active_reward_weights')==scut_after.get('active_reward_weights')
  checks['SCUT_candidate_whole_CPU_provenance']=ready.get('candidate_SCUT_cache_binding')==candidate and candidate.get('mode')==expect['training_window_mode'] and candidate.get('same_FINAL_live_core') is True and candidate.get('U000_exact7') is True and candidate.get('actual_new_updates')==expect['candidate_actual_updates'] and candidate.get('physical_history_applied') is False
  checks['original_actor_config_only_binding']=all((x.get('actor_config_binding') or {}).get('original_actor_configuration_function_unmodified') is True and (x.get('actor_config_binding') or {}).get('no_PPO_implementation_or_live_critic_optimizer') is True and (x.get('actor_config_binding') or {}).get('candidate_LR')==expect['checkpoint_LR'] for x in (scut,scut_after))
  checks['original_env_close_returned']=pre.get('calling_original_env_close') is True and pre.get('completed_controls')==1000 and envclose.get('original_env_close_returned') is True and intent.get('env_close_returned') is True
  checks['durable_V6_intent_final_binding']=intent.get('final_sha256')==hashlib.sha256(raw).hexdigest() and intent.get('final_bytes')==len(raw) and intent.get('error_before_close') is False and intent.get('original_app_close_arguments')==[] and intent.get('original_fast_shutdown_unchanged') is True and (intent.get('original_bound_close') or {}).get('fast_shutdown') is True and intent.get('expected_process_nonreturn') is True and intent.get('app_close_returned') is None and intent.get('publication')=='TEMP_FLUSH_FSYNC_ATOMIC_RENAME_DIRECTORY_FSYNC_BEFORE_ORIGINAL_APP_CLOSE' and intent.get('epoch',0)>=f.get('last_eval_epoch',float('inf'))
  skill=f.get('skill') or {};checks['missing_E0_grader_remains_null']=skill.get('full_grader','ABSENT') is None and bool(skill.get('predicate_gap')) and f.get('full_skill_graduation','ABSENT') is None and skill.get('full_skill_graduation','ABSENT') is None
  checks['no_registry_or_mother_mutation']=f.get('registry_writes')==0 and f.get('mother_replaced') is False
 except BaseException:detail['original_qualification_error']=traceback.format_exc();checks['all_required_json_and_fields_present']=False
 errors=sorted(p.name for p in out.glob('*ERROR*.json'));checks['own_worker_ERROR_absent']=not errors;detail['own_error_files']=errors
 return dict(kind='SCUT_E0_HOUR_FROZEN_ACTUAL_WAIT_EXECUTION_QUALIFICATION_V1',role='E0',qualified=bool(checks) and all(checks.values()),checks=checks,actual_child_wait_returned=True,actual_child_pid=pid,actual_parent_pid=os.getpid(),actual_returncode=rc,qualification_scope='FINITE_EXECUTION_ONLY_NOT_SKILL_GRADUATION',skill_grader=None,full_skill_graduation=None,detail=detail)

def settle_own_card(uuid,waited,admitted):
 rows=[]
 if not waited or not admitted:return False,rows
 until=time.monotonic()+120
 while True:
  try:
   resource=nvidia(uuid);apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);empty=uuid not in apps;ok=empty and resource['free_MiB']>=23500 and resource['utilization_percent']==0;rows.append(dict(epoch=time.time(),resource=resource,selected_card_compute_empty=empty,settled=ok))
   if ok:return True,rows
  except BaseException:rows.append(dict(epoch=time.time(),original_error=traceback.format_exc(),settled=False))
  if time.monotonic()>=until:return False,rows
  time.sleep(2)

def main():
 assert B.is_relative_to(OWN/'tasks')and not(B/'PARENT_STARTED.json').exists();plan=json.loads((B/'GROUP_PLAN.json').read_bytes());uuid=plan['GPU_UUID'];roles=plan['roles'];assert len(roles)==1 and [r['role']for r in roles]==['E0'] and plan['migration_close']['roles']==['E0'];put('PARENT_STARTED.json',dict(pid=os.getpid(),creation=psutil.Process().create_time(),epoch=time.time(),kind='ONEGPU_SINGLE_E0_FRESH80_FINITE_EVAL_NO_LEARNING',GPU_UUID=uuid));locks=[];children=[];errors=[];group_start=None;started=time.time();terminal=[]
 try:
  for r in plan['worker_files']:
   p=B/r['relative'];raw=p.read_bytes();assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA']
  class BusyResource(Exception):pass
  wait_until=time.monotonic()+1800;wait_rows=[]
  while True:
   candidate=None
   try:
    for path in(OWN/'state'/('three_expert_v2_'+uuid+'.lock'),OWN/'state/finite_environment_validation.lock'):
     candidate=path.open('rb+');fcntl.flock(candidate,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(candidate);candidate=None
    canonical=OWN/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json';raw=canonical.read_bytes();c=json.loads(raw);assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['remaining_training_seconds']>c['finite_minimum_remaining_seconds']
    if c['active_segment']is not None:raise BusyResource('Originalcanonicalhasactiveowner;nointerference')
    apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
    if uuid in apps:raise BusyResource('Selectedcardhasexistingcomputeprocess')
    res=nvidia(uuid)
    if res['free_MiB']<23500 or res['utilization_percent']!=0:raise BusyResource('Selectedcardnotemptyatfreshadmission')
    assert psutil.virtual_memory().available>96*1024**3 and shutil.disk_usage(B).free>25*1024**3
    break
   except (BlockingIOError,BusyResource)as busy:
    if candidate is not None:candidate.close()
    for fd in reversed(locks):fcntl.flock(fd,fcntl.LOCK_UN);fd.close()
    locks.clear();wait_rows.append(dict(epoch=time.time(),reason=str(busy),locks_held=0,SDK_or_selected_model_opened=False,canonical_writes=0,remaining_wait_seconds=max(0,wait_until-time.monotonic())));put('BOUNDED_ORIGINAL_RESOURCE_WAIT.json',wait_rows)
    if time.monotonic()>=wait_until:raise TimeoutError('Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions')
    time.sleep(15)
  put('ACTUAL_GROUP_ADMISSION.json',dict(epoch=time.time(),group_id=plan['group_id'],resource=res,selected_card_compute_processes=[],original_private_GPU_EX_held=True,original_global_finite_EX_held=True,canonical_SHA_at_read=hashlib.sha256(raw).hexdigest(),canonical_original_generation=c['authority_generation'],canonical_remaining_snapshot=c['remaining_training_seconds'],canonical_minimum=c['finite_minimum_remaining_seconds'],canonical_owner_at_read=None,canonical_writes=0,canonical_bytes_copied=False,no_PPO_BPTT_GO=True));del raw,c
  deadline=time.time()+2400
  for r in roles:
   out=B/'cases'/r['role'];out.mkdir(parents=True,exist_ok=True);task=make_task(r,plan,deadline,[f.fileno()for f in locks]);(out/'task.json').write_text(json.dumps(task,indent=2));env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2')
   for key in('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(key,None)
   for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp','TORCH_HOME':'cache/torch'}.items():
    p=out/'private'/rel;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
   log=(out/'SDK_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/r['worker']),'--task',str(out/'task.json'),'--group-root',str(B)],cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=tuple(f.fileno()for f in locks),start_new_session=True);log.close();children.append((r,out,p,psutil.Process(p.pid).create_time()));put('CHILDREN.json',[dict(role=r['role'],pid=p.pid,creation=creation,GPU_UUID=uuid,root=str(out),worker=r['worker'])for r,out,p,creation in children])
  assert len(children)==1;ready_until=time.time()+900;memory=[]
  while time.time()<ready_until:
   ready=[r['role']for r,out,p,creation in children if(out/'WORKER_SCENE_READY.json').exists()];failed=[r['role']for r,out,p,creation in children if(out/'WORKER_ERROR.json').exists()or(p.poll()is not None and r['role']not in ready)];put('GROUP_BARRIER_STATUS.json',dict(epoch=time.time(),ready=ready,failed=failed,members=[r['role']for r in roles]))
   if failed:raise RuntimeError('Someownmemberfailedbeforecommonstart:'+str(failed))
   if ready==['E0']:
    group_start=time.time();put('GROUP_EVAL_START.json',dict(group_id=plan['group_id'],GPU_UUID=uuid,members=ready,all_members_ready=True,epoch=group_start,source='SingleE0SDKscene+liveactor+N80fullDRreadybeforeanycontrolledstep'));break
   if not memory or time.time()-memory[-1]['epoch']>=30:memory.append(dict(epoch=time.time(),**nvidia(uuid)));put('GROUP_GPU_MEMORY_SAMPLES.json',memory)
   time.sleep(2)
  if group_start is None:raise TimeoutError('SingleE0SDKstartupreadybarrier900s expired')
  while time.time()<deadline and any(p.poll()is None for r,out,p,creation in children):
   if not memory or time.time()-memory[-1]['epoch']>=30:memory.append(dict(epoch=time.time(),**nvidia(uuid)));put('GROUP_GPU_MEMORY_SAMPLES.json',memory)
   time.sleep(2)
  for r,out,p,creation in children:
   if p.poll()is None:raise TimeoutError('Owngroup2400s boundedworkerend:'+r['role'])
   rc=p.wait();data=json.loads((out/'V2_FROZEN_EVAL_FINAL.json').read_bytes())if(out/'V2_FROZEN_EVAL_FINAL.json').exists()else None;q=qualify_waited_e0(out,p.pid,rc,plan);err={ep.name:json.loads(ep.read_bytes())for ep in out.glob('*ERROR*.json')};terminal.append(dict(role=r['role'],pid=p.pid,GPU_UUID=uuid,returncode=rc,actual_waited=True,ready=(out/'WORKER_SCENE_READY.json').exists(),started=(out/'WORKER_EVAL_STARTED.json').exists(),pre_close=(out/'PRE_CLOSE.json').exists(),passed_execution=q['qualified'],semantic_qualification=q,data=data,error=err));put('TERMINAL_ROWS.json',terminal)
  put('SCUT_E0_HOUR_FROZEN_PARENT_FINAL.json',dict(kind='ACTUAL_SINGLE_GPU_E0_FRESH80_FROZEN_FINITE_EVAL',group_id=plan['group_id'],GPU_UUID=uuid,common_start_epoch=group_start,single_E0_ready_before_start=True,skill_grader=None,full_skill_graduation=None,all_E0_actual_execution_complete=all(v['passed_execution']for v in terminal),rows=terminal,source20k_DR_history_sliced=False,source20k_histories_physically_applied=False,old20k_fullrestore_proof_preserved_separately=True,new_PPO_BPTT_GO=0,canonical_writes=0,epoch=time.time()))
 except BaseException:
  errors.append(traceback.format_exc());put('GROUP_ABORT.json',dict(epoch=time.time(),errors=errors,ownscope_only=True));put('GROUP_STARTUP_ABORT.json',dict(epoch=time.time(),errors=errors,ownscope_only=True));put('PARENT_ORIGINAL_ERROR.json',dict(errors=errors,no_samepurpose_automatic_retry=True))
 finally:
  waits=[]
  for r,out,p,creation in children:
   if p.poll()is None:
    try:
     q=psutil.Process(p.pid);assert abs(q.create_time()-creation)<.02 and str(B)in' '.join(q.cmdline());os.killpg(p.pid,signal.SIGTERM)
    except psutil.NoSuchProcess:pass
    try:p.wait(timeout=25)
    except subprocess.TimeoutExpired:
     q=psutil.Process(p.pid);assert abs(q.create_time()-creation)<.02 and str(B)in' '.join(q.cmdline());os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=25)
   waits.append(dict(role=r['role'],pid=p.pid,returncode=p.wait(),actual_waited=True))
  waited=len(waits)==len(children)and all(v['actual_waited']for v in waits)
  settled,settle_rows=settle_own_card(uuid,waited,(B/'ACTUAL_GROUP_ADMISSION.json').exists())
  if waited:
   for fd in reversed(locks):fcntl.flock(fd,fcntl.LOCK_UN)
  for fd in locks:fd.close()
  put('PARENT_EXIT_SCOPE.json',dict(epoch=time.time(),all_own_children_waited=waited,child_waits=waits,original_single_GPU_private_EX_released=waited,original_global_finite_EX_released=waited,GPU_settled=settled,GPU_settle_rows=settle_rows,errors=errors,no_foreign_scope_touched=True,canonical_writes=0,SDK_PT_opens_by_parent=0,wall_seconds=time.time()-started))
if __name__=='__main__':main()
