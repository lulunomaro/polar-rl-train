"""SOURCE schema/predicate only. No native admission, process, file or SDK I/O."""
from __future__ import annotations

PURPOSE = 'NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN'
TASK_KIND = 'PASSIVE_INTERFACE_CAPTURE_N80_TASK_V1'
FINAL_KIND = 'PASSIVE_INTERFACE_CAPTURE_N80_FINAL_V1'
INTEGRATION = 'PHASE1_PASSIVE_INTERFACE_SOURCE_INTEGRATION_V1'
CHANNELS = {'base_ang_vel': 3, 'projected_gravity': 3,
            'leg_pos': 4, 'leg_vel': 4, 'wheel_vel': 2}
UNKNOWN = 'UNKNOWN'


def need(value, message):
    if not value:
        raise ValueError(message)


def validate_source_request(value):
    """A bounded interface request is distinct from original skill denominators."""
    need(type(value) is dict, 'request object required')
    need(value.get('purpose') == PURPOSE, 'NEW capture purpose required')
    need(value.get('kind') == TASK_KIND, 'NEW capture kind required')
    need(value.get('integration') == INTEGRATION, 'NEW integration required')
    need(value.get('requested_roles') in (['E3'], ['E3', 'W35']), 'explicit E3 or E3/W35 only')
    need(type(value.get('controls')) is int and value['controls'] in (64, 128), 'bounded64/128 controls only')
    need(type(value.get('num_envs')) is int and value['num_envs'] == 80, 'original N80 retained')
    need(value.get('action_source') == 'explicit_synthetic0_tape', 'explicit non-policy tape required')
    for field in ('skill_evaluation', 'training_enabled', 'policy_quality_claim', 'native_enabled'):
        need(value.get(field) is False, field + ' must remain false in SOURCE request')
    need(value.get('model_pt_reads') == 0, 'synthetic0 path has zero model reads')
    need(value.get('physics_dt') == .0025 and value.get('decimation') == 8,
         'original physics400Hz/control50Hz retained')
    need(value.get('feedback_period_physics_ticks') == 4, 'original feedback100Hz retained')
    need(value.get('clean_input_dim') == 16 and value.get('full_clean35_mid_end') == UNKNOWN,
         'clean16 only; full clean35 remains UNKNOWN')
    need(value.get('action_observer_status') == 'DEFERRED_UNSEALED', 'action API is not admitted here')
    need(value.get('sensor_dependency_status') == 'SEALED_SOURCE_VERIFIED_NATIVE_PENDING', 'reviewed sealed sensor dependency required')
    need(value.get('gate1') == UNKNOWN, 'SOURCE is not Gate1 admission')
    return dict(value)


def validate_waited_capture_evidence(final, waited, closure, *, role, controls):
    """Future evidence schema, NOT authentication or a native qualification.

    RC0 and old passed_quality/qualQualityTrue are never sufficient. A fake
    schema-consistent fixture is still fake. Action observer is deferred in this
    revision, therefore complete-interface pass stays False unconditionally.
    """
    need(role in ('E3', 'W35') and type(controls) is int and controls in (64, 128),
         'explicit member and bounded controls required')
    need(final.get('kind') == FINAL_KIND and final.get('purpose') == PURPOSE,
         'old quality FINAL is not capture evidence')
    need(final.get('integration') == INTEGRATION and final.get('role') == role,
         'capture integration/member mismatch')
    need(final.get('num_envs') == 80 and final.get('controls') == controls,
         'bounded capture denominator mismatch')
    need(final.get('bridge_controls') == controls and final.get('synthetic_actions') == controls,
         'actual bridge/action counts required')
    need(final.get('physics_ticks_delta') == controls * 8, 'actual original physics ticks required')
    need(final.get('fresh_100hz_samples_by_key') == {k: controls * 2 for k in CHANNELS},
         'unique non-reset original100Hz key samples required, not raw call counts')
    need(final.get('clean_input_dim') == 16 and final.get('full_clean35_mid_end') == UNKNOWN,
         'no manufactured clean35')
    need(final.get('actor35_source') == 'original_returned_policy_buffer', 'actor35 original buffer required')
    need(final.get('observer_extra_plant_calls') == 0 and final.get('observer_rng_calls') == 0,
         'observer has no extra plant or RNG calls')
    need(final.get('actual_binding_checked') is True and final.get('original_return_identity_checked') is True,
         'actual binding and return identity evidence required')
    need(final.get('terminal_pre_reset_observed') is True and final.get('partial_reset_observed') is True,
         'original terminal/partial-reset coverage required; bounded run may remain inconclusive')
    need(final.get('clock_mid_end_observed') is True, 'original mid/end clock observations required')
    need(final.get('actor35_bitwise_untapped_comparison') is True,
         'actual untapped/tapped actor35 comparison is separate from origin identity')
    need(final.get('model_pt_reads') == 0 and final.get('optimizer_steps') == 0,
         'synthetic0 has no PT/optimizer path')
    need(final.get('skill_evaluation') is False and final.get('policy_quality_claim') is False,
         'interface run is not skill quality')
    need(waited.get('actual_popen_wait_returned') is True and type(waited.get('returncode')) is int
         and waited['returncode'] == 0, 'actual child Popen.wait required before semantic evaluation')
    need(waited.get('actual_parent_popen_wait_returned') is True, 'outer actual parent Popen.wait required')
    for field in ('tap_restored_before_bridge_close', 'original_bridge_close_once', 'original_env_close_once',
                  'complete_AppV6_Base_chain', 'actual_app_close_binding_checked',
                  'all_own_children_waited', 'original_private_GPU_EX_released', 'original_finite_EX_released'):
        need(closure.get(field) is True, 'complete real close/wait/release evidence required: ' + field)
    need(closure.get('app_close_semantics') in ('returned_original_once', 'pinned_original_fastclose_intent'),
         'original App close return or NEW-purpose validated pinned fast-close intent required')
    need(closure.get('canonical_writes') == 0 and closure.get('foreign_scope_actions') == 0,
         'original owner/canonical closure retained')
    need(final.get('action_observer_status') == 'DEFERRED_UNSEALED', 'this SOURCE revision keeps action deferred')
    return dict(kind='SOURCE_CAPTURE_EVIDENCE_SCHEMA_CHECK_NOT_NATIVE', schema_consistent=True,
                capture_interface_passed=False, action_observer_status='DEFERRED_UNSEALED',
                gate1=UNKNOWN, exact=False, actual_run_attested_here=False,
                policy_quality=None, skill_pass_rate=None)
