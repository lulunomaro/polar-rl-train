"""Admission binding: exact frozen evidence, gate source and full checkpoint."""
def validate(evidence,flat,actual_source,mature,gate_version,gate_sha,adjudication):
    assert evidence['ledger_bytes_exact']
    assert evidence['complete_15s_two_seed_profile_pairs'] and evidence['hook_and_original_behavior_exact']
    assert evidence['prospective_gate_version']==gate_version and evidence['gate_source_sha256']==gate_sha
    assert len(evidence['rows'])==9
    primary=[r for r in evidence['rows'] if r['case'].split('_')[0] in ('latest6','mature5')]
    assert len(primary)==8 and all(r['contact_gate'] for r in primary),'Current and paired-mature conditions must all pass'
    cross=[r for r in evidence['rows'] if r['case'].startswith('passed6')]
    assert len(cross)==1 and cross[0]['contact_gate']==adjudication['prior17773_new_gate_pass']
    assert adjudication['accept_measurement_for_bounded_latest6_trial'] and adjudication['prior17773_not_used_as_new_gate_qualifier']
    assert adjudication['no_numeric_or_measurement_change_after_results'] and adjudication['registered_source_roles_retained']
    assert adjudication['gate_source_sha256']==gate_sha
    expected={(source,seed,profile) for source in ('latest6','mature5') for seed in (20261002,20261003) for profile in ('nominal','white_v2')}
    actual={(r['case'].split('_')[0],r['seed'],r['profile']) for r in evidence['rows'] if not r['case'].startswith('passed6')}
    assert actual==expected,'Missing preregistered seed/profile/source condition'
    assert flat['all_original_flat_pass'] and flat['initial_root_q_pair_exact'] and flat['ledger_bytes_exact']
    assert len(flat['results'])==4 and all(v['pass_'] and v['actual_parameters_pass'] for v in flat['results'].values())
    assert actual_source==flat['source']==evidence['source_selection']['latest6']
    assert actual_source['finite_tensors']==68
    assert mature==dict(checkpoint=evidence['source_selection']['mature5']['path'],cap=5.,profile='white_v2')
    return True
