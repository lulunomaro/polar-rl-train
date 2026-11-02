"""Pure WM-only Task/Ready/GO/receipt ABI. No controller, I/O or budget writer.

jump_72 is ONLY the existing240 transport slot. It grants no PPO/Pi update.
Unknown explicit runtime Task fields are retained; required scope is validated.
"""
from copy import deepcopy
import hashlib
import json
import math

KIND = 'OWN_DEPTH_WM_ONLY_FROZEN_TEACHER2135_ONLINE_WARM_403N50_V275'
READY_KIND = 'OWN_DEPTH_WM_ONLY_FROZEN_TEACHER2135_FIRST_ANCHOR_READY_V275'
FIRST_KIND = 'FIRST_ACTUAL_NEW_WM_UPDATE_FROZEN_TEACHER2135_V275'
FINAL_KIND = 'FINAL_ACTUAL_WM_WARM_FROZEN_TEACHER2135_V275'
ROLE = 'jump_72'
LEARNING_SCOPE = 'one_new_WM_Adam_only'
SOURCE_SHA = '0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'
PARENT_SHA = 'aac0ef67b8dc7e2b616e45952bf71e09b1ffb24bfcb84644f4d68550ed228869'
WM_INDEX_SHA = '05925ecccf95c58b0e1203207e4b1e5d6ec81c5a9eb16f2c67bae4dbcbcde3cf'
TEACHER_BYTES = 22099209
TEACHER_ITERATION = 2135
TEACHER_ADAM = 42940
TEACHER_LR = .0019461950683593758


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def ready_value_SHA(value):
    """Exact actual240 owner/node serialization. Not a model-CPU report hash."""
    return hashlib.sha256(json.dumps(value, indent=2).encode()).hexdigest()


def task_defaults():
    return dict(kind=KIND, role_key=ROLE, transport_role_label=ROLE,
        learning_scope=LEARNING_SCOPE, WM_ONLY=True, FROZEN_TEACHER=True,
        source_SHA=SOURCE_SHA, source_parent_SHA=PARENT_SHA, source_bytes=TEACHER_BYTES,
        source_iteration=TEACHER_ITERATION, source_Adam_step=TEACHER_ADAM, source_LR=TEACHER_LR,
        actor_obs=35, critic_obs=38, action_dim=6, learned_STD_dim=6,
        source_hidden=[128, 64, 32], source_activation='elu',
        freeze_actor_critic_STD_full17Adam=True, actual_Pi_Critic_teacher_updates=0,
        PPO_updates_allowed=False, Pi_updates_allowed=False, critic_updates_allowed=False,
        STD_updates_allowed=False, WM_optimizer_count=1, new_WM_Adam=True,
        new_WM_architecture_fresh=True, window_start_world_updates=0, window_start_policy_updates=0,
        convert_actor44_critic47=False, complete_three_optimizer_conversion=False,
        WM_source_INDEX_SHA=WM_INDEX_SHA, WM_input_dim=273, WM_output_dim=223,
        state_dim=224, physical_dim=73, auxiliary_dim=151, context_dim=40,
        first_current_anchor_only=True, future_actual_depth_in_H32=False,
        WM_H=32, WM_batch=1024, replay_capacity=64, WM_hidden=[512, 512, 512],
        WM_learning_rate=.0001, WM_gradient_clip=1., WM_time_loss_reduction='sum_time_div_batch',
        num_envs=80, ground_envs=8, jump_envs=72,
        terrain_scheme='ORIGINAL272_FUDAN_STATIC_LEVEL0_TO5_WM_DATA_ONLY',
        terrain_levels=[0, 1, 2, 3, 4, 5], terrain_placement_static=True,
        original_dynamic_curriculum_claimed=False, no_270mm_extension=True,
        literal_original_fudan_JUMP=True, original_E0_ground_reward_separate=True,
        original_Fudan19_methods_16weights_unchanged=True,
        physics_dt=.0025, physics_dtype='F32', TGS=[32, 4], policy_hz=50, feedback_hz=100,
        gas_nominal_N=400, gas_nominal_k_N_m=2000, D0white_v3_D1_D7=True,
        closure_m=.01, mimic_rad=.01, one_original_writer=True,
        native_before_first_WM_controls=24, fresh_physics_DR_not_old_environment_resume=True,
        checkpoint_complete_DR_command_air_contact_memory=True,
        max_parent_seconds=3900, save_seconds=3600, exit_headroom_seconds=300,
        native87_policy_only=False, native_continuation=False, new_native_architecture_fresh=False,
        actual_H1_step270_scope_admitted=False, actual_Pi_runtime_admitted=False)


def validate_task(t):
    require(isinstance(t, dict), 'Task object required')
    for key, value in task_defaults().items():
        require(t.get(key) == value, 'Wrong WM-only Task field: ' + key)
    # These are separate real saved-evidence scopes, supplied by ROOT.
    for key in ('source_CPU_report_SHA', 'actual272_receipt_SHA', 'actual274_receipt_SHA', 'worker_SHA'):
        require(sha(t.get(key)), 'Missing actual source/evidence SHA: ' + key)
    for key in ('run_id', 'job_root', 'owner_root'):
        require(isinstance(t.get(key), str) and t[key], 'Missing actual runtime identity/path: ' + key)
    require(t['job_root'].startswith('/') and t['owner_root'].startswith('/'), 'Actual absolute target roots required')
    require(not t.get('source_CPU_SHA'), 'Ready VALUE SHA belongs in owner GO/row, not Task (no circular self-hash)')
    # Runtime272 fields are allowed. If aliases exist, their meaning is exact.
    for key, expected in (('model_SHA', SOURCE_SHA), ('model_bytes', TEACHER_BYTES),
                          ('model_iteration', TEACHER_ITERATION), ('model_Adam_step', TEACHER_ADAM)):
        if key in t:
            require(t[key] == expected, 'Wrong qualified teacher alias: ' + key)
    if 'manifest_SHA' in t:
        require(sha(t['manifest_SHA']), 'Invalid optional manifest binding')
    return True


def make_task(runtime_fields):
    t = task_defaults()
    t.update(deepcopy(runtime_fields))
    validate_task(t)
    return t


def validate_schedule(c):
    require(isinstance(c, dict) and set(c.get('experts', {})) == {ROLE}, 'One original72 transport slot only')
    require(c.get('scheduling_authority') == 'human_requested_available_experts' and c.get('deferred_experts') == [],
            'Original schedule authority/deferred contract required')
    spec = c['experts'][ROLE]
    validate_task(spec)
    require(spec.get('key') == ROLE and spec.get('execution_backend') == 'target72', 'Wrong original transport/backend')
    require(spec.get('run_id') == c.get('run_id') and sha(spec.get('manifest_SHA')), 'Schedule Task/run/manifest mismatch')
    require(isinstance(spec.get('GPU_UUID'), str) and spec['GPU_UUID'].startswith('GPU-'), 'ROOT actual selected GPU required')
    return True


def flat_go_fields(s):
    validate_task(s)
    # No source_CPU_SHA is returned. The original owner already assigns it
    # from row.closed_source_CPU.SHA = SHA(json.dumps(full Ready VALUE,indent=2)).
    return dict(role_key=ROLE, transport_role_label=ROLE, learning_scope=LEARNING_SCOPE,
        WM_ONLY=True, FROZEN_TEACHER=True, WM_task_kind=KIND,
        frozen_teacher_fullstate_reuse2135=True, source_model_SHA=SOURCE_SHA,
        source_parent_SHA=PARENT_SHA, source_iteration=TEACHER_ITERATION,
        input_Adam=TEACHER_ADAM, source_saved_LR=TEACHER_LR,
        actor_obs=35, critic_obs=38, action_dim=6, learned_STD_dim=6,
        freeze_actor_critic_STD_full17Adam=True, actual_Pi_Critic_teacher_updates=0,
        WM_optimizer_count=1, new_WM_Adam=True, window_start_world_updates=0, window_start_policy_updates=0,
        convert_actor44_critic47=False, complete_three_optimizer_conversion=False,
        WM_source_INDEX_SHA=WM_INDEX_SHA, WM_input_dim=273, WM_output_dim=223,
        state_dim=224, auxiliary_dim=151, context_dim=40, WM_H=32, WM_batch=1024,
        replay_capacity=64, WM_hidden=[512, 512, 512], first_current_anchor_only=True,
        future_actual_depth_in_H32=False, num_envs=80, ground_envs=8, jump_envs=72,
        terrain_scheme=s['terrain_scheme'], terrain_levels=s['terrain_levels'], terrain_placement_static=True,
        no_270mm_extension=True, original_Fudan19_methods_16weights_unchanged=True,
        original_E0_ground_reward_separate=True, physics_dt=.0025, TGS=[32, 4],
        policy_hz=50, feedback_hz=100, gas_nominal_N=400, D0white_v3_D1_D7=True,
        closure_m=.01, mimic_rad=.01, one_original_writer=True,
        actual_H1_step270_scope_admitted=False, actual_Pi_runtime_admitted=False)


def validate_ready_value(v, spec):
    validate_task(spec)
    require(isinstance(v, dict) and v.get('passed') is True and v.get('kind') == READY_KIND, 'Wrong actual WM Ready VALUE')
    for key in ('source_SHA', 'source_parent_SHA', 'source_bytes', 'source_iteration', 'source_LR',
                'source_CPU_report_SHA', 'actual272_receipt_SHA', 'actual274_receipt_SHA', 'worker_SHA',
                'WM_source_INDEX_SHA', 'num_envs', 'ground_envs', 'jump_envs'):
        require(v.get(key) == spec[key], 'Ready/evidence Task mismatch: ' + key)
    require(v.get('Adam_step') == TEACHER_ADAM and v.get('manifest_SHA') == spec['manifest_SHA'], 'Ready teacher/manifest mismatch')
    for key in ('WM_ONLY', 'FROZEN_TEACHER', 'teacher_fullstate_CPU_passed',
                'actor35_critic38_STD6_full17Adam_finite', 'actual272_complete_current_packet_PASS',
                'actual274_CUDA_H32_no_step_PASS', 'first_current_anchor_only',
                'fresh_CNone_CIM_resources_actual', 'target_private_and_validation_EX_probe_released'):
        require(v.get(key) is True, 'Missing actual WM admission proof: ' + key)
    require(v.get('actual_Pi_Critic_teacher_updates') == 0 and v.get('admission_optimizer_steps') == 0,
            'Admission cannot contain policy or optimizer updates')
    for key, expected in (('WM_input_dim', 273), ('WM_output_dim', 223), ('state_dim', 224),
                          ('WM_H', 32), ('WM_batch', 1024), ('WM_hidden', [512, 512, 512]),
                          ('complete_three_optimizer_conversion', False), ('future_actual_depth_in_H32', False)):
        require(v.get(key) == expected, 'Wrong actual CUDA WM admission shape/scope: ' + key)
    require(type(v.get('supported_start_candidates')) is int and v['supported_start_candidates'] > 0,
            'No actual supported first-anchor starts')
    require(sha(v.get('actual_resource_admission_SHA')), 'Fresh actual resource receipt SHA required; released probe, no node-held-lock claim')
    require(v.get('learning_scope') == LEARNING_SCOPE and v.get('transport_role_label') == ROLE, 'Ready learning/transport scope mismatch')
    return True


def make_ready_value(spec, actual_evidence):
    """Assemble metadata from ROOT's actual projections; never manufactures PASS."""
    validate_task(spec)
    keys = ('source_SHA', 'source_parent_SHA', 'source_bytes', 'source_iteration', 'source_LR',
        'source_CPU_report_SHA', 'actual272_receipt_SHA', 'actual274_receipt_SHA', 'worker_SHA',
        'WM_source_INDEX_SHA', 'num_envs', 'ground_envs', 'jump_envs')
    v = {k: spec[k] for k in keys}
    v.update(kind=READY_KIND, manifest_SHA=spec['manifest_SHA'], Adam_step=TEACHER_ADAM,
        WM_input_dim=273, WM_output_dim=223, state_dim=224, WM_H=32, WM_batch=1024,
        WM_hidden=[512, 512, 512], complete_three_optimizer_conversion=False,
        future_actual_depth_in_H32=False, learning_scope=LEARNING_SCOPE, transport_role_label=ROLE)
    v.update(deepcopy(actual_evidence))
    validate_ready_value(v, spec)
    return v


def valid_ready(row, spec):
    try:
        q = row.get('closed_source_CPU') or {}
        v = q.get('value') or {}
        validate_ready_value(v, spec)
        return bool(row.get('key') == spec['key'] and row.get('phase') == 'ready'
            and row.get('manifest_SHA') == spec['manifest_SHA'] and not row.get('original_error')
            and q.get('SHA') == ready_value_SHA(v))
    except (KeyError, TypeError, ValueError):
        return False


def _go_identity(g, run, t):
    validate_task(t)
    require(g.get('run_id') == run == t['run_id'] and g.get('source_SHA') == SOURCE_SHA, 'Wrong current WM run/source')
    for key, value in flat_go_fields(t).items():
        require(g.get(key) == value, 'Wrong typed WM GO field: ' + key)
    require(g.get('source_qualification_kind') == READY_KIND and sha(g.get('source_CPU_SHA')), 'GO requires complete Ready VALUE hash/kind')
    require(sha(g.get('manifest_SHA')), 'GO manifest missing')
    if 'manifest_SHA' in t:
        require(g['manifest_SHA'] == t['manifest_SHA'], 'Task/GO manifest mismatch')
    require(g.get('max_parent_seconds') == 3900 and g.get('exit_headroom_seconds') == 300, 'Original finite caps required')
    started = g.get('learning_started_epoch')
    require(isinstance(started, (int, float)) and math.isfinite(started), 'Actual original owner start epoch required')
    require(g.get('save_deadline') == started + 3600 and g.get('nominal_end_epoch') == started + 3900, 'Original3600save/3900exit required')
    return True


def validate_go(g, run, t, now):
    _go_identity(g, run, t)
    require(g['learning_started_epoch'] <= now < g['save_deadline'], 'WM admission outside original learning window')
    return True


def validate_ready_go(g, value, spec):
    validate_ready_value(value, spec)
    require(g.get('source_CPU_SHA') == ready_value_SHA(value), 'GO source_CPU_SHA is full Ready VALUE SHA, not teacher modelCPU SHA')
    require(g.get('manifest_SHA') == spec['manifest_SHA'] and g.get('source_qualification_kind') == READY_KIND,
            'Ready/GO manifest or kind mismatch')
    return True


def _counter_and_save(r, t, g, *, first):
    _go_identity(g, t['run_id'], t)
    require(r.get('passed') is True and r.get('kind') == (FIRST_KIND if first else FINAL_KIND), 'Wrong WM production receipt')
    require(r.get('source_SHA') == SOURCE_SHA and r.get('run_id') == t['run_id'], 'Receipt teacher/run mismatch')
    u = r.get('actual_new_WM_updates')
    require(type(u) is int and (u == 1 if first else u > 0), 'Actual new WM update invariant failed')
    for key in ('actual_new_PPO_updates', 'actual_new_Pi_updates', 'actual_new_critic_updates',
                'actual_new_STD_updates', 'actual_Pi_Critic_teacher_updates'):
        require(r.get(key) == 0, 'Frozen teacher/Pi counter must stay0: ' + key)
    require(r.get('WM_optimizer_count') == 1 and r.get('teacher_actor_critic_STD_full17Adam_unchanged') is True,
            'One new WM Adam/frozen teacher proof required')
    for key, expected in (('teacher_iteration', TEACHER_ITERATION), ('teacher_Adam_step', TEACHER_ADAM),
                          ('teacher_LR', TEACHER_LR), ('convert_actor44_critic47', False),
                          ('complete_three_optimizer_conversion', False)):
        require(r.get(key) == expected, 'Wrong frozen teacher/conversion receipt: ' + key)
    controls = r.get('new_completed_controls')
    require(type(controls) is int and controls >= 32 and r.get('new_environment_transitions') == controls * 80,
            'Actual80env control/transition counts required')
    require(r.get('physics_callbacks') == controls * 8 and r.get('feedback_samples') == controls * 2,
            'Original8physics/2feedback counts required')
    require(r.get('teacher_source_byte_reads') == 1 and r.get('teacher_source_decodes') == 1, 'One necessary frozen teacher byte read/decode required')
    require(r.get('finite_WM_loss_grad_params_optimizer') is True, 'Actual finite WM tree required')
    require(r.get('native24_before_first_WM_step_passed') is True, 'Actual native24 must precede first WM update')
    require(sha(r.get('actual_resource_admission_SHA')), 'Production receipt must bind actual node-held resource JSON SHA (not staged probe SHA)')
    saved = r.get('first_complete' if first else 'final') or {}
    require(isinstance(saved.get('path'), str) and saved['path'].startswith('/')
        and type(saved.get('bytes')) is int and saved['bytes'] > 0 and sha(saved.get('SHA')), 'Complete new WM artifact metadata required')
    for key, expected in (('saved_WM_updates', u), ('WM_Adam_step_min', u), ('WM_Adam_step_max', u),
                          ('teacher_iteration', TEACHER_ITERATION), ('teacher_Adam_step', TEACHER_ADAM),
                          ('teacher_LR', TEACHER_LR), ('typed_WM_only_task_present', True),
                          ('full_WM_tree_finite', True), ('frozen_teacher_fullstate_preserved', True),
                          ('replay_saved', False), ('complete_three_optimizer_conversion', False)):
        require(saved.get(key) == expected, 'Wrong complete WM save field: ' + key)
    require(isinstance(saved.get('save_epoch'), (int, float)) and math.isfinite(saved['save_epoch']), 'Actual save epoch required')
    require(saved['save_epoch'] >= g['learning_started_epoch'], 'WM artifact predates this window')
    if not first:
        require(saved['save_epoch'] >= g['save_deadline'], 'Normal full WM save must reach original deadline')
    return True


def validate_first(r, t, g):
    return _counter_and_save(r, t, g, first=True)


def validate_final(r, t, g):
    return _counter_and_save(r, t, g, first=False)
