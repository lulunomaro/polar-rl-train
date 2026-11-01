"""Latest qualified W35 and model-free authority contract. No PT/SDK imports."""
from pathlib import Path
import hashlib,json
SHA='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b'
BYTES=17619333;ITER=32481;ADAM=651260;UPDATES=77;LR=.0002562890625000001
CPU_SHA='e55cad0a6d1e70b99ed8b527a8d50241c4b30c59f4cdf449842889d2ee84e5fb'
SOURCE_JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_QUALIFIED343E_CONTINUE227D_20261101_0712/w35_72'
SOURCE_MODEL=SOURCE_JOB+'/production/model_final_complete.pt'
CANONICAL='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
KIND='W35_LATEST32481_32S_SAMEUID_RM70_MIMIC01_EVAL_ONLY_V1'
KNOWN235_RUN='E2_B3AE_WORLD_MIMIC01_PPO235V4_20261101_0937'
GPUS={'GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}

def metadata(p):
 p=Path(p);assert p.suffix=='.json';b=p.read_bytes();return json.loads(b),dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def qualified(closing,cpu,cpu_sha):
 assert cpu_sha==CPU_SHA and cpu['passed']
 q=cpu['roles']['w35_72'];r=closing['roles']['w35_72'];f=r['formal']
 for x in (q,f,r['final']['final'],closing['formals']['w35_72']):assert x['SHA']==SHA and x['bytes']==BYTES
 assert q['passed'] and q['finite_tensors']==181 and q['saved_iteration']==ITER and q['Adam17_step']==ADAM
 assert q['new_PPO_updates']==UPDATES and q['actual_saved_optimizer_LR']==[LR] and q['actor35_critic38_STD6'] and q['complete_task_and_DR_state_present'] and q['save_at_or_after_requested_deadline']
 assert f['path']==SOURCE_MODEL and f['saved_iteration']==ITER and f['Adam_min']==f['Adam_max']==ADAM and f['actual_new_PPO_updates']==UPDATES
 assert closing['passed_collection'] and r['qualified_formal'] and r['errors']==[] and r['actual_material_limit_error_count']==0 and r['private_EX_free']
 assert r['original_node_terminal']['row']['returncode']==0 and not r['original_node_terminal']['row']['original_error']
 assert r['original_node_exit']['all_own_children_waited'] and r['original_node_exit']['private_EX_released'] and closing['formals']['w35_72']['two_host_SHA_equal']
 o=closing['owner_closed'];assert o['passed'] and o['canonical_None'] and o['shared_locks_free']
 return dict(source_SHA=SHA,model_bytes=BYTES,iteration=ITER,Adam17=ADAM,LR=LR,prior_updates=UPDATES,historical_closed_epoch=o['epoch'])

def validate_task(t,admitted=False):
 expected=dict(kind=KIND,model_SHA=SHA,model_bytes=BYTES,model_iteration=ITER,Adam17=ADAM,model_new_PPO_updates=UPDATES,actual_saved_LR=LR,
  model_path=SOURCE_MODEL,qualified_latest227D_job_root=SOURCE_JOB,num_envs=20000,controls_max=1600,physics_max=12800,feedback_max=3200,
  seconds_max=32.,worker_seconds=3600,parent_seconds=3780,no_new_learning_or_GO=True,model_physical_byte_reads=1,model_decodes=1,model_copies=0,
  legacy_mimic_radians=.05,planned_mimic_radians=.01,closure_m=.002,explicit_guard_tightening=True,full_SuperMimic=False)
 for k,v in expected.items():assert t[k]==v,('Task mismatch',k)
 assert t['GPU_UUID'] in GPUS and t['purpose_id'].startswith('ROOT_W35_LATEST32481_FULL32S_') and t['run_id']
 assert t['telemetry_producer']['format']=='mod4.227.lossless_fieldset_positional_jsonl.v1' and t['telemetry_producer']['retained_byte_limit']==192*1024**2
 if admitted:assert t['actual_current_authority_private_shared_resources_admitted'] and t['original_eval_parent_holds_private_and_validation_EX']
 return True

def validate_authority(c,binding,owner_identity=None,owner_current=None,process_fact=None,closed=None):
 assert c['authority_generation']==GENERATION and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 assert binding['kind']=='KNOWN_ACTIVE235_EXACT_ORIGINAL_E2_SOLO_AUTHORITY_BINDING' and binding['run_id']==KNOWN235_RUN
 owner=binding['owner'];assert owner['pid']==1014881 and owner['creation']==1793496943.07 and owner['cwd']=='/home/lc01/Zonglin Li/zonglin2'
 assert owner_identity['pid']==owner['pid'] and owner_identity['creation']==owner['creation']
 assert owner_current['go']==binding['go'] and set(binding['go'])=={'e2'}
 if c['active_segment'] is not None:
  assert c['active_segment']['owner_parent_pid']==owner['pid'] and process_fact['running']
  for k in ('pid','creation','exe','argv','cwd'):assert process_fact[k]==owner[k],k
  return dict(mode='FRESH_EXACT235_ACTIVE',active_GPU_UUID=binding['go']['e2']['GPU_UUID'],run_id=binding['run_id'],owner=owner)
 assert closed and closed['cohort_final']['go']==binding['go'] and closed['cohort_final']['original_cost_settled'] and closed['owner_exit']['original_cost_settled'] and closed['owner_exit']['own_original_two_fcntl_released_if_held']
 assert not process_fact['running'] and all(x['terminal_all_own_children_waited'] for x in closed['cohort_final']['rows'].values())
 return dict(mode='FRESH_CNONE_AFTER_MATCHING235_CLOSED',active_GPU_UUID=None,run_id=binding['run_id'],owner=owner)

