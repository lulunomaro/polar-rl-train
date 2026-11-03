"""Source fragment assembled into the NEW runtime, not a native entrypoint.
All model identities below are published metadata strings; no file at those paths
is opened, resolved or statted by these functions.
"""
WORKER_ALIASES = {
    'CURB_PROTECTED878': 'worker_sources/e1/worker_curb878_n80.py',
    'SLOPE135': 'worker_sources/e1/worker_slope135_n80.py',
}
BASELINE_IDENTITIES = {
    'CURB_PROTECTED878': dict(
        source_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000/roles/CURB_PROTECTED878/production/checkpoints/model_BPTT000000_I000000_S0001_complete.pt',
        source_bytes=220144758,
        source_SHA='ae4ac8d31b82c9b7488e7e40419bf2d590be6566822b78a7604e49f848e6bcfe',
        mother_source_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700/roles/CURB_PROTECTED878/production/model_posttrain_final_complete_U020.pt',
        mother_source_bytes=17621306,
        mother_source_SHA='db3d5a6a2a81fb71f6f4e3ca0ee18c09785ddff80b990787960ffc3d8d376d68'),
    'SLOPE135': dict(
        source_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000/roles/SLOPE135/production/checkpoints/model_BPTT000000_I000000_S0001_complete.pt',
        source_bytes=220144758,
        source_SHA='22d7ea42c208256cc5c89980472f72df71d8f279a9bc98f09c1eaa8426f2abe1',
        mother_source_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR3_GENERIC_V2_20261102_131153_1793596313729480700/roles/SLOPE135/production/model_posttrain_final_complete_U020.pt',
        mother_source_bytes=17620922,
        mother_source_SHA='ec5b495691e10bf4ef6587e7fad99df02a18ff48e44f6b70d5170aaa7b641b05'),
}


def validate_seed(seed):
    need(type(seed) is int and seed in ALLOWED_SEEDS, 'only independent holdout seed20260929 or20260930 admitted; historical20260928 is not new evidence')
    return seed


def purpose_for(seed):
    return 'GOOD_EXPERT_HOLDOUT_C878_S135_SEED' + str(validate_seed(seed)) + '_V1'


def holdout_protocol(seed):
    seed = validate_seed(seed)
    return dict(kind='INDEPENDENT_GOOD_EXPERT_HOLDOUT_SEED_PROTOCOL_V1', seed=seed,
        purpose=purpose_for(seed), published_baseline_seed=20260928,
        historical_seed_reassessment_counts_as_new_evidence=False,
        independent_group_per_seed=True, paired_effect_claim=False,
        cohort='original_env_id_mod3_ascending27_descending27_stand26',
        controls_per_role=750, num_envs=80, original_acceptance_unchanged=True)


def current_seed():
    need(CONTEXT and 'task' in CONTEXT, 'one configured holdout task is required before factory/seed use')
    return validate_seed(CONTEXT['task']['seed'])


def _validate_zero_update_baseline(row):
    role = row['role']; need(role in REQUESTED_ROLES, 'only good-expert source containers')
    producer = _producer_descriptor(row.get('a1_producer'), role)
    final = producer['FINAL']; checkpoint = final['checkpoint']; expected = BASELINE_IDENTITIES[role]
    need(final['actual_BPTT_policy_steps'] == 0 and checkpoint.get('iteration') == 0
         and all(type(value) is int and value == 0 for value in final['counts'].values()),
         'baseline is actual0 fullfreshcapture, not a trained SM candidate')
    for key, source_key in (('path', 'source_path'), ('bytes', 'source_bytes'), ('SHA', 'source_SHA')):
        need(checkpoint[key] == expected[source_key], 'published source-container identity differs: ' + key)
    teacher = final['teacher']
    for key in ('source_path', 'source_bytes', 'source_SHA'):
        need(teacher[key] == expected['mother_' + key], 'published original motherteacher identity differs: ' + key)
    need(checkpoint.get('teacher_source') == teacher and row.get('original_bootstrap_teacher') == teacher
         and teacher.get('teacher_frozen') is True, 'source-container/motherteacher identity distinction required')
    return producer


def _validate_e1_execution(final, row):
    seed = validate_seed(row.get('seed'))
    need(final.get('seed') == seed and final.get('holdout_protocol') == row.get('holdout_protocol') == holdout_protocol(seed),
         'actual E1 FINAL seed/independent purpose differs')
    need(final.get('physics') == 6000 and final.get('feedback') == 1500 and final.get('actor_calls') == 750,
         'original E1 physical/control/feedback/actor counts incomplete')
    for key in ('fresh_fullDR_before', 'fresh_fullDR_after'):
        audit = final.get(key)
        need(type(audit) is dict and audit.get('original_seed') == seed
             and audit.get('purpose') == purpose_for(seed) and audit.get('one_explicit_fresh_reset') == 1
             and audit.get('fresh_N80_D0_D7_enabled') is True
             and audit.get('saved20k_history_physically_applied') is False
             and audit.get('new_constructor_nominals_preserved') is True,
             'original fresh N80 seed/D0D7/reset receipt missing: ' + key)
    _absolute_skill(row['role'], final)
    return True


def summarize_independent_seed_results(results):
    """Metadata-only conditional counts, no new acceptance or global quality claim.

    Call only on two externally qualified, actually waited batch FINALs. This
    function creates no wait/admission/native measurement proof of its own.
    """
    import math
    need(type(results) is list and len(results) == 2 and {r.get('seed') for r in results} == set(ALLOWED_SEEDS),
         'exact independent two-seed results required; duplicate seed is not a replicate')
    need(len({r.get('group_id') for r in results}) == 2, 'each seed needs its own independent group')
    def interval(k, n):
        z = 1.959963984540054; p = k / n; a = 1 + z*z/n
        mid = (p + z*z/(2*n)) / a
        half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / a
        return dict(numerator=k, denominator=n, rate=p, wilson95=[max(0., mid-half), min(1., mid+half)])
    for result in results:
        _batch_fields(result)
        need(result.get('kind') == 'ACTUAL_GOOD_EXPERT_HOLDOUT_C878_S135_V1'
             and result.get('all_requested_actual_execution_complete') is True
             and result.get('requested_ready_before_start') is True, 'actually qualified per-seed batch required')
        rows = result.get('rows')
        need(type(rows) is list and len(rows) == 2 and {r.get('role') for r in rows} == set(REQUESTED_ROLES)
             and all(_terminal_success(r) for r in rows), 'actual two waited semantic terminal rows required')
        for row in rows:
            source = row['data']['source_cache']; expected = BASELINE_IDENTITIES[row['role']]
            need(all(source.get(key) == expected[key] for key in ('source_path', 'source_SHA', 'source_bytes'))
                 and source.get('actual_BPTT_policy_steps') == 0
                 and source.get('original_bootstrap_teacher', {}).get('source_SHA') == expected['mother_source_SHA'],
                 'fixed original-teacher baseline identity required for conditional seed aggregation')
            _validate_e1_execution(row['data'], dict(seed=result['seed'], holdout_protocol=result['holdout_protocol'], role=row['role']))
            actual = _absolute_skill(row['role'], row['data'])
            need(actual == result['absolute_original_scope_results'][row['role']], 'per-seed counts differ from original endpoint rows')
            need(row['data']['seed'] == result['seed'] and row['data']['evaluation_purpose'] == result['batch_purpose'], 'cross-seed terminal data')
    summary = {}
    for role in REQUESTED_ROLES:
        stats = [result['absolute_original_scope_results'][role] for result in results]
        by_direction = {}
        for direction in ('ascending', 'descending'):
            denominator = sum(stat[direction]['denominator'] for stat in stats)
            by_direction[direction] = {metric: interval(sum(stat[direction][metric] for stat in stats), denominator)
                                       for metric in ('complete', 'contact_confirmed')}
        by_direction['stand'] = interval(sum(stat['stand']['no_failure'] for stat in stats),
                                         sum(stat['stand']['denominator'] for stat in stats))
        summary[role] = by_direction
    return dict(kind='CONDITIONAL_TWO_SEED_METADATA_SUMMARY_NOT_NEW_NATIVE_PROOF_V1', seeds=list(ALLOWED_SEEDS),
        role_results=summary, seedwise_results=copy.deepcopy(results), pooled_whole_skill_rate=None,
        ninety_percent_whole_skill_claim=None, relative_improvement=None, noninferiority_claim=None,
        seed_independence='protocol_independent_seed_not_IID_or_UID_equivalence_proof',
        intervals='descriptive_Wilson95_per_direction_or_standing_not_simultaneous_or_cluster_adjusted',
        original_thresholds_changed=False, admission_or_wait_proof_created_here=False)
