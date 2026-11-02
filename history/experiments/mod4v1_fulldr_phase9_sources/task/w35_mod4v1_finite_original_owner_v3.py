"""NEW finite MOD4v1 W35 parent using original canonical/locks/accounting functions.
One existing authority generation. No new ledger, budget, refund or concurrent writer.
"""
from pathlib import Path
import json,os,time,hashlib,fcntl,subprocess,traceback,shutil
import three_slot_common_v1 as b
from single_writer72_authority_V85M_source import authority_tracking_schema_admitted,authority_original_extension_count,authority_budget_GO_allowed
B=Path(__file__).resolve().parent;put=b.put;KEY='w35_72';GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842';USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3';CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
KIND='MOD4V1_W35_RESUME32561_FULLD0D7_RM70_V3';SOURCE='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f';MODEL='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FULLDR_ADAPT_V2_20261102_021542_1793556942487949000/production/model_final_complete.pt';GPU_RESTORE='2eaf652c3ce0e54db7057cb1bddb3fcfaa446ff047592a6c6f813fe0dd3d89e8'

def account(go,rows,end=False):
 c=b.read(b.C);a=c['active_segment'];assert a and a['owner_parent_pid']==os.getpid();c,a=b.charge_values(c,a,{KEY:go},rows,time.time());c['active_segment']=a
 if end:
  assert b.terminal(rows[KEY]);a['ended_epoch']=time.time();a['actual_terminal_rows']=rows;c['completed_segments'].append(a);c['active_segment']=None
 put(b.C,c);return c

def main():
 assert not(B/'OWNER_STARTED.json').exists();cfg=b.read(B/'OWNER_PLAN.json');run=cfg['run_id'];locks=[];private=shared=None;p=None;active=False;go=None;rows={};error=None;rc=None
 put(B/'OWNER_STARTED.json',{'epoch':time.time(),'pid':os.getpid(),'run_id':run,'no_new_budget_or_canonical':True})
 try:
  manifest=b.read(B/'INSTALL_MOD4V1_ACTUAL.json')
  for row in manifest['files']:
   f=B/row['relative'];assert f.resolve().is_relative_to(B) and f.stat().st_size==row['bytes'] and b.H(f)==row['SHA']
  native=b.read(B/'evidence/NEW_ASSET_NATIVE_ACTUAL.json');sdk=b.read(B/'evidence/NEW_TARGET_SDK_FULL32_ACTUAL.json');history=b.read(B/'evidence/RM70_SCOPE_REUSE_ACTUAL.json')
  assert native['passed'] and sdk['passed_execution'] and sdk['bounded32s_complete'] and not sdk['errors'] and sdk['returncode']==0
  restored=sdk['rows']['MOD4V1_FULLRESTORE_GUARD_ACTUAL.json'];assert restored['usd_sha256']==USD and restored['contract_sha256']==CONTRACT and restored['num_envs']==20000 and restored['new_constructor_nominal_caches_preserved'] and restored['original_fresh_reset_calls']==1 and restored['observation_shapes_checked']
  assert history['actual_original_geometry_fullSHA_verified'] and history['actual_shared_material_source_reused_unchanged']
  restore=b.read(B/'evidence/INPUT89ACA_GPU_FULLRESTORE_ACTUAL.json');assert b.H(B/'evidence/INPUT89ACA_GPU_FULLRESTORE_ACTUAL.json')==GPU_RESTORE and restore['passed'] and restore['source_SHA']==SOURCE and restore['iteration']==32561 and restore['Adam17']==652860 and restore['actual_LR']==.00011390625000000006 and restore['actor_critic_STD_optimizer_verified']
  decision=b.read(B/'evidence/ACTUAL_POST80_FULL32_DECISION.json');trace=b.read(B/'evidence/ACTUAL_POST80_TRACE_SIGNED.json');closed=b.read(B/'evidence/ACTUAL_POST80_TRACE_EXIT.json')
  assert decision['after_model_SHA']==SOURCE and decision['new_PPO_updates']==80 and decision['decision']['RM70_full_expert_qualification']is False and trace['no_qualification'] and closed['all_own_children_waited'] and closed['owned_private_validation_locks_released'] and closed['error']is None
  for path in b.LOCKS:
   f=path.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  c=b.read(b.C);assert c['active_segment'] is None and authority_tracking_schema_admitted(c) and authority_original_extension_count(c)==9 and authority_budget_GO_allowed(c) and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'
  assert c['remaining_training_seconds']>86412.86069250107+3900
  private=(b.C.parent.parent/('three_expert_v2_'+GPU+'.lock')).open('rb+');fcntl.flock(private,fcntl.LOCK_EX|fcntl.LOCK_NB)
  shared=(b.C.parent.parent/'finite_environment_validation.lock').open('rb+');fcntl.flock(shared,fcntl.LOCK_SH|fcntl.LOCK_NB)
  import psutil
  line=subprocess.check_output(['/usr/bin/nvidia-smi','-i',GPU,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[v.strip() for v in line.split(',')]
  apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
  assert a[0]==GPU and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30 and GPU not in apps and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(B).free>25*1024**3
  put(B/'ACTUAL_CANONICAL_READ.json',{'epoch':time.time(),'path':str(b.C),'SHA':b.H(b.C),'generation':c['authority_generation'],'remaining_seconds':c['remaining_training_seconds'],'charged_seconds':c['charged_training_seconds'],'active_segment':None,'original_two_EX_held':True,'owner_pid':os.getpid(),'run_id':run,'strict_reserve_seconds':86412.86069250107})
  put(B/'ACTUAL_RESOURCE_LEASES.json',{'epoch':time.time(),'GPU_UUID':GPU,'GPU_line':line,'GPU_compute_empty':True,'private_EX_held':True,'original_finite_env_SH_held':True,'RAM_available':psutil.virtual_memory().available,'disk_free':shutil.disk_usage(B).free,'owner_pid':os.getpid()})
  admission={'kind':'ROOT_MOD4V1_W35_ACTUAL_ADMISSION_V1','run_id':run,'role_key':KEY,'GPU_UUID':GPU,'asset_USD_SHA':USD,'asset_contract_SHA':CONTRACT,'new_asset_native0PT_passed':True,'actual_target_source_and_SDK_admitted':True,'actual_private_GPU_EX_held_by_original_parent':True,'actual_original_shared_finite_env_SH_held':True,'actual_fresh_GPU_and_host_resources_admitted':True,'historical_RM70_geometry_and_shared_material_proofs_exactly_reused':True,'actual_current_canonical_owner_and_budget_admission_passed':True,'canonical_binding':{'path':str(b.C),'generation':c['authority_generation'],'owner_run_id':run,'one_original_writer':True},'actual_canonical_read_receipt_SHA':b.H(B/'ACTUAL_CANONICAL_READ.json'),'actual_lock_and_resource_receipt_SHA':b.H(B/'ACTUAL_RESOURCE_LEASES.json'),'new_asset_native0PT_receipt_SHA':b.H(B/'evidence/NEW_ASSET_NATIVE_ACTUAL.json'),'target_source_SDK_receipt_SHA':b.H(B/'evidence/NEW_TARGET_SDK_FULL32_ACTUAL.json'),'historical_RM70_scope_reuse_receipt_SHA':b.H(B/'evidence/RM70_SCOPE_REUSE_ACTUAL.json')}
  put(B/'ROOT_ADMISSION_ACTUAL.json',admission);admit_sha=b.H(B/'ROOT_ADMISSION_ACTUAL.json');mh=b.H(B/'INSTALL_MOD4V1_ACTUAL.json')
  ready={'passed':True,'kind':KIND,'source_SHA':SOURCE,'source_iteration':32561,'Adam_step':652860,'source_LR':.00011390625000000006,'source_GPU_fullrestore_proof_SHA':GPU_RESTORE,'asset_USD_SHA':USD,'asset_contract_SHA':CONTRACT,'root_admission_SHA':admit_sha,'manifest_SHA':mh,'evidence_scope':'Actual target20k source fullrestore/native24/full32 execution, actual89aca GPUfullrestore proof, not oldCPUproof, newprivate/finite/canonical owner admission; not skill graduation'}
  put(B/'READY_MOD4V1_ACTUAL.json',ready)
  task={'kind':KIND,'run_id':run,'role_key':KEY,'num_envs':20000,'source_SHA':SOURCE,'source_bytes':17621509,'source_iteration':32561,'source_Adam_step':652860,'source_LR':.00011390625000000006,'source_prior_new_PPO_updates':80,'model_path':MODEL,'source_GPU_fullrestore_proof_SHA':GPU_RESTORE,'asset_USD_SHA':USD,'asset_contract_SHA':CONTRACT,'closure_episode_m':.01,'mimic_rad':.01,'original_canonical_generation':c['authority_generation'],'canonical_path':str(b.C),'source_read_purpose':{'physical_byte_opens':1,'decodes':1,'source_bytes':17621509},'GPU_UUID':GPU,'asset_dir':str(B/'runtime/assets'),'worker_SHA':b.H(B/'worker_mod4v1_w35.py'),'manifest_file':'INSTALL_MOD4V1_ACTUAL.json','ready_file':'READY_MOD4V1_ACTUAL.json','root_admission_file':'ROOT_ADMISSION_ACTUAL.json','root_admission_SHA':admit_sha,'derivation_index_SHA':b.H(B/'MOD4V1_DERIVATION_INDEX.json'),'max_parent_seconds':3900,'save_after_seconds':3600,'exit_headroom_seconds':300}
  put(B/'TASK.json',task);now=time.time();go={'run_id':run,'role_key':KEY,'GPU_UUID':GPU,'one_original_writer':True,'source_model_SHA':SOURCE,'source_iteration':32561,'input_Adam':652860,'source_qualification_kind':KIND,'num_envs':20000,'actor_obs':35,'critic_obs':38,'action_dim':6,'physics_dt':.0025,'TGS':[32,4],'policy_hz':50,'feedback_hz':100,'asset_USD_SHA':USD,'asset_contract_SHA':CONTRACT,'manifest_SHA':mh,'root_admission_SHA':admit_sha,'source_CPU_SHA':hashlib.sha256(json.dumps(ready,indent=2).encode()).hexdigest(),'learning_started_epoch':now,'max_parent_seconds':3900,'save_deadline':now+3600,'nominal_end_epoch':now+3900,'exit_headroom_seconds':300,'original_owner_pid':os.getpid()}
  # Begin the same original segment only under both original exclusive owner locks.
  c=b.read(b.C);assert c['active_segment'] is None;c['active_segment']={'pid':os.getpid(),'owner_parent_pid':os.getpid(),'kind':'Linux_MOD4V1_W35_FULLDR_RM70_'+run,'started_epoch':now,'accounted_through_epoch':now,'charged_expert_seconds':0.,'experts':{},'charge_contract':'Original charge_values; actual load learn save SDKclose childwait terminal, no refund/clamp or uncharged PPO tail'};put(b.C,c);active=True;put(B/'GO_PRODUCTION.json',go)
  env=dict(os.environ,CUDA_VISIBLE_DEVICES=GPU,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  for name in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(name,None)
  for name,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
   d=B/'private_train'/rel;d.mkdir(parents=True,exist_ok=True);env[name]=str(d)
  log=(B/'PPO_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'worker_mod4v1_w35.py'),'--mode','train','--num-envs','20000','--run-id',run,'--out',str(B/'production')],cwd=B,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=tuple(f.fileno() for f in locks)+(private.fileno(),shared.fileno()),start_new_session=True);log.close();put(B/'WORKER_IDENTITY_BEFORE_WAIT.json',b.ident(p.pid))
  while p.poll() is None:
   c=account(go,rows);put(B/'OWNER_CURRENT.json',{'epoch':time.time(),'run_id':run,'worker':b.ident(p.pid),'source_SHA':SOURCE,'canonical_remaining_seconds':c['remaining_training_seconds'],'go':go,'one_original_writer':True})
   if time.time()>=go['save_deadline'] or c['remaining_training_seconds']<=86412.86069250107:
    (B/'production').mkdir(exist_ok=True);put(B/'production/STOP_AFTER_SAVE.json',{'epoch':time.time(),'reason':'Original finite save deadline/reserve, complete own save and exit'})
   time.sleep(3)
  rc=p.wait();final=b.read(B/'production/FINAL.json');rows={KEY:{'key':KEY,'phase':'terminal','terminal_all_own_children_waited':True,'returncode':rc,'owner_received_terminal_epoch':time.time(),'final':final,'original_error':bool(rc!=0),'manifest_SHA':mh}};account(go,rows,True);active=False
  put(B/'COHORT_FINAL.json',{'run_id':run,'rows':rows,'go':{KEY:go},'original_cost_settled':True,'passed_execution':bool(rc==0 and final and final.get('passed')),'next_action':'Immediate actual-model replay and independent full32 sameUID evaluation; do not claim skill graduation from savedformat'})
 except BaseException:
  error=traceback.format_exc();put(B/'OWNER_ORIGINAL_ERROR.json',{'error':error,'active_not_falsely_cleared':active})
  if p is not None and p.poll() is None:
   (B/'production').mkdir(exist_ok=True);put(B/'production/STOP_AFTER_SAVE.json',{'epoch':time.time(),'reason':'Original owner exception, own complete save/exit only'})
   while p.poll() is None:
    if active:account(go,rows)
    time.sleep(3)
  if active:
   rc=p.wait() if p is not None else 1;rows={KEY:{'key':KEY,'phase':'terminal','terminal_all_own_children_waited':True,'returncode':rc,'owner_received_terminal_epoch':time.time(),'original_error':True}};account(go,rows,True);active=False
 finally:
  waited=p is None or p.poll() is not None
  if waited:
   for f in (shared,private):
    if f is not None:fcntl.flock(f,fcntl.LOCK_UN);f.close()
   for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',{'epoch':time.time(),'original_cost_settled':not active,'all_own_children_waited':waited,'own_original_two_fcntl_released_if_held':waited,'private_finite_leases_released':waited,'error':error,'no_automatic_extra_window':True})
if __name__=='__main__':main()
