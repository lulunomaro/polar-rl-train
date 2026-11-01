CANONICAL = '/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
GENERATION = 'MOD4_SINGLE_WRITER72_20261026'
KNOWN235_RUN = 'E2_B3AE_WORLD_MIMIC01_PPO235V4_20261101_0937'

def validate_authority(c, binding, owner_identity=None, owner_current=None, process_fact=None, closed=None):
    assert c['authority_generation'] == GENERATION and c['authorized_training_seconds'] == 2268000 and (c['new_authority_budget_extensions'] == [])
    assert binding['kind'] == 'KNOWN_ACTIVE235_EXACT_ORIGINAL_E2_SOLO_AUTHORITY_BINDING' and binding['run_id'] == KNOWN235_RUN
    owner = binding['owner']
    assert owner['pid'] == 1014881 and owner['creation'] == 1793496943.07 and (owner['cwd'] == '/home/lc01/Zonglin Li/zonglin2')
    assert owner_identity['pid'] == owner['pid'] and owner_identity['creation'] == owner['creation']
    assert owner_current['go'] == binding['go'] and set(binding['go']) == {'e2'}
    if c['active_segment'] is not None:
        assert c['active_segment']['owner_parent_pid'] == owner['pid'] and process_fact['running']
        for k in ('pid', 'creation', 'exe', 'argv', 'cwd'):
            assert process_fact[k] == owner[k], k
        return dict(mode='FRESH_EXACT235_ACTIVE', active_GPU_UUID=binding['go']['e2']['GPU_UUID'], run_id=binding['run_id'], owner=owner)
    assert closed and closed['cohort_final']['go'] == binding['go'] and closed['cohort_final']['original_cost_settled'] and closed['owner_exit']['original_cost_settled'] and closed['owner_exit']['own_original_two_fcntl_released_if_held']
    assert not process_fact['running'] and all((x['terminal_all_own_children_waited'] for x in closed['cohort_final']['rows'].values()))
    return dict(mode='FRESH_CNONE_AFTER_MATCHING235_CLOSED', active_GPU_UUID=None, run_id=binding['run_id'], owner=owner)
