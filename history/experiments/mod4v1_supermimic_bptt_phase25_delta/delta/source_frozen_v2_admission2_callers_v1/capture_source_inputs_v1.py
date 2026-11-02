"""Capture explicit small local source/metadata only. No caller is imported/run."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE.parent
S = HERE / '_SOURCE_INPUT'
FILES = [
    'upload_preflight_frozen_e3_w35_microbatch_v2_once.py',
    'stage_frozen_e3_w35_microbatch_v2_after_preflight_once.py',
    'dispatch_frozen_e3_w35_microbatch_v2_original_parent_once.py',
    'collect_frozen_e3_w35_microbatch_v2_metadata_once.py',
    'source_stage_a1_microbatch_eval_v2/stage_a1_microbatch_eval_v2.py',
    'payload_frozen_microbatch_v2/MICROBATCH_STAGE_INDEX_V2.json',
    'reports/FROZEN_MICROBATCH14_LOCAL_SOURCE_PAYLOAD_V2.json',
    'reports/ACTUAL_FROZEN_E3_W35_BATCH_V2_20261103_012611/CLOSED_RESULT.json',
    'observe_frozen_v2_resources_after_zero_admission_timeout_once.py',
]

def H(raw): return hashlib.sha256(raw).hexdigest()

def read_small(path):
    assert path.suffix in ('.py', '.json')
    raw = path.read_bytes(); assert len(raw) <= 262144
    return raw


def main():
    assert not (S / 'INPUT_PINS.json').exists()
    records = []
    for relative in FILES:
        path = R / relative; raw = read_small(path)
        target = S / relative; target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream: stream.write(raw)
        records.append(dict(relative=relative, original_path=str(path), bytes=len(raw), SHA256=H(raw)))
    manifest = json.loads((R / FILES[6]).read_bytes())
    index = json.loads((R / FILES[5]).read_bytes())
    assert len(manifest['files']) == len(index['entries']) == 14
    observed = []
    for row in manifest['files']:
        relative = row['file']; assert relative.startswith('source/') and '..' not in relative and '\\' not in relative
        path = R / 'payload_frozen_microbatch_v2' / relative; raw = read_small(path)
        assert (len(raw), H(raw)) == (row['bytes'], row['SHA'])
        ix = [e for e in index['entries'] if e['relative'] == row['installed_alias']]
        assert len(ix) == 1 and (ix[0]['bytes'], ix[0]['SHA256']) == (len(raw), H(raw))
        observed.append(dict(path=str(path), bytes=len(raw), SHA256=H(raw), installed_alias=row['installed_alias']))
    result = dict(kind='EXPLICIT_SOURCE_METADATA_ONLY_SNAPSHOT_ADMISSION2_V1', project_root=str(R),
        files=records, original_four_templates_edited=False, verified_unchanged_payload14=observed,
        SSH_SDK_GPU_PT_raw_C_locks_Git_parent_or_caller_operations=0)
    with (S / 'INPUT_PINS.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps(dict(passed=True, snapshot_files=len(records), payload_PINS_verified=len(observed),
                         source_only=True, caller_executions=0), indent=2))


if __name__ == '__main__': main()
