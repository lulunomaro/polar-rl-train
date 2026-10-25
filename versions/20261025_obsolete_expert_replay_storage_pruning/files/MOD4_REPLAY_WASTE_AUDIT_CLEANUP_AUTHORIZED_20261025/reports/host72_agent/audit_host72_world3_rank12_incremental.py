"""Saved local JSON only: add closed WORLD3 rank1/rank2 middle replays."""
import collections
import datetime
import json
import pathlib
import statistics

W = pathlib.Path(r'C:/Users/lulu/Desktop/claude/mjcf')
S = W / 'MOD4_REPLAY_WASTE_AUDIT_CLEANUP_AUTHORIZED_20261025/reports'
O = S / 'host72_agent'
P = W / 'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016'
F = P / 'final878_actual'

def read(p):
    return json.loads(p.read_text(encoding='utf8'))

closure_file = F / 'source210/THREE_RANK_FINAL_ACTUAL.json'
owner_file = F / 'source210/OWNER_EXIT_ACTUAL.json'
node_file = F / 'target72/NODE72_AGENT_EXIT_ACTUAL.json'
closure, owner, node = map(read, (closure_file, owner_file, node_file))
assert closure['complete'] and closure['unique_original_cost_settled']
assert all(x['returncode'] == 0 and x['worker'] is None for x in closure['rows'])
assert owner['own_locks_released'] and owner['canonical_active_settled']
assert all(x['returncode'] == 0 and x['worker'] is None for x in node['rows'])

raw_metadata = [json.loads(x) for x in (S / 'HOST72_ALL_OWNED_PROJECT_FILE_METADATA.jsonl').open(encoding='utf8')]
by_path = {x['path']: x for x in raw_metadata}
prior_files = [O / 'EXACT_72_REPLAY_CLEANUP_PROPOSAL_ACTUAL.json', O / 'EXACT_72_REPLAY_CLEANUP_PROPOSAL_V2_INCREMENTAL_ACTUAL.json']
prior_paths = {x['path'] for f in prior_files for x in read(f)['proposeddelete']}
proposeddelete, preserve, uncertain, groups, errors = [], [], [], [], []
for rank in (1, 2):
    receipt_file = F / f'target72/rank{rank}/RETENTION_COMMAND_ACTUAL.json'
    receipt = read(receipt_file)
    assert receipt['actual_controls'] == 21192
    assert receipt['pre_reset_roots_no_teleport']
    trace = sorted(receipt['trace_files'], key=lambda x: (x['first'], x['last'], x['path']))
    actual = []
    for history in trace:
        p = history['path']
        fresh = by_path.get(p)
        if fresh is None or fresh['bytes'] != history['bytes']:
            errors.append({'path': p, 'reason': 'saved_metadata_missing_or_bytes_differ_from_original_trace_receipt'})
            continue
        assert f'/rank{rank}/' in p and f'rank{rank}_retention_prefix_' in p
        entry = dict(fresh)
        entry.update({
            'producer': f'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/rank{rank}/retention_command',
            'rank': rank,
            'control_first': history['first'],
            'control_last_exclusive': history['last'],
            'original_SHA': history.get('sha256'),
            'original_trace_index_receipt': str(receipt_file),
            'original_SHA_is_historical_not_newly_hashed': True,
            'closure_evidence': [str(closure_file), str(owner_file), str(node_file)],
            'obsolescence_evidence': [str(S / 'CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json'), str(S / 'HUMAN_LOWER_REPLAY_DELETION_THRESHOLD_AND_THREE_SOL_XHIGH_AGENTS_ACTUAL.json')],
        })
        actual.append(entry)
    assert len(actual) == len(trace), errors
    # Rank streams are distinct producers despite shared PPO parameters.
    keep_paths = {actual[0]['path'], actual[-1]['path']}
    internal = actual[1:-1]
    short = min(internal, key=lambda x: (x['bytes'], x['control_first']))
    if short['bytes'] < .95 * statistics.median(x['bytes'] for x in actual):
        keep_paths.add(short['path'])
    for entry in actual:
        assert entry['path'] not in prior_paths
        if entry['path'] in keep_paths:
            entry['decision_reason'] = 'first_last_or_short_initial_24_control_fragment_representative'
            preserve.append(entry)
        else:
            entry['decision_reason'] = 'closed_WORLD3_final878_retired_old_E1_route_unused_middle_command_replay'
            proposeddelete.append(entry)
    # Exact numerical native fixtures remain intact.
    native = [dict(x, decision_reason='native_physical_numerical_fixture_preserve') for x in raw_metadata
              if f'/tasks/MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/rank{rank}/' in x['path']
              and pathlib.PurePosixPath(x['path']).name.startswith('native_physical_controls_')]
    preserve.extend(native)
    groups.append({'rank': rank, 'trace_files': len(actual), 'proposeddelete_files': sum(x['path'] not in keep_paths for x in actual), 'retained_control_intervals': [[x['control_first'], x['control_last_exclusive']] for x in actual if x['path'] in keep_paths], 'native_fixture_files_preserved': len(native), 'current_actor_or_optimizer_source': False})

def totals(rows):
    ids = {(x['device'], x['inode']): x for x in rows}
    counts = collections.Counter((x['device'], x['inode']) for x in rows)
    return {'files': len(rows), 'logical_bytes': sum(x['bytes'] for x in rows), 'unique_allocated_bytes': sum(x['allocated_bytes'] for x in ids.values()), 'allocated_reclaimable_if_snapshot_unchanged_and_all_selected_unlinked': sum(x['allocated_bytes'] for k, x in ids.items() if counts[k] >= x['nlink']), 'linked_inodes_not_fully_selected': sum(counts[k] < x['nlink'] for k, x in ids.items())}

out = {
    'schema': 'MOD4_EXACT_REPLAY_CLEANUP_PROPOSAL_V3_INCREMENTAL',
    'host': '72',
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'READ_ONLY_PROPOSAL_NO_DELETE',
    'incremental_to': [str(x) for x in prior_files],
    'overlap_prior_649_paths': len(prior_paths & {x['path'] for x in proposeddelete}),
    'scope': 'Only original retired WORLD3 final878 rank1/rank2 command-retention middle replay; native physical fixtures preserved.',
    'inputs': [str(S / 'HOST72_ALL_OWNED_PROJECT_FILE_METADATA.jsonl'), str(closure_file), str(owner_file), str(node_file), str(S / 'CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json')],
    'closure_actual': {'three_rank_complete': closure['complete'], 'returncodes': [x['returncode'] for x in closure['rows']], 'unique_original_cost_settled': closure['unique_original_cost_settled'], 'owner_exit': owner, 'target72_returncodes': [x['returncode'] for x in node['rows']]},
    'retention_policy': 'By independent rank producer across root and logs subdirectory: first interval0-120 plus last21120-21192 plus unusual initial24-control interval120-144. Keep all native_physical_controls exact fixtures, every text/report/log/code and model.',
    'no_raw_contents_or_model_load_or_hash_or_remote_connection_or_delete': True,
    'SHA_status': 'Original retained-command report SHA only, fresh existence and bytes from saved metadata; executor must revalidate inode/device/nlink/bytes/mtime_ns.',
    'summary': {'proposeddelete': totals(proposeddelete), 'preserve': totals(preserve), 'uncertain': totals(uncertain)},
    'producer_groups': groups,
    'proposeddelete': proposeddelete,
    'preserve': preserve,
    'uncertain': uncertain,
    'reader_errors': errors,
    'archive_status': 'pending_root_unique_stage_Git_archive',
}
path = O / 'EXACT_72_REPLAY_CLEANUP_PROPOSAL_V3_INCREMENTAL_WORLD3_ACTUAL.json'
path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'path': str(path), 'summary': out['summary'], 'groups': groups, 'overlap_prior_649_paths': out['overlap_prior_649_paths'], 'errors': errors}, ensure_ascii=False, indent=2))
