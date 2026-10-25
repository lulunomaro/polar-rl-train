"""Read saved text metadata only. Never opens remote data or binary/model files."""
import collections
import datetime
import json
import pathlib
import re
import statistics

W = pathlib.Path(r'C:/Users/lulu/Desktop/claude/mjcf')
T = W / 'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
S = W / 'MOD4_REPLAY_WASTE_AUDIT_CLEANUP_AUTHORIZED_20261025' / 'reports'
O = S / 'host72_agent'
O.mkdir(exist_ok=True)

metadata_path = S / 'HOST72_ALL_OWNED_PROJECT_FILE_METADATA.jsonl'
rows = [json.loads(line) for line in metadata_path.open(encoding='utf8')]
by_path = {d['path']: d for d in rows}
replay = [d for d in rows if d['kind'] == 'array_or_replay_candidate_only']
receipt_map = collections.defaultdict(list)
reader_errors = []

def walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)

# These are original completed-transfer receipts, not filename similarity evidence.
receipt_paths = sorted(set(T.glob('**/reports/*FORENSICS*VERIFIED*.json')))
receipt_paths += sorted(set(T.glob('**/reports/*FORENSIC*ACTUAL*.json')) - set(receipt_paths))
receipt_paths += sorted(set(T.glob('**/reports/*VERIFIED*RETAINED*.json')) - set(receipt_paths))
receipt_paths.append(T / 'reports/V96_V3_C38_VERIFIED_DUPLICATE_SPACE_RELEASED_ACTUAL.json')
receipt_paths = sorted(set(receipt_paths))
for file in receipt_paths:
    if file.stat().st_size > 12_000_000:
        continue
    try:
        data = json.loads(file.read_text(encoding='utf8'))
    except Exception as exc:
        reader_errors.append({'path': str(file), 'error': repr(exc)})
        continue
    for item in walk(data):
        target = item.get('target_path')
        source = item.get('path')
        if (isinstance(target, str) and target in by_path
                and isinstance(source, str) and source.endswith('.npz')
                and source != target and item.get('bytes') == by_path[target]['bytes']):
            receipt_map[target].append({
                'source_path': source,
                'original_SHA': item.get('SHA'),
                'receipt': str(file),
                'target_full_SHA_verified_at_original_transfer': item.get('target_full_SHA_verified'),
                'receipt_passed': data.get('passed'),
            })

producer_groups = collections.defaultdict(list)
unmapped_forensic = []
for row in replay:
    p = row['path']
    if '/forensic_originals/' not in p or not re.search(r'/control_prefix_\d+\.npz$', p):
        continue
    maps = receipt_map.get(p, [])
    producers = {m['source_path'].rsplit('/', 1)[0] for m in maps}
    if len(producers) != 1:
        unmapped_forensic.append(row)
        continue
    producer = next(iter(producers))
    enriched = dict(row)
    enriched['producer'] = producer
    enriched['original_transfer_evidence'] = maps
    enriched['sequence_index'] = int(re.search(r'control_prefix_(\d+)\.npz$', p).group(1))
    producer_groups[producer].append(enriched)

proposeddelete, preserve, uncertain, group_reports = [], [], [], []
closed_source_files = []
for file in sorted(T.glob('*/reports/PAIR_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json')):
    data = json.loads(file.read_text(encoding='utf8'))
    hs = data.get('cohort', {}).get('rows', {}).get('h1', {})
    final_path = (hs.get('latest_save') or {}).get('path')
    if final_path:
        closed_source_files.append((final_path.split('/job0/')[0], str(file), hs.get('actual_exit'), hs.get('original_error')))

old_closed_receipts = [
    W / 'MOD4_UNIFIED_THREE_SLOT_H1_E2_E3_HANDOFF_20261017/reports/HUMAN_NETWORK_RESTORED_SOURCE210_EXISTING_FINALS_BOUND_ACTUAL.json',
    W / 'MOD4_THREE_EXPERTS_RECOVERED_FULL_FINAL_CONTINUATION_20261017/reports/WINDOW_V2_THREE_FINALS_EXISTING_FULLSAVE_COST_EXIT_ORIGINAL_HANDOFF_COLLECTION_ACTUAL.json',
    W / 'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017/reports/M_CLOSED24_H1_FINAL_RECOVERY85_NATIVE_COMPLETE_ORIGINAL_HANDOFF_1657_BOUND_ACTUAL.json',
]
for file in old_closed_receipts:
    data = json.loads(file.read_text(encoding='utf8'))
    for item in walk(data):
        latest = item.get('latest_save')
        actual_exit = item.get('actual_exit')
        if not isinstance(latest, dict) or not isinstance(actual_exit, dict):
            continue
        final_path = latest.get('path')
        if final_path and actual_exit.get('actual_waited'):
            entry = (final_path.split('/job0/')[0], str(file), actual_exit, item.get('original_error'))
            if entry not in closed_source_files:
                closed_source_files.append(entry)

def close_evidence(producer):
    result = []
    for prefix, file, actual_exit, original_error in closed_source_files:
        if producer.startswith(prefix + '/'):
            result.append({'path': file, 'actual_exit': actual_exit, 'original_error': original_error})
    return result

for producer, items in sorted(producer_groups.items()):
    closure = close_evidence(producer)
    indices = sorted({d['sequence_index'] for d in items})
    # Current recent diagnostic originals and all already-minimal sets stay intact.
    protected_current = any('CURRENT65_' in d['path'] or 'CURRENT67_' in d['path'] for d in items)
    if protected_current or len(indices) <= 4:
        for d in items:
            d['decision_reason'] = 'current65_or67_diagnostic_original' if protected_current else 'already_minimal_first_last_anomaly_evidence'
            preserve.append(d)
        group_reports.append({'producer': producer, 'files': len(items), 'indices': indices, 'status': 'preserve_current_or_minimal', 'closure': closure})
        continue
    # Only use a proved closed producer for first-pass actionable pruning.
    if not closure:
        for d in items:
            d['decision_reason'] = 'producer_transfer_identified_but_local_closure_not_yet_resolved'
            uncertain.append(d)
        group_reports.append({'producer': producer, 'files': len(items), 'indices': indices, 'status': 'uncertain_closure', 'closure': []})
        continue
    # First, last, and the shortest unusual internal fragment represent history.
    retain_indices = {indices[0], indices[-1]}
    med = statistics.median(d['bytes'] for d in items)
    internal = [d for d in items if d['sequence_index'] not in retain_indices]
    if internal:
        shortest = min(internal, key=lambda d: (d['bytes'], d['sequence_index'], d['path']))
        if shortest['bytes'] < 0.95 * med:
            retain_indices.add(shortest['sequence_index'])
    # Distinct producer paths NEVER merged merely because filenames/bytes match.
    for d in items:
        d['closure_evidence'] = closure
        if d['sequence_index'] in retain_indices:
            d['decision_reason'] = 'producer_first_last_or_short_fragment_anomaly_representative'
            preserve.append(d)
        else:
            d['decision_reason'] = 'closed_superseded_producer_unused_middle_replay_new_explicit_lower_threshold'
            proposeddelete.append(d)
    group_reports.append({'producer': producer, 'files': len(items), 'distinct_indices': len(indices), 'first_index': indices[0], 'last_index': indices[-1], 'retained_indices': sorted(retain_indices), 'proposeddelete_files': sum(d['sequence_index'] not in retain_indices for d in items), 'closure': closure, 'status': 'proposeddelete_unused_middle'})

handled = {d['path'] for d in proposeddelete + preserve + uncertain}
for d in replay:
    if d['path'] in handled:
        continue
    x = dict(d)
    if 'CURRENT65_' in d['path'] or 'CURRENT67_' in d['path']:
        x['decision_reason'] = 'current65_or67_diagnostic_original'
        preserve.append(x)
    elif '/forensic_originals/' in d['path'] and 'control_prefix_' in d['path'] and 'MINIMAL_V4/' in d['path']:
        x['decision_reason'] = 'already_minimal_one_to_three_representative_per_old_producer_preserve'
        preserve.append(x)
    elif '/forensic_originals/' in d['path'] and 'control_prefix_' in d['path']:
        x['decision_reason'] = 'original_transfer_producer_mapping_not_yet_resolved'
        uncertain.append(x)
    else:
        x['decision_reason'] = 'native_query_fixture_or_unreviewed_training_array_or_small_derived_preserve_in_this_proposal'
        preserve.append(x)

# Root owns V1 exact unlink. This is an additive manifest, never retries V1 paths.
prior_file = O / 'EXACT_72_REPLAY_CLEANUP_PROPOSAL_ACTUAL.json'
prior = json.loads(prior_file.read_text(encoding='utf8'))
prior_selected = {d['path'] for d in prior['proposeddelete']}
previous_proposal_rows = [d for d in proposeddelete if d['path'] in prior_selected]
proposeddelete = [d for d in proposeddelete if d['path'] not in prior_selected]

def totals(items):
    ids = {}
    selected_counts = collections.Counter((d['device'], d['inode']) for d in items)
    for d in items:
        ids[(d['device'], d['inode'])] = d
    guaranteed = sum(d['allocated_bytes'] for key, d in ids.items() if selected_counts[key] >= d['nlink'])
    return {'files': len(items), 'logical_bytes': sum(d['bytes'] for d in items), 'unique_allocated_bytes': sum(d['allocated_bytes'] for d in ids.values()), 'allocated_reclaimable_if_snapshot_unchanged_and_all_selected_unlinked': guaranteed, 'linked_inodes_not_fully_selected': sum(selected_counts[k] < d['nlink'] for k, d in ids.items())}

out = {
    'schema': 'MOD4_EXACT_REPLAY_CLEANUP_PROPOSAL_V1',
    'host': '72',
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'READ_ONLY_PROPOSAL_NO_DELETE',
    'incremental_to': str(prior_file),
    'previous_506_proposed_paths_excluded_from_this_proposeddelete': True,
    'inputs': [str(metadata_path), str(S / 'HOST72_NEW_REPLAY_STORAGE_METADATA_ACTUAL.json'), str(S / 'CURRENT_DEPENDENCY_PROTECTION_BASELINE_ACTUAL.json'), str(S / 'HUMAN_LOWER_REPLAY_DELETION_THRESHOLD_AND_THREE_SOL_XHIGH_AGENTS_ACTUAL.json')],
    'metadata_only_binary_contents_never_opened': True,
    'fresh_metadata_existence_is_authority_original_indices_are_historical_only': True,
    'SHA_status': 'original_transfer_SHA_only_not_new_current_hash',
    'producer_identity_method': 'original_transfer_receipt_source_path_and_target_path_plus_fresh_target_bytes; no merge across different producer source paths',
    'all_text_models_optimizer_FINAL_player_assets_Git_native_query_fixtures_preserved': True,
    'current65_current67_jump_and_current_collision_diagnostics_preserved': True,
    'retention_policy': 'joint all surviving directories by original producer; preserve first and last and shortest unusual internal fragment; preserve already-minimal sets',
    'fresh_execution_requirements': ['root performs exact lstat equality of bytes/device/inode/nlink/mtime_ns before unlink', 'root confirms no selected file is open by active owned process', 'no recursive directory deletion; unlink exact listed regular files only', 'new errors and actual receipts must be appended and Git archived by root'],
    'summary': {'proposeddelete': totals(proposeddelete), 'preserve': totals(preserve), 'uncertain': totals(uncertain)},
    'producer_groups': group_reports,
    'proposeddelete': proposeddelete,
    'previous_proposal_rows_reference_only_not_delete_targets': previous_proposal_rows,
    'preserve': preserve,
    'uncertain': uncertain,
    'reader_errors': reader_errors,
    'archive_status': 'pending_root_unique_stage_Git_archive',
}
file = O / 'EXACT_72_REPLAY_CLEANUP_PROPOSAL_V2_INCREMENTAL_ACTUAL.json'
file.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'output': str(file), 'summary': out['summary'], 'groups': group_reports, 'receipt_files_read': len(receipt_paths), 'reader_errors': reader_errors}, ensure_ascii=False, indent=2))
