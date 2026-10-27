"""Pure typed metadata contract. No I/O, model loading, authority or GO on import."""
import hashlib,json,re
SOURCE_SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
SOURCE_UPDATE=138
SOURCE_ADAM=832460
KIND='MOD4_H1_NATIVE87_POLICY_ONLY_SOURCE_SDK_CPU_PRECONTROL_V2'
AUTHORITY_GENERATION='MOD4_SINGLE_WRITER72_20261026'
CANONICAL='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
GPUS=dict(h1='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',e2='GPU-16828f91-2b45-b646-8dc0-9481138e2842',recovery='GPU-c27eecbd-6838-7290-1cd2-37e34522213d')
SEEDS=dict(h1=27,e2=28,recovery=29)
METHOD=dict(num_envs=4096,episode_timeout_s=5.,control_dt_s=.01,physics_dt_s=.0025,solver='TGS',solver_position_iterations=32,solver_velocity_iterations=4,decimation=4,
    packed_state_dim=127,aux_dim=54,static_xi_dim=31,obs_dim=86,goal_dim=146,goal_frames=10,hist=10,
    wm_hidden=[2048,2048,2048],policy_hidden=[2048,1024,512,256],horizon=32,buffer_steps=1000,
    utd=.4,wm_batch=1024,pi_batch=1024,wm_only_iters=64,amp='none',compile=False)
REPLAY_BYTES_PER_TRANSITION=1205 # s127+s1127+a6+a_prev6+xi31+r fp32;f int64;ep_step int32;done bool
REPLAY_BYTES=4096*1000*REPLAY_BYTES_PER_TRANSITION
MIN_RAM_BYTES=32*1024**3
MIN_FREE_GPU_MIB=15669
MIN_PAYLOAD_DISK_BYTES=25*1024**3
MIN_SAVE_DISK_BYTES=8*1024**3

def digest(value):return hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest()
def sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None
def require(v,message):
    if not v:raise ValueError(message)

def validate_spec(s):
    key=s['key'];require(key in SEEDS,'unknown slot')
    require(s.get('native87_policy_only') is True and s.get('new_native_architecture_fresh') is True,'new method scope required')
    require(s.get('finite_method_test') is True,'explicit finite native method scope required')
    require(s.get('closed_production_continuation') is False and s.get('native_continuation') is False,'no exact production/native continuation claim')
    require(s.get('bootstrap_source_kind')=='closed_production_policy_only','typed normal bootstrap source required')
    require(s.get('source_SHA')==s.get('bootstrap_source_SHA')==SOURCE_SHA,'all3 slots must use qualified H1 update138')
    require(s.get('source_Adamstep')==SOURCE_ADAM and s.get('source_normal_PPO_update')==SOURCE_UPDATE,'source counter mismatch')
    require(s.get('seed')==SEEDS[key] and s.get('method_config')==METHOD,'seed/method mismatch')
    require(s.get('GPU_UUID')==GPUS[key] and s.get('execution_backend')==('source210' if key=='h1' else 'target72'),'GPU/backend mismatch')
    require(s.get('policy_hz')==100 and s.get('max_parent_seconds')==3900 and s.get('exit_headroom_seconds')==300,'original finite clock/cap required')
    require(s.get('owner_authority_generation')==AUTHORITY_GENERATION,'sole72 generation mismatch')
    require(s.get('fresh_environment_resume_scope')=='policy_only_no_source_environment_state','source20k state must not be reshaped')
    if key=='h1':require(sha(s.get('owner_control_dependency_binding_SHA')),'h1 control dependency binding SHA required')
    for k in ('manifest_SHA','native87_contract_SHA','qualified_H1_report_SHA','previous86_closure_SHA','reference_artifact_SHA','objective_contract_SHA'):
        require(sha(s.get(k)),k+' required')
    require(isinstance(s.get('candidate_pins'),dict) and s['candidate_pins'] and all(sha(v) for v in s['candidate_pins'].values()),'exact candidate pins required')
    return True

def validate_schedule(cfg):
    require(set(cfg['experts'])==set(SEEDS) and cfg['deferred_experts']==[],'all3 H1 seeds required')
    require(cfg['scheduling_authority']=='human_requested_available_experts' and cfg['authority_generation']==AUTHORITY_GENERATION,'authority mismatch')
    for key,s in cfg['experts'].items():require(key==s['key'] and validate_spec(s),'slot mismatch')
    return True

READY_FLAGS=('role_control_dependency_metadata_closure_checked','actual_installed_CPU_passed','actual_H1_source_SDK_CPU_passed','whole_frozen_PPO_policy_source_CPU_passed',
    'actor9_critic8_STD17Adam_source_exact','RSL_wholepolicy_strict_roundtrip_passed','source_normal138_qualified',
    'source_original86_all3_cost_allout_passed','factory4096_timeout5_source_CPU_passed','fresh_policy_only_scope_source_CPU_passed',
    'source20k_environment_state_not_restored','new_native_architecture_source_API_CPU_passed','new_native_optimizer_scope_source_CPU_passed',
    'original_physics_clip6_success_guards_retained','expected_runtime30joint_order_source_CPU_passed','actual_GPU_precontrol_admission_required',
    'reference_provider_future10_actual_CPU_passed','manifest_and_exact_python_inventory_passed')

def native87_valid_ready(row,spec):
    try:
        validate_spec(spec);envelope=row.get('closed_source_CPU') or {};v=envelope.get('value') or {}
        return bool(row.get('key')==spec['key'] and row.get('phase')=='ready' and not row.get('original_error')
          and row.get('manifest_SHA')==spec['manifest_SHA'] and envelope.get('actual_CPU_waited_EXIT0') is True
          and envelope.get('SHA')==digest(v) and v.get('kind')==KIND and v.get('passed') is True
          and v.get('source_SHA')==v.get('bootstrap_SHA')==SOURCE_SHA and v.get('source_normal_PPO_update')==138
          and v.get('bootstrap_Adam')==832460 and v.get('native_continuation_restore_required') is False
          and v.get('native_environment_state_from_source') is False and v.get('source_environment_count')==20000
          and v.get('configured_environment_count')==4096 and v.get('actual_environment_count') is None and v.get('actual_GPU_runtime_readback_passed') is False and v.get('actual_GPU_fresh4096_DR_readback_passed') is False and v.get('episode_timeout_s')==5.
          and v.get('GPU_UUID')==spec['GPU_UUID'] and v.get('execution_backend')==spec['execution_backend']
          and v.get('seed')==spec['seed'] and v.get('method_config')==METHOD and v.get('candidate_pins')==spec['candidate_pins']
          and (v.get('role_control_dependency_CPU') or {}).get('checked') is True
          and ((v.get('role_control_dependency_CPU') or {}).get('actual_installed_dependencies_verified') is True
               and v.get('owner_control_dependency_binding_SHA')==spec['owner_control_dependency_binding_SHA']
               and (v.get('role_control_dependency_CPU') or {}).get('binding_SHA')==spec['owner_control_dependency_binding_SHA']
               and (v.get('role_control_dependency_CPU') or {}).get('scope')=='source210_h1_exact_installed_dependency_SHA_and_import'
               if spec['key']=='h1' else (v.get('role_control_dependency_CPU') or {}).get('scope')=='target72_original_loopback_not_required'
               and (v.get('role_control_dependency_CPU') or {}).get('actual_installed_dependencies_verified') is False)
          and all(v.get(k) is True for k in READY_FLAGS)
          and all(v.get(k)==spec[k] for k in ('native87_contract_SHA','qualified_H1_report_SHA','previous86_closure_SHA','reference_artifact_SHA','objective_contract_SHA')))
    except (ValueError,KeyError,TypeError):return False

def validate_saved_source_and_closure(qualified,typed_close,authority):
    require(qualified['passed'] is True and qualified['key']=='h1','qualified source report missing')
    v=qualified['value'];f=v['final']
    require(v['passed'] and v['normal_PPO_source_only'] and f['SHA']==SOURCE_SHA and f['updates']==138 and v['Adam']==832460,'wrong qualified source')
    require(f['formal_manifest_passed'] and f['twohost_complete_SHA'] and not f['failed_partial_prefix'],'source not formally qualified')
    require(typed_close['passed'] and typed_close['original_canonical_cost_settled'] and not typed_close['errors'],'previous86 close not complete')
    require(authority['all_authority72_owner_children_actual_out'] and authority['canonical_active_segment'] is None
        and authority['canonical_path']==CANONICAL and authority['no_account_write_or_canonical_copy'],'previous86 authority not allout')
    return True

def worker_plan(spec):
    validate_spec(spec)
    return dict(slot=spec['key'],seed=spec['seed'],method='H1_native_v3_repaired_independent_seed',
        bootstrap_source_SHA=SOURCE_SHA,bootstrap_update138=True,bootstrap_Adam832460=True,
        bootstrap_scope='frozen normal PPO actor9+critic8+STD+17Adam only; no env/RNG/DR/replay/phase reshape',
        fresh_native_architecture=True,exact_native86_continuation=False,method_config=METHOD,
        output_fullsave='new real4096 D0-D7 + new WM/Pi/Critic/3optimizers/config/reference/counters/RNG',
        replay_bytes=REPLAY_BYTES,history_obs_bytes=4096*10*86*4,minimum_available_RAM_bytes=MIN_RAM_BYTES,
        GPU_empty_MiB_strictly_greater=15669,VRAM_peak_admission='pending_actual_physics+replay+BPTT+save_probe',
        payload_free_disk_bytes=MIN_PAYLOAD_DISK_BYTES,fullsave_free_disk_bytes=MIN_SAVE_DISK_BYTES,
        paper_deviations=['WM/Pi batch1024 vs upstream G1batch4096; different MOD4 task/hardware, not paper speed reproduction',
           'wm_only64 vs paper500 due original3900s finitewindow; not paper speed reproduction'],
        installed_SDK_admission='pending_no_actual_Task_GO_or_install_created')
