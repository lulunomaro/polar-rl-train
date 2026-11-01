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
KIND='W35_LATEST32481_32S_SAMEUID_RM70_CLOSURE10MM_MIMIC01_EVAL_ONLY_V1'
KNOWN_ACTIVE_RUN='MODEL2050_LITERAL40050_JUMP240_1793502489321389900'
KNOWN_BINDING_KIND='KNOWN_ACTIVE240_EXACT_ORIGINAL_MODEL2050_SOLO_AUTHORITY_BINDING'
KNOWN_ROLE='jump_72'
KNOWN_ACTIVE_GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
EXPECTED_OWNER={'pid': 1018842, 'creation': 1793502495.27, 'exe': '/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2', 'argv': ['/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2', '--library-path', '/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib', '/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python', '-B', '-u', '-B', '-c', "import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"], 'cwd': '/home/lc01/Zonglin Li/zonglin2', 'root': '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MODEL2050_LITERAL_JUMP_400N50_20261101v240/owner72', 'role': 'owner'}
EXPECTED_GO={'jump_72': {'native87_policy_only': False, 'new_native_architecture_fresh': False, 'bootstrap_source_kind': None, 'fresh_environment_resume_scope': None, 'source_normal_PPO_update': None, 'seed': None, 'num_envs': 20000, 'native87_contract_SHA': None, 'manifest_SHA': '03c2df6ddaad2899a95bd083e440fc41db0f9c0fad8eb3d3a30a7ccce766224c', 'bootstrap_SHA': None, 'bootstrap_Adam': None, 'native_continuation_restore_required': False, 'source_native_iteration': None, 'window_start_world_updates': None, 'window_start_policy_updates': None, 'learning_started_epoch': 1793502499.2176878, 'save_deadline': 1793506099.2176878, 'nominal_end_epoch': 1793506399.2176878, 'max_parent_seconds': 3900, 'exit_headroom_seconds': 300, 'source_SHA': 'aac0ef67b8dc7e2b616e45952bf71e09b1ffb24bfcb84644f4d68550ed228869', 'source_native_CPU_SHA': None, 'source_CPU_SHA': '50069ee3616fa3a5a7a20f7aa258d8c5f6bba6809150268080c43aa46729836c', 'source_qualification_kind': 'MODEL2050_LITERAL40050_ACTUAL_SOURCE_CPU_AND_NATIVE8_READY240', 'original_owner_pid': 1018842, 'original_owner_creation': 1793502495.27, 'run_id': 'MODEL2050_LITERAL40050_JUMP240_1793502489321389900', 'actual_H1_prelaunch_v2_scope_admitted': False, 'actual_H1_step270_scope_admitted': False, 'role_key': 'jump_72', 'fullstate_reuse2050': True, 'source_model_SHA': 'aac0ef67b8dc7e2b616e45952bf71e09b1ffb24bfcb84644f4d68550ed228869', 'source_iteration': 2050, 'input_Adam': 41240, 'source_saved_LR': 0.00011390625000000006, 'actor_obs': 35, 'critic_obs': 38, 'action_dim': 6, 'hidden': [128, 64, 32], 'preserve_learned_STD': True, 'ground_envs': 2000, 'jump_envs': 18000, 'literal_original_fudan_JUMP': True, 'original_E0_ground_reward': True, 'physics_dt': 0.0025, 'TGS': [32, 4], 'policy_hz': 50, 'feedback_hz': 100, 'nominal_gas_k_N_m': 2000, 'discount_gamma': 0.9801, 'discount_lam': 0.9025, 'one_original_writer': True, 'new_target_D0_D7_physical_queues_and_reward_memory': True, 'source_ONNX_actor_identity_passed': True, 'full_actor_critic_STD_17Adam_restore_required': True}}
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
  legacy_mimic_radians=.05,planned_mimic_radians=.01,closure_m=.01,previous_closure_m=.002,user_authorized_closure10mm=True,explicit_mimic_guard_tightening=True,full_SuperMimic=False)
 for k,v in expected.items():assert t[k]==v,('Task mismatch',k)
 assert t['GPU_UUID'] in GPUS and t['purpose_id'].startswith('ROOT_W35_LATEST32481_FULL32S_CLOSURE10MM_') and t['run_id']
 assert t['telemetry_producer']['format']=='mod4.227.lossless_fieldset_positional_jsonl.v1' and t['telemetry_producer']['retained_byte_limit']==192*1024**2
 if admitted:assert t['actual_current_authority_private_shared_resources_admitted'] and t['original_eval_parent_holds_private_and_validation_EX']
 return True

def validate_authority(c,binding,owner_identity=None,owner_current=None,process_fact=None,closed=None):
 assert c['authority_generation']==GENERATION and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 assert binding['kind']==KNOWN_BINDING_KIND and binding['run_id']==KNOWN_ACTIVE_RUN
 owner=binding['owner']
 for k in ('pid','creation','exe','argv','cwd','root'):assert owner[k]==EXPECTED_OWNER[k],k
 assert owner_identity['pid']==owner['pid'] and owner_identity['creation']==owner['creation']
 # b.ident.root is process cwd;SPAWN.owner.root is its task directory.
 # Use explicit fresh process cwd for comparison,never compare those root labels.
 assert binding['go']==EXPECTED_GO and owner_current['go']==EXPECTED_GO and set(binding['go'])=={KNOWN_ROLE}
 if c['active_segment'] is not None:
  a=c['active_segment'];assert a['owner_parent_pid']==owner['pid'] and process_fact['running']
  for k in ('pid','creation','exe','argv','cwd'):assert process_fact[k]==owner[k],k
  # Original240 charge_values initializes this exact field from full GO.
  assert set(a['experts'])=={KNOWN_ROLE} and a['experts'][KNOWN_ROLE]['started_epoch']==EXPECTED_GO[KNOWN_ROLE]['learning_started_epoch']
  return dict(mode='FRESH_EXACT240_ACTIVE',active_GPU_UUID=KNOWN_ACTIVE_GPU_UUID,run_id=binding['run_id'],owner=owner)
 assert closed and closed['cohort_final']['go']==EXPECTED_GO and closed['cohort_final']['original_cost_settled'] and closed['owner_exit']['original_cost_settled'] and closed['owner_exit']['own_original_two_fcntl_released_if_held']
 assert not process_fact['running'] and set(closed['cohort_final']['rows'])=={KNOWN_ROLE} and all(x['terminal_all_own_children_waited'] for x in closed['cohort_final']['rows'].values())
 return dict(mode='FRESH_CNONE_AFTER_MATCHING240_CLOSED',active_GPU_UUID=None,run_id=binding['run_id'],owner=owner)
