"""Metadata-only enabled-candidate association. No controller/model/raw imports.
A matching artifact is evidence of association, never a dynamic qualification.
"""
from pathlib import Path
import hashlib
import json


class EvidenceError(ValueError):
    pass


def need(value, reason):
    if not value:
        raise EvidenceError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':'))


def read_small(path):
    p = Path(path)
    need(p.is_file() and p.stat().st_size < 512000, 'missing_or_oversized_small_artifact:' + str(p))
    raw = p.read_bytes()
    def invalid(token):
        raise EvidenceError('nonfinite_json_token:' + token)
    return json.loads(raw, parse_constant=invalid), hashlib.sha256(raw).hexdigest()


def _path(root, value):
    p = Path(value)
    p = (root / p).resolve() if not p.is_absolute() else p.resolve()
    need(p.is_relative_to(root), 'candidate_path_outside_task_root')
    return p


def _records(root, rows):
    need(isinstance(rows, list), 'source_records_must_be_list')
    found = {}
    for row in rows:
        need(isinstance(row, dict) and isinstance(row.get('path'), str), 'invalid_source_record')
        sha = row.get('SHA')
        need(isinstance(sha, str) and len(sha) == 64 and all(c in '0123456789abcdef' for c in sha), 'invalid_source_sha')
        path = Path(row['path'])
        # Other locked dependencies can be in the old authorized project root.
        # Only the three candidate entries are required to be inside task root.
        path = (root / path).resolve() if not path.is_absolute() else path.resolve()
        need(path not in found or found[path] == sha, 'conflicting_duplicate_source_record')
        found[path] = sha
    return found


def validate_case(root, name, expected_config, source_index, spec):
    """Read one saved config/result/manifest; never open trace, meshes or assets.
    spec is itself a source-locked protocol member, not runtime input from a robot.
    All actual CFG fields and numeric representations must match the frozen CFG.
    """
    root = Path(root).resolve()
    need(isinstance(name, str) and Path(name).name == name and name not in ('.', '..'), 'invalid_case_name')
    need(isinstance(expected_config, dict) and expected_config.get('case_id') == name, 'invalid_expected_case')
    hop = expected_config.get('hop')
    need(isinstance(hop, dict) and hop.get(spec['config_feature_key']) is True, 'expected_feature_not_enabled')
    need(hop.get('operator_enable') is True, 'expected_operator_disabled')
    d = root / 'results' / name
    need(not (d / 'ERROR.json').exists(), 'ERROR_present_in_case')
    actual_config, config_sha = read_small(d / 'config.json')
    result, result_sha = read_small(d / 'result.json')
    manifest, manifest_sha = read_small(d / 'SOURCE_MANIFEST.json')
    need(canonical(actual_config) == canonical(expected_config), 'actual_config_not_locked_profile')
    need(isinstance(result, dict) and canonical(result.get('config')) == canonical(expected_config), 'result_config_not_locked_profile')
    need(isinstance(manifest, dict), 'invalid_source_manifest')
    need(result.get('kind') == spec['kind'] and manifest.get('kind') == spec['kind'], 'candidate_kind_mismatch')
    need(result.get(spec['result_feature_field']) is True, 'actual_result_candidate_not_enabled')
    need(manifest.get(spec['manifest_feature_field']) is True, 'manifest_candidate_not_requested')
    locked = _records(root, source_index['files'])
    runtime = _records(root, manifest.get('files'))
    candidate = {}
    for key in ('core_path', 'entry_path', 'data_path'):
        p = _path(root, spec[key])
        need(p in locked, 'candidate_not_in_source_lock:' + key)
        need(runtime.get(p) == locked[p], 'runtime_source_not_locked_candidate:' + key)
        candidate[key] = dict(path=str(p), SHA=locked[p])
    data_sha = candidate['data_path']['SHA']
    need(result.get(spec['data_hash_field']) == data_sha, 'result_endpoint_data_SHA_mismatch')
    need(manifest.get(spec['data_hash_field']) == data_sha, 'manifest_endpoint_data_SHA_mismatch')
    return dict(case=name, config_SHA=config_sha, result_SHA=result_sha,
                source_manifest_SHA=manifest_sha, candidate_sources=candidate,
                status='MATCHES_FROZEN_ENABLED_CANDIDATE_NOT_DYNAMIC_QUALIFICATION')
