"""Decoded-only application of the frozen Phase1 verifier; no artifact I/O or CLI.

See README.md for original-byte provenance, retained-only scope and source pins.
None means an unavailable original, never zero controls or a successful capture.
"""
import copy

import capture_evidence_verifier_v1 as pure

PURE_REFERENCE = {
    'bytes': 41739,
    'SHA256': '2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979',
}
V3_REVIEWED_REFERENCE = {
    'capture_source_index': {
        'bytes': 124202,
        'SHA256': 'bdeea3f057fb922bd9ae2670dcbf19188f651ca64ab2cbb0331f56a5a1124797'},
    'worker_source_seal': {
        'bytes': 2920,
        'SHA256': '80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da'},
    'B2_sensor_source_seal': {
        'bytes': 2909,
        'SHA256': 'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a'},
}
ARTIFACTS = {
    'worker_final': 'cases/E3/FINAL.json',
    'task': 'cases/E3/task.json',
    'group_final': 'FINAL.json',
    'parent_exit_scope': 'PARENT_EXIT_SCOPE.json',
    'source_grade': 'PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json',
    'common_go': 'GROUP_EVAL_START.json',
    'worker_ready': 'cases/E3/WORKER_SCENE_READY.json',
    'worker_started': 'cases/E3/WORKER_EVAL_STARTED.json',
    'env_close': 'cases/E3/ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json',
    'app_close_binding': 'cases/E3/APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json',
    'app_fast_intent': 'cases/E3/APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json',
    'app_close_returned': 'cases/E3/APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json',
    'parent_started': 'PARENT_STARTED.json',
    'parent_dispatch': 'PHASE1_CAPTURE_PARENT_DISPATCH_RECEIPT_V1.json',
    'controller_started': 'PHASE1_CAPTURE_PARENT_CONTROLLER_STARTED_V1.json',
    'outer_parent_wait': 'PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json',
    'worker_error': 'cases/E3/WORKER_ERROR.json',
    'parent_error': 'PARENT_ORIGINAL_ERROR.json',
}
REQUIRED_LIFECYCLE = (
    'group_final', 'parent_exit_scope', 'source_grade', 'common_go',
    'worker_ready', 'worker_started', 'env_close', 'app_close_binding',
    'parent_started', 'parent_dispatch', 'controller_started', 'outer_parent_wait',
)
WHOLE_FIELDS = (
    'sensor', 'actuation', 'boundary', 'coverage', 'rng_counts',
    'bounded_trace', 'restore', 'original_setup', 'inconclusive_reasons',
)
COMPONENTS = {
    'retention_schema': 'sensor_retention_schema',
    'retained_100Hz_MID_END_noise_used_cache': 'clean16_used_noise_bias_delay_and_episode_clock',
    'physical_pre_reset_and_partial_reset': 'pre_reset_bridge_and_partial_reset',
    'original_actor_same_buffer': 'original_actor_same_buffer_sanity',
    'retained_queue_issue_apply_write_reset': 'retained_actuation_queue_issue_apply_write',
    'stored_RNG_DR_source_claims': 'stored_RNG_static_memory_and_source_claims',
}


def _gap(alias, reason, *, missing_fields=None, provenance_only=False):
    return dict(alias=alias, original_artifact=ARTIFACTS.get(alias), reason=reason,
                missing_fields=missing_fields,
                action=('reuse original-byte metadata from the caller-held whole cache; '
                        'canonical reserialization is not the original byte identity'
                        if provenance_only else
                        'supply the original whole document only if it was actually published; '
                        'otherwise keep unavailable; no reconstruction from a projection'),
                no_fetch_or_retry_performed=True)


def _producer_reference(reported):
    match = (None if reported is None else type(reported) is dict and all(
        pure.typed_equal(reported.get(k), v) for k, v in V3_REVIEWED_REFERENCE.items()))
    return dict(reviewed_V3_reference=copy.deepcopy(V3_REVIEWED_REFERENCE),
                reported_source_pins=copy.deepcopy(reported),
                reported_metadata_matches_reviewed_V3_reference=match,
                actual_staged_runtime_binding='UNKNOWN_EXTERNAL_PARENT_EVIDENCE',
                scope='reference comparison only; not producer authentication, V4 identity or an approval gate')


def apply_capture(final, task, lifecycle, original_byte_provenance, reported_producer_pins=None):
    """Organize supplied ORIGINAL whole decoded documents; never read or fetch them.

    original_byte_provenance maps each document alias to original_bytes,
    original_SHA256 and decoded_canonical_SHA256. Those are caller attestations;
    the frozen verifier checks syntax and decoded binding, not physical I/O.
    reported_producer_pins is optional and never gates the decoded evidence.
    """
    life = ({k: v for k, v in lifecycle.items() if v is not None}
            if type(lifecycle) is dict else {})
    out = dict(kind='PHASE1_ACTUAL_CAPTURE_DECODED_APPLICATION_SOURCE_V1',
               status='NOT_EVALUABLE', counts=None,
               execution=dict(status='NOT_EVALUABLE', value=None),
               source_reference=_producer_reference(reported_producer_pins),
               schema_method_reference=dict(pure_module=copy.deepcopy(PURE_REFERENCE),
                   schema_reference_id=pure.SOURCE_ID, source_pin_count=len(pure.SOURCE_PINS),
                   scope='17 schema/method references, NOT V3/V4 producer qualification'),
               evidence={}, artifact_gaps=[], pure_review=None,
               published_failure_facts={k: copy.deepcopy(life[k]) for k in
                   ('worker_error', 'parent_error', 'outer_parent_wait', 'parent_exit_scope') if k in life},
               gate1='UNKNOWN', exact=False, capture_interface_passed=False,
               paper_ready=False, stage2_GO=False, skill_success_rate=None,
               application_is_admission=False, artifact_reads_performed=0)
    gaps = out['artifact_gaps']
    if final is None:
        gaps.append(_gap('worker_final', 'MISSING_ORIGINAL_FINAL; publication/existence not assumed'))
    elif type(final) is dict:
        absent = [k for k in WHOLE_FIELDS if k not in final]
        if absent:
            gaps.append(_gap('worker_final', 'MISSING_WHOLE_PAYLOAD_FIELDS; a projection is not a whole FINAL', missing_fields=absent))
    if task is None:
        gaps.append(_gap('task', 'original task unavailable'))
    for alias in REQUIRED_LIFECYCLE:
        if alias not in life:
            gaps.append(_gap(alias, 'original published lifecycle document unavailable'))
    binding = life.get('app_close_binding')
    if type(binding) is dict and type(binding.get('fast_shutdown')) is bool:
        close_alias = 'app_fast_intent' if binding['fast_shutdown'] else 'app_close_returned'
        if close_alias not in life:
            gaps.append(_gap(close_alias, 'original mode-specific close publication unavailable'))
    group = life.get('group_final')
    if type(group) is dict and type(group.get('terminal')) is list:
        for row in group['terminal']:
            if type(row) is dict and row.get('role') == 'E3' and type(row.get('data')) is dict:
                absent = [k for k in WHOLE_FIELDS if k not in row['data']]
                if absent:
                    gaps.append(_gap('group_final', 'terminal.data is a projection; original whole group FINAL required', missing_fields=absent))
                    break
    docs = dict(life, worker_final=final, task=task)
    metadata = original_byte_provenance if type(original_byte_provenance) is dict else {}
    for alias, document in docs.items():
        if document is not None and alias not in metadata:
            gaps.append(_gap(alias, 'original-byte provenance unavailable', provenance_only=True))
    known_projection = any(x['missing_fields'] for x in gaps)
    if known_projection:
        out['status'] = 'NEEDS_ORIGINAL_WHOLE_ARTIFACTS'
    else:
        method_provenance = dict(schema_reference_id=pure.SOURCE_ID,
            schema_source_pins={k: dict(bytes=v[0], SHA256=v[1]) for k, v in pure.SOURCE_PINS.items()},
            whole_documents=copy.deepcopy(metadata))
        try:
            review = pure.verify_capture(final, task, life, method_provenance)
        except AttributeError as exc:
            # Invalid nested JSON types can be outside the frozen verifier's field guard.
            out['status'] = 'INPUT_SCHEMA_ERROR'
            out['input_error'] = type(exc).__name__ + ': ' + str(exc)
        else:
            out['pure_review'] = review
            out['status'] = review['status']
            out['counts'] = copy.deepcopy(review['counts'])
            out['execution'] = copy.deepcopy(review['execution'])
    review = out['pure_review'] or {}
    checks = {row['check']: row for row in review.get('components', [])}
    for name, check in COMPONENTS.items():
        out['evidence'][name] = copy.deepcopy(checks.get(check, dict(
            check=check, status='UNKNOWN', detail='not evaluated or not retained; no invented zero/PASS')))
    out['retention_and_unknowns'] = [
        'Only retained first2+last2 actuation windows and bounded first32/last32 sensor events/special cap4; not full64/128 controls',
        'Normal MID/END requires original scene_update, reset_depth0 and physics_tick%4==0; reset-internal calls are not normal100Hz',
        'Float32 clean+used-noise(+leg-bias), per-row warmup/sameTick/cache equations are delegated unchanged to the frozen verifier',
        'Decoded numeric consistency is not measured tensor dtype/bitwise proof; original row mapping is SOURCE only',
        'Unretained boundaries, natural terminal links, localDue, private RNG equality, physical readback and full clean35 remain UNKNOWN',
        'Execution value is decoded bounded counters plus published wait closure only, not component success, skill or Stage1/Stage2 admission',
        'V3 reference tuple and the 17 method pins do not establish any V4 identity; no new runtime, wall, resource or audit gate',
    ]
    return out
