"""Stdlib-only immutable core seal and exact source/metadata manifest."""
from pathlib import Path
import hashlib
import json
import traceback

HERE = Path(__file__).resolve().parent
EXPECTED = '2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039'


def digest(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def run():
    core = digest(HERE / 'ctx_reward_learner.py')
    assert core['sha256'] == EXPECTED
    parent_snapshots = []
    for name in ('native_supermimic_bridge.py', 'worker_supermimic_bptt.py'):
        source = HERE.parent / 'source_runtime' / name
        before = source.stat()
        data = source.read_bytes()
        after = source.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'parent source changed while reading'
        destination = HERE / 'evidence' / ('parent_readonly_' + name)
        with destination.open('xb') as stream:
            stream.write(data)
        parent_snapshots.append(dict(original=str(source), snapshot=str(destination),
                                     bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                                     mutable_parent_snapshot_not_pack_identity=True))
    seal = dict(scope='SOURCE_ONLY', core=core, sealed=True, further_core_edits=False,
                validation='28 AST/stdlib checks PASS; no local torch/runtime/SDK test',
                parent_readonly_snapshots=parent_snapshots)
    with (HERE / 'SEAL.json').open('x', encoding='utf-8') as stream:
        json.dump(seal, stream, indent=2, ensure_ascii=False)
    names = ['ctx_reward_learner.py', 'teacher_residual.py', 'validate_source.py',
             'seal_source.py', 'ADAPTER_INTERFACE.md', 'SOURCE_REVIEW.md',
             'SOURCE_OPERATION_LOG.json', 'ERRATUM_PARENT_INTERFACE_READONLY.md',
             'VALIDATION.json', 'VALIDATION_RUN1.json', 'VALIDATION_CONSOLE.txt',
             'VALIDATION_RUN1_CONSOLE.txt', 'VALIDATION_RUN2_CONSOLE.txt',
             'stdlib_ledger_test_receipts.jsonl', 'SEAL.json']
    names += ['evidence/' + name for name in (
        'learner.py', 'networks.py', 'replay.py', 'geometry.py', 'contract.py',
        'frozen_e0.py', 'isaac_bridge.py', 'lqr_reference_mdp.py', 'step_env.py',
        'train_supermimic.py', 'h1_fullstate_checkpoint_v1.EMPTY.py',
        'parent_readonly_native_supermimic_bridge.py', 'parent_readonly_worker_supermimic_bptt.py')]
    manifest = dict(scope='SOURCE_ONLY', core_sealed_sha256=EXPECTED,
                    files=[digest(HERE / name) for name in names])
    with (HERE / 'MANIFEST.json').open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, indent=2, ensure_ascii=False)
    print(json.dumps(dict(sealed=core, manifest_entries=len(manifest['files']), scope='SOURCE_ONLY')))


if __name__ == '__main__':
    try:
        run()
    except BaseException:
        with (HERE / 'SEAL_FAILURE.txt').open('a', encoding='utf-8') as stream:
            stream.write(traceback.format_exc())
        raise
