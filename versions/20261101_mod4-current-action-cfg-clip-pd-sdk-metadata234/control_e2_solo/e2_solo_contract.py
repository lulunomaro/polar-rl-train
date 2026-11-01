"""Next E2-only original-owner SOURCE contract. JSON/source metadata only."""
from pathlib import Path
import hashlib,json

KIND='MOD4_E2_QUALIFIED_B3AE_SOLO_FULLSTATE_SOURCE_READY_V1'
WORKER_KIND='MOD4_E2_B3AE_ORIGINAL_WORLD_MIX_FULL_PPO_CONTINUE_V1'
ROLE='e2'  # Exact existing correct sender whitelist key;not e2_72.
SHA='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
BYTES=14615089
ITER=42822
ADAM=859300
LR=.00022500000000000002
CPU_SHA='d741414f54c22bff910541560e3af689f0c36afa507fb416e7beb7dd632468bb'
MODEL='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_PPO50_GAS400_2610v93/e2/adaptation/final_valid_update92.pt'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
MANIFEST_SHA='ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f'
GPUS={'GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}


def require(value,reason):
 if not value:raise ValueError(reason)
def ready_SHA(value):return hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest()
def metadata(path):
 p=Path(path);require(p.suffix=='.json' and not p.name.endswith(('.partial','.active')),'Complete saved JSON only')
 b=p.read_bytes();return json.loads(b),dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())


def qualified_cpu(value,sha):
 require(sha==CPU_SHA and value['passed'] is True,'Original qualified E2 wholeCPU report')
 require(value['model']['SHA']==SHA and value['model']['bytes']==BYTES,'Qualified b3ae only')
 require(value['stored_iteration']==ITER and value['Adam_step']==ADAM and value['adaptive_LR']==LR,'Original fullstate counters/LR')
 for k in ('whole_model_all_tensors_finite','all_critical_D1_D7_and_E2_command_CPU_validated','actor9_critic8_STD6_original35_38','all17_Adam_and_original_nonLR_optimizer_settings'):
  require(value[k] is True,'Whole source proof: '+k)
 require(len(value['fingerprints'])==175 and value['new_branch_skill_qualified'] is False,'175 saved fingerprints,not graduation')


def scoped232(value):
 require(value['kind']=='ROOT232_SCOPED_E2_FULLRESTORE_NATIVE24_ACTUAL_PROJECTION','ROOT selected232 proof,not outer false relabel')
 require(value['source_SHA']==SHA and value['num_envs']==20000,'Actual232 same E2 source/profile')
 require(value['original232_parent_passed_execution'] is False and value['missing_post_Appclose_readcounts_preserved'] is True,'Original232 readerfalse remainsfalse')
 require(value['fullrestore_passed'] is True and value['core_fingerprints_matched']==68 and value['Adam17']==ADAM and value['iteration']==ITER and value['LR']==LR,'Actual scoped core restore')
 require(value['source_has_E2_command_state'] is True and value['original_D0_D7_then_one_new_episode'] is True,'Saved E2 command/RNG and original restore chain')
 require(value['native24_passed'] is True and (value['controls'],value['physics'],value['feedback'])==(24,192,48),'Original actual20k native24')
 require(value['original_worker_wait_RC']==0 and value['all_own_children_waited'] and value['private_EX_released'],'Actual original232 close/wait')
 require(value['original_report_ref']['path'] and len(value['original_report_ref']['SHA'])==64,'Saved original232 source receipt reference')


def fresh(value):
 require(value['kind']=='ROOT_E2_SOLO_FRESH_CNONE_CIM_RESOURCE_ACTUAL','New ROOT sole-E2 admission')
 require(value['passed'] is True and value['fresh_current_CNone'] is True and value['canonical_active'] is None,'Actual freshCNone only,no active owner hotadd')
 require(value['generation']==GENERATION and value['total_authorized_seconds']==2268000,'Original canonical generation/total')
 for k in ('fresh_LOCAL_exact_CIM_passed','original_private_EX_probe_free','original_shared_locks_probe_free','no_new_writer_grant_copy_refund_or_hotadd'):
  require(value[k] is True,'Actual new ROOT condition: '+k)
 require(value['GPU_UUID'] in GPUS and value['GPU_name']=='NVIDIA GeForce RTX 4090','Original target72 GPU')
 require(value['GPU_free_MiB']>15669 and value['GPU_util_percent']<=30 and value['RAM_available_bytes']>32*1024**3 and value['disk_free_bytes']>25*1024**3,'Original light limits;nonempty compute allowed')
 require(value['control_snapshot_id'] and value['actual_report_refs'] and value['checked_epoch']>0,'Actual current source references')


def task_base():
 return dict(kind=WORKER_KIND,source_qualification_kind=KIND,role_key=ROLE,source_SHA=SHA,source_bytes=BYTES,
  source_iteration=ITER,source_Adam_step=ADAM,source_LR=LR,model_path=MODEL,num_envs=20000,
  actor_obs=35,critic_obs=38,action_dim=6,preserve_learned_STD=True,nominal_gas_N_each=400,
  physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,original_canonical_generation=GENERATION,
  domain_kind='E2_WORLD_MOVING_SIGNED4',sampler_stage='world_directional_v1',world_progress_goal=.5,
  preserve_original_reward_commands_sampler_and_D0_D7=True,source_command_state_and_named_global_RNG_restore_then_new_episode=True,
  max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,
  source_saved_fullstate_CPU_SHA=CPU_SHA,source_read_purpose=dict(physical_byte_opens=1,decodes=1,source_bytes=BYTES))


def validate_task(task):
 for k,v in task_base().items():require(task[k]==v,'Typed E2 identity: '+k)
 require(task['GPU_UUID'] in GPUS and task['worker_SHA'] and task['run_id'],'Actual new selected role/run')
 require('source_CPU_SHA' not in task,'No cyclic wholeReady hash in Task')
 return True


def valid_ready_value(value,spec):
 return bool(value.get('passed') is True and value.get('kind')==KIND and value.get('source_SHA')==SHA and
  value.get('source_iteration')==ITER and value.get('Adam_step')==ADAM and value.get('source_LR')==LR and
  value.get('source_saved_fullstate_CPU_SHA')==CPU_SHA and value.get('source_fullstate_CPU_passed') is True and
  value.get('original232_scoped_fullrestore_native24_reused') is True and value.get('original232_outer_false_preserved') is True and
  value.get('all_actor_critic_optimizer_tensors_finite') is True and value.get('actual_35_38_6_shapes') is True and
  value.get('fresh_CNone_CIM_resources_passed') is True and value.get('manifest_SHA')==spec['manifest_SHA'] and
  value.get('launch_evidence_SHA')==spec['launch_evidence_SHA'])


def validate_job(job,task,go):
 validate_task(task);job=Path(job)
 evidence,er=metadata(job/'PRELAUNCH_E2_SOLO_ACTUAL_EVIDENCE.json')
 require(er['SHA']==task['launch_evidence_SHA']==go['launch_evidence_SHA'],'Actual admission evidence binding')
 fresh(evidence['fresh_actual']);scoped232(evidence['actual232_scoped'])
 require(evidence['saved_CPU_ref']['SHA']==CPU_SHA,'Actual qualified CPU metadata reference')
 ready,_=metadata(job/'ADMISSION_E2_SOLO_READY.json');manifest,mr=metadata(job/task['manifest_file'])
 require(valid_ready_value(ready,dict(manifest_SHA=mr['SHA'],launch_evidence_SHA=er['SHA'])),'Ready/manifest/source join')
 require(go['source_CPU_SHA']==ready_SHA(ready) and go['manifest_SHA']==mr['SHA'] and go['source_qualification_kind']==KIND,'Original owner-issued wholeReady SHA')
 require(go['role_key']==ROLE and go['source_model_SHA']==SHA and go['source_iteration']==ITER and go['input_Adam']==ADAM,'Exact original sender E2 role/source')
 require(go['one_original_writer'] and go['genuine_original_E2_WORLD_MOVING_SIGNED4'],'Original one-role E2 GO')
 require(go['prelaunch_control_snapshot_id']==evidence['fresh_actual']['control_snapshot_id'],'Actual fresh root snapshot')
 require(manifest['input_model_metadata']['SHA']==SHA and all(not r['relative'].endswith(('.pt','.partial','.active')) for r in manifest['files']),'Source PT metadata only,complete source files')

