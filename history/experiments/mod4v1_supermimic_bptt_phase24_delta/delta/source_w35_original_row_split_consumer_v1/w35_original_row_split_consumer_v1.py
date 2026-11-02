"""One-pass, stdlib-only grading of NEW own W35 original positional row facts.

Does not run an environment, reconstruct tracking predicates, infer standing from
commands, open a checkpoint, or edit the producer. Source-only until the parent
explicitly invokes this on its newly closed own frozen-evaluation case.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import sys

VERSION = 'W35_ORIGINAL_ROW_SPLIT_CONSUMER_V1'
FORMAT = 'mod4.227.lossless_fieldset_positional_jsonl.v1'
TARGET = 'same_UID_original_RM70_command'
DATA_NAME = 'RM70_SAME_UID_COMMAND_AND_ROUTE_FACTS227.positional.jsonl'
SCHEMA_NAME = 'RM70_SAME_UID_COMMAND_AND_ROUTE_SCHEMAS227.json'
SOURCE_PINS = {
    'rm70_intervals227.py': dict(bytes=14185, SHA256='d84182d3675f41d53d35da54c4d80519b9b2280ccb6d3f47f33cfff64029d609', lines='135-170,184-190'),
    'positional_rows227.py': dict(bytes=6557, SHA256='72627c449b8ce071bcf278027ef1f9fe6a32ab7f2d20910e895fb13bf8f3fd29', lines='79-87,99-151'),
}
MAX_LINE = 4 * 1024 ** 2
MAX_METADATA = 8 * 1024 ** 2
MAX_DATA = 192 * 1024 ** 2
IDENTITY = ('env_id', 'episode_uid', 'command_uid', 'same_UID_segment')
SOURCE_UID = ('source_E1_episode', 'original_command_counter')
COUNTERS = ('first_control', 'last_control', 'controls', 'first_physics_tick', 'last_physics_tick')
BOOLS = ('standing', 'start_observed', 'original_kinematic_bounds_met',
         'natural_complete_nonterminal_interval', 'complete_interval_bounds_fact',
         'terminated_before_reset', 'truncated_before_reset')
AUDIT_FIELDS = ('source_SHA',) + IDENTITY + SOURCE_UID + COUNTERS + BOOLS + ('seconds', 'end_reason')


class ConsumerError(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise ConsumerError(message)


def _sha(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _uint(value):
    return type(value) is int and value >= 0


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, 'duplicate JSON key: ' + str(key))
        value[key] = item
    return value


def _native(value):
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        need(math.isfinite(value), 'nonfinite JSON value')
        return
    if type(value) is list:
        for item in value:
            _native(item)
        return
    need(type(value) is dict, 'non-native JSON value')
    for key, item in value.items():
        need(type(key) is str, 'non-string JSON key')
        _native(item)


def _loads(raw):
    def bad(token):
        raise ConsumerError('nonfinite JSON token: ' + token)
    value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=bad)
    _native(value)
    return value


def _encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf8')


def wilson95(n, N):
    """Descriptive interval, not a new skill acceptance threshold."""
    if N == 0:
        return None
    z = 1.959963984540054
    p = n / N
    den = 1 + z * z / N
    mid = (p + z * z / (2 * N)) / den
    half = z * math.sqrt(p * (1 - p) / N + z * z / (4 * N * N)) / den
    return [max(0., mid - half), min(1., mid + half)]


def _registry(header):
    need(type(header) is dict and header.get('format') == FORMAT, 'original positional format differs')
    schemas = header.get('schemas')
    need(type(schemas) is list, 'schemas list missing')
    result = {}
    union = set()
    for expected, schema in enumerate(schemas):
        need(type(schema) is dict and type(schema.get('schema_id')) is int and schema['schema_id'] == expected,
             'schema IDs must be original consecutive integers, not bool')
        fields, positional, constants = (schema.get(k) for k in ('fields', 'positional_fields', 'constants'))
        need(type(fields) is list and all(type(k) is str for k in fields) and fields == sorted(set(fields)), 'schema fields differ')
        need(type(positional) is list and all(type(k) is str for k in positional) and len(set(positional)) == len(positional), 'positional fields differ')
        need(type(constants) is dict and not set(positional).intersection(constants), 'schema constant/position collision')
        need(set(fields) == set(positional).union(constants), 'schema field coverage differs')
        need(positional == [k for k in fields if k not in constants], 'original positional order differs')
        _native(constants)
        result[expected] = (positional, constants)
        union.update(fields)
    need(header.get('field_union') == sorted(union), 'schema field_union differs')
    return result


def _context(case_metadata, expected_role, expected_group_id, expected_source_sha):
    gaps = []
    if type(case_metadata) is not dict:
        return ['case_role_group_source_binding_missing'], None, None
    if case_metadata.get('role') != expected_role:
        gaps.append('case_role_missing_or_differs')
    if case_metadata.get('passed_execution') is not True:
        gaps.append('case_successful_FINAL_missing')
    group = case_metadata.get('group_id')
    if type(group) is not str or not group or (expected_group_id is not None and group != expected_group_id):
        gaps.append('case_group_missing_or_differs')
    cache = case_metadata.get('source_cache')
    if type(cache) is not dict or cache.get('source_SHA') != expected_source_sha:
        gaps.append('case_candidate_source_SHA_missing_or_differs')
    if case_metadata.get('num_envs') != 80 or type(case_metadata.get('num_envs')) is not int:
        gaps.append('case_original_N80_missing_or_differs')
    if case_metadata.get('controls') != 1600 or type(case_metadata.get('controls')) is not int:
        gaps.append('case_original_1600_controls_missing_or_differs')
    facts = case_metadata.get('skill', {}).get('original_RM70_interval_route_facts') if type(case_metadata.get('skill')) is dict else None
    events = facts.get('events') if type(facts) is dict else None
    return gaps, group, events


def _group():
    return dict(observed_target_rows=0, n=0, N=0, false=0, partial=0, unknown=0,
                end_reasons=Counter(), terminated_before_reset_true=0, truncated_before_reset_true=0)


def _row_errors(row, expected_source_sha):
    errors = []
    if row.get('source_SHA') != expected_source_sha:
        errors.append('row_source_SHA_missing_or_differs')
    for key in IDENTITY + COUNTERS:
        if not _uint(row.get(key)):
            errors.append('missing_or_bad_' + key)
    for key in SOURCE_UID:
        # These are original source counters. No invented nonnegative sentinel rule.
        if type(row.get(key)) is not int:
            errors.append('missing_or_bad_' + key)
    for key in BOOLS:
        if type(row.get(key)) is not bool:
            errors.append('missing_or_nonBoolean_' + key)
    if type(row.get('end_reason')) is not str or not row['end_reason']:
        errors.append('missing_or_bad_end_reason')
    seconds = row.get('seconds')
    if type(seconds) not in (int, float) or (type(seconds) is float and not math.isfinite(seconds)) or seconds <= 0:
        errors.append('missing_or_bad_seconds')
    if row.get('not_full_expert_or_signed2pi_cycle_graduation') is not True:
        errors.append('original_restricted_scope_flag_missing_or_differs')
    for key, value in row.items():
        if key.startswith('original_terminal_reason_') and type(value) is not bool:
            errors.append('nonBoolean_' + key)
    if all(_uint(row.get(k)) for k in IDENTITY + COUNTERS):
        if row['env_id'] >= 80:
            errors.append('env_id_outside_original_N80')
        if row['controls'] <= 0 or row['last_control'] < row['first_control'] or row['last_control'] >= 1600:
            errors.append('control_bounds_inconsistent')
        if row['last_physics_tick'] - row['first_physics_tick'] != 8 * row['controls']:
            errors.append('original_8_substep_tick_span_inconsistent')
    if all(type(row.get(k)) is bool for k in BOOLS):
        complete = row['natural_complete_nonterminal_interval']
        kin = row['original_kinematic_bounds_met']
        if row['complete_interval_bounds_fact'] != (complete and kin):
            errors.append('original_complete_and_kin_fact_inconsistent')
        if complete and (not row['start_observed'] or row['terminated_before_reset'] or row['truncated_before_reset']):
            errors.append('original_complete_start_or_terminal_conditions_inconsistent')
        if complete and row.get('end_reason') != 'original_resample':
            errors.append('natural_complete_without_original_resample')
    return errors


def stream_consume(stream, *, schema, expected_role, expected_source_sha, producer=None,
                   case_metadata=None, expected_group_id=None, schema_raw=None, data_basename=None):
    """Consume one binary stream once; never reads paths/checkpoints or closes stream.

    schema is the exact companion header dict, schema_raw its original bytes when
    available. producer is original rows.finish() metadata. case_metadata is the
    newly closed original worker FINAL, not a fabricated role hint. Missing binding
    quarantines rows as unknown. Original Boolean facts, not velocities, grade.
    """
    need(expected_role == 'W35', 'this consumer only grades requested W35')
    need(_sha(expected_source_sha), 'expected candidate source SHA must be lowercase SHA256')
    registry = _registry(schema)
    binding_gaps, group_id, events = _context(case_metadata, expected_role, expected_group_id, expected_source_sha)
    if schema.get('source_model_SHA') != expected_source_sha:
        binding_gaps.append('header_candidate_source_SHA_missing_or_differs')
    if data_basename is not None and schema.get('data_basename') != data_basename:
        binding_gaps.append('header_data_basename_differs')
    header_producer = schema.get('producer_metadata')
    if header_producer is not None:
        need(type(header_producer) is dict, 'header producer_metadata is neither dict nor None')
        if 'role' in header_producer and header_producer['role'] != expected_role:
            binding_gaps.append('header_producer_role_differs')
        if 'group_id' in header_producer and header_producer['group_id'] != group_id:
            binding_gaps.append('header_producer_group_differs')
    groups = {name: _group() for name in ('moving', 'standing', 'unknown_standing')}
    unknown_reasons, ignored, raw_complete, reason_flags = Counter(), Counter(), Counter(), Counter()
    example_errors, seen = [], {}
    data_hash, identity_hash = hashlib.sha256(), hashlib.sha256()
    size = lines = target_rows = decoded_rows = duplicates = 0
    rows_by_schema = [0] * len(registry)
    format_errors = Counter()

    def unknown(name, reasons, line_number, row):
        groups[name]['unknown'] += 1
        unknown_reasons.update(set(reasons))
        if len(example_errors) < 16:
            example_errors.append(dict(line=line_number, reasons=sorted(set(reasons)),
                                       identity={k: row.get(k) for k in ('source_SHA',) + IDENTITY + SOURCE_UID}))

    def remove_contribution(previous):
        name, bucket = previous['group'], previous['bucket']
        if bucket is None:
            return
        g = groups[name]
        if bucket == 'partial':
            g['partial'] -= 1
        else:
            g['N'] -= 1
            g['n' if bucket == 'pass' else 'false'] -= 1
        unknown(name, ['duplicate_UID_invalidates_prior_row'], previous['line'], previous['row'])
        previous['bucket'] = None

    while True:
        raw = stream.readline(MAX_LINE + 1)
        if not raw:
            break
        need(type(raw) is bytes, 'stream must be binary')
        lines += 1
        size += len(raw); data_hash.update(raw)
        too_long = len(raw) > MAX_LINE
        while not raw.endswith(b'\n') and len(raw) == MAX_LINE + 1:
            raw = stream.readline(MAX_LINE + 1)
            if not raw:
                break
            size += len(raw); data_hash.update(raw)
            too_long = True
        need(size <= MAX_DATA, 'data exceeds original 192MiB upper bound; no quota increase')
        if too_long:
            format_errors['line_too_long'] += 1
            unknown('unknown_standing', ['line_too_long'], lines, {})
            continue
        if not raw.endswith(b'\n'):
            format_errors['original_newline_missing'] += 1
        try:
            value = _loads(raw)
            need(type(value) is list and len(value) == 2, 'row is not original [schema_id,values]')
            sid, values = value
            need(type(sid) is int and sid in registry, 'row schema ID unknown or bool')
            positional, constants = registry[sid]
            need(type(values) is list and len(values) == len(positional), 'row positional length differs')
            row = dict(constants); row.update(zip(positional, values))
            rows_by_schema[sid] += 1
            decoded_rows += 1
        except (ValueError, TypeError, UnicodeError) as exc:
            format_errors['malformed_row'] += 1
            unknown('unknown_standing', ['malformed_row:' + type(exc).__name__], lines, {})
            continue
        if row.get('record_type') != TARGET:
            if type(row.get('record_type')) is not str:
                unknown('unknown_standing', ['record_type_missing_or_nonstring'], lines, row)
            else:
                ignored[row['record_type']] += 1
            continue
        target_rows += 1
        standing = row.get('standing')
        name = ('standing' if standing else 'moving') if type(standing) is bool else 'unknown_standing'
        g = groups[name]; g['observed_target_rows'] += 1
        if type(row.get('end_reason')) is str:
            g['end_reasons'][row['end_reason']] += 1
        for key in ('terminated_before_reset', 'truncated_before_reset'):
            if row.get(key) is True:
                g[key + '_true'] += 1
        for key, value in row.items():
            if key.startswith('original_terminal_reason_') and value is True:
                reason_flags[key] += 1
        if type(row.get('natural_complete_nonterminal_interval')) is bool:
            raw_complete[str(row['natural_complete_nonterminal_interval']).lower()] += 1
        identity_hash.update(_encoded({k: row[k] for k in AUDIT_FIELDS if k in row}) + b'\n')
        errors = list(binding_gaps) + _row_errors(row, expected_source_sha)
        key = tuple(row[k] for k in IDENTITY) if all(_uint(row.get(k)) for k in IDENTITY) else None
        # Source-mismatched rows do not acquire a trusted UID identity.
        duplicate = key is not None and row.get('source_SHA') == expected_source_sha and key in seen
        if duplicate:
            duplicates += 1
            remove_contribution(seen[key])
            errors.append('duplicate_UID_row')
        if errors:
            unknown(name, errors, lines, row)
            bucket = None
        elif row['natural_complete_nonterminal_interval']:
            bucket = 'pass' if row['complete_interval_bounds_fact'] else 'false'
            g['N'] += 1; g['n' if bucket == 'pass' else 'false'] += 1
        else:
            bucket = 'partial'; g['partial'] += 1
        if key is not None and row.get('source_SHA') == expected_source_sha and key not in seen:
            seen[key] = dict(group=name, bucket=bucket, line=lines,
                             row={k: row[k] for k in ('source_SHA',) + IDENTITY + SOURCE_UID if k in row})

    actual_sha = data_hash.hexdigest()
    integrity_errors = []
    metadata_gaps = []
    dropped = attempted = None
    if type(producer) is not dict:
        metadata_gaps.append('original_rows_finish_metadata_missing')
    else:
        expected_values = dict(bytes=size, rows=lines, SHA=actual_sha, format=FORMAT,
                               schema_count=len(registry), rows_by_schema=rows_by_schema,
                               field_union=schema['field_union'])
        for key, value in expected_values.items():
            if type(producer.get(key)) is not type(value) or _encoded(producer[key]) != _encoded(value):
                integrity_errors.append('producer_' + key + '_mismatch_or_missing')
        if schema_raw is None:
            metadata_gaps.append('exact_schema_bytes_unavailable')
        else:
            need(type(schema_raw) is bytes and _encoded(_loads(schema_raw)) == _encoded(schema), 'schema_raw does not decode exactly to supplied header')
            for key, value in dict(schema_bytes=len(schema_raw), schema_SHA=hashlib.sha256(schema_raw).hexdigest(),
                                   retained_total_bytes=size + len(schema_raw)).items():
                if type(producer.get(key)) is not type(value) or _encoded(producer[key]) != _encoded(value):
                    integrity_errors.append('producer_' + key + '_mismatch_or_missing')
        dropped, attempted = producer.get('dropped_rows'), producer.get('attempted_rows')
        if not _uint(dropped) or not _uint(attempted) or attempted != lines + dropped:
            integrity_errors.append('producer_attempted_or_dropped_inconsistent')
            dropped = attempted = None
        if type(producer.get('retention_limited')) is not bool:
            metadata_gaps.append('producer_retention_limited_unknown')
        elif dropped is not None and dropped > 0 and producer['retention_limited'] is not True:
            integrity_errors.append('producer_drop_without_retention_limited')
        limit = producer.get('retained_byte_limit')
        if not _uint(limit) or limit <= 0 or limit > MAX_DATA or schema.get('byte_limit') != limit:
            integrity_errors.append('producer_original_byte_limit_invalid')
        elif schema_raw is not None and size + len(schema_raw) > limit:
            integrity_errors.append('retained_data_plus_schema_over_limit')
    unknown_count = sum(g['unknown'] for g in groups.values())
    event_checks = {}
    if type(events) is dict:
        observed = dict(natural_complete_intervals=sum(g['N'] for g in groups.values()),
                        complete_kinematic_bounds_met=sum(g['n'] for g in groups.values()),
                        complete_kinematic_false=sum(g['false'] for g in groups.values()),
                        partial_intervals=sum(g['partial'] for g in groups.values()))
        for key, value in observed.items():
            expected = events.get(key)
            exact = _uint(expected) and expected == value
            event_checks[key] = dict(original=expected, retained_valid_rows=value, equal=exact)
            if dropped == 0 and unknown_count == 0 and not exact:
                integrity_errors.append('original_event_' + key + '_mismatch_or_missing')
    else:
        metadata_gaps.append('original_pooled_events_missing')
    if format_errors:
        integrity_errors.append('original_positional_stream_format_errors')
    verified = (not binding_gaps and not integrity_errors and type(producer) is dict and schema_raw is not None)
    all_original_coverage = (verified and not metadata_gaps and not format_errors and dropped == 0
                             and producer.get('retention_limited') is False and unknown_count == 0)
    for name, g in groups.items():
        rate = (g['n'] / g['N']) if verified and g['N'] else None
        g.update(rate=rate, wilson95=(wilson95(g['n'], g['N']) if verified else None),
                 all_original_complete_population_rate=(rate if all_original_coverage else None),
                 denominator='retained valid same-UID original natural-complete nonterminal intervals',
                 end_reasons=dict(g['end_reasons']))
    return dict(kind=VERSION, role=expected_role, group_id=group_id, source_SHA=expected_source_sha,
                record_type=TARGET, groups=groups,
                grading_integrity_verified=verified,
                all_original_complete_population_coverage_verified=all_original_coverage,
                binding_evidence_gaps=binding_gaps, metadata_evidence_gaps=metadata_gaps,
                integrity_errors=integrity_errors, unknown_reason_counts=dict(unknown_reasons),
                unknown_examples=example_errors, format_error_counts=dict(format_errors),
                dropped_rows=dropped, attempted_rows=attempted, drops_moving_standing_allocation=None,
                raw_rows=dict(bytes=size, SHA256=actual_sha, lines=lines, decoded=decoded_rows,
                              target=target_rows, ignored_record_types=dict(ignored), rows_by_schema=rows_by_schema,
                              original_complete_Boolean_observed=dict(raw_complete)),
                UID_provenance=dict(identity_fields=list(IDENTITY), original_source_counters=list(SOURCE_UID),
                                    unique_source_bound_identity_tuples=len(seen), duplicate_rows=duplicates,
                                    ordered_provenance_SHA256=identity_hash.hexdigest(), no_reset_stitching=True,
                                    missing_UIDs_never_inferred=True),
                original_terminal_reason_true_counts=dict(reason_flags), original_pooled_event_crosschecks=event_checks,
                full_expert_skill_rate=None, relative=None, mother_actual_reference=None,
                no_new_aggregate_graduation_rate=True, velocity_or_MAE_regrading=False,
                standing_from_original_Boolean_only=True, source_python=SOURCE_PINS,
                actual_parent_wait_or_resource_admission_proof=None,
                header_producer_metadata=header_producer,
                interpretation='Conditional original Boolean row facts for this case; not a full expert or paired-effect claim.')


def _read_metadata(path):
    with path.open('rb') as handle:
        raw = handle.read(MAX_METADATA + 1)
    need(len(raw) <= MAX_METADATA, 'metadata exceeds bounded small-file limit')
    return _loads(raw), dict(path=str(path), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest()), raw


def _inside(path, root):
    resolved = Path(path).resolve(strict=True)
    need(resolved.is_relative_to(root) and resolved.is_file(), 'input must be an existing file inside explicit NEW own case-root')
    return resolved


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--case-root', required=True)
    parser.add_argument('--case-final', default=None)
    parser.add_argument('--schema', default=None)
    parser.add_argument('--expected-role', required=True, choices=['W35'])
    parser.add_argument('--expected-source-sha', required=True, help='actual candidate checkpoint SHA from this case, NOT Python source SHA')
    parser.add_argument('--expected-group', required=True)
    parser.add_argument('--output', required=True, help='NEW JSON file; exclusive creation, never overwrite')
    args = parser.parse_args(argv)
    output = Path(args.output).resolve()
    try:
        need(not output.exists(), 'output already exists; choose a NEW output file')
        root = Path(args.case_root).resolve(strict=True)
        need(root.is_dir(), 'explicit own case-root must be a directory')
        final_path = _inside(args.case_final or root / 'FINAL.json', root)
        final, final_receipt, _ = _read_metadata(final_path)
        gaps, _, _ = _context(final, args.expected_role, args.expected_group, args.expected_source_sha)
        need(not gaps, 'case FINAL binding failed: ' + ','.join(gaps))
        facts = final['skill']['original_RM70_interval_route_facts']
        producer = facts['producer']
        need(type(producer) is dict, 'original rows.finish producer receipt missing')
        data_path = _inside(args.input, root)
        schema_path = _inside(args.schema or producer.get('schema_path', ''), root)
        need(data_path == Path(producer.get('path', '')).resolve(strict=True), 'input differs from original producer path')
        need(schema_path == Path(producer.get('schema_path', '')).resolve(strict=True), 'schema differs from original producer path')
        need(output not in (data_path, schema_path, final_path), 'output must not alias an input')
        schema, schema_receipt, schema_raw = _read_metadata(schema_path)
        with data_path.open('rb') as stream:
            before = os.fstat(stream.fileno())
            result = stream_consume(stream, schema=schema, expected_role=args.expected_role,
                                    expected_source_sha=args.expected_source_sha, producer=producer,
                                    case_metadata=final, expected_group_id=args.expected_group,
                                    schema_raw=schema_raw,
                                    data_basename=data_path.name)
            after = os.fstat(stream.fileno())
        # Exact schema bytes are loaded once above; preserve them without a second read.
        result['input_binding'] = dict(case_root=str(root), case_FINAL=final_receipt, schema=schema_receipt,
                                       data_path=str(data_path), data_opens=1, data_hash_passes=1,
                                       expected_group=args.expected_group,
                                       file_unchanged_during_consume=(before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns))
        if not result['input_binding']['file_unchanged_during_consume']:
            result['integrity_errors'].append('input_changed_during_single_pass')
            result['grading_integrity_verified'] = False
            result['all_original_complete_population_coverage_verified'] = False
            for g in result['groups'].values():
                g.update(rate=None, wilson95=None, all_original_complete_population_rate=None)
        output.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        with output.open('x', encoding='utf8', newline='\n') as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        sys.stdout.write(raw)
        return 0 if result['grading_integrity_verified'] else 2
    except (ValueError, TypeError, KeyError, OSError) as exc:
        sys.stderr.write(json.dumps(dict(kind=VERSION, status='input_or_binding_error', error=type(exc).__name__ + ': ' + str(exc)), ensure_ascii=False) + '\n')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
