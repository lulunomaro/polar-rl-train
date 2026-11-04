"""Run only five NEW SOURCE checks and export four NEW files; no fixture import/call."""
from pathlib import Path
import hashlib
import io
import json
import os
import platform
import sys
import unittest

HERE = Path(__file__).resolve().parent
BASE = ['README.md','typed_c2_cpu_fixture.py','test_source_only.py','seal_source.py']
OUTPUTS = ['SOURCE_PINS.json','SOURCE_TEST_LOG.txt','SOURCE_RECEIPT.json','SOURCE_SEAL.json']
FORBIDDEN = ('torch','numpy','isaacsim','isaaclab','omni','pxr','warp','psutil','paramiko')
AUDIT = dict(native_or_Torch_imports=0, model_raw_asset_opens=0, subprocesses=0, network=0,
             locks_or_canonical_opens=0, escaped_writes=0, deletes_moves_mkdirs=0)
FS = dict(read_opens=0, NEW_artifact_write_opens=0)


def audit(event, args):
    if event == 'import' and args and str(args[0]).split('.')[0] in FORBIDDEN:
        AUDIT['native_or_Torch_imports'] += 1
        raise RuntimeError('SOURCE check blocks Torch/native import')
    if event in ('subprocess.Popen','os.system','os.spawn','os.exec'):
        AUDIT['subprocesses'] += 1
        raise RuntimeError('SOURCE check blocks target/CLI subprocesses')
    if event.startswith('socket.'):
        AUDIT['network'] += 1
        raise RuntimeError('SOURCE check blocks network')
    if event in ('msvcrt.locking','fcntl.flock','fcntl.lockf'):
        AUDIT['locks_or_canonical_opens'] += 1
        raise RuntimeError('SOURCE check blocks locking')
    if event in ('os.remove','os.rename','os.replace','os.rmdir','os.mkdir'):
        AUDIT['deletes_moves_mkdirs'] += 1
        raise RuntimeError('SOURCE check blocks delete/move/mkdir')
    if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).resolve()
        if path.suffix.lower() in ('.pt','.pth','.ckpt','.safetensors','.raw','.bin','.npy','.npz','.pkl','.usd'):
            AUDIT['model_raw_asset_opens'] += 1
            raise RuntimeError('SOURCE check blocks model/raw/assets')
        if path.suffix.lower() == '.lock' or path.name.lower() == 'training_budget_10h.json':
            AUDIT['locks_or_canonical_opens'] += 1
            raise RuntimeError('SOURCE check blocks canonical/lock paths')
        mode, flags = args[1], args[2]
        writing = (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
        if writing:
            if path.parent != HERE or path.name not in OUTPUTS:
                AUDIT['escaped_writes'] += 1
                raise RuntimeError('SOURCE check blocks write outside four NEW outputs')
            FS['NEW_artifact_write_opens'] += 1
        else: FS['read_opens'] += 1


def export(name, value):
    text = value if type(value) is str else json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+'\n'
    with (HERE/name).open('x', encoding='utf-8', newline='\n') as stream: stream.write(text)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',',':'), allow_nan=False).encode()


def main():
    assert sys.version_info[:2] == (3,14) and sys.dont_write_bytecode
    assert not any((HERE/name).exists() for name in OUTPUTS), 'One-shot outputs already frozen/present'
    sys.addaudithook(audit)
    import test_source_only as checks
    before = {name:checks.identity(HERE/name) for name in BASE}
    pins = checks.build_pins()
    export('SOURCE_PINS.json', pins)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(checks))
    after = checks.build_pins()
    loaded = sorted(n for n in sys.modules if n.split('.')[0] in FORBIDDEN)
    assert result.wasSuccessful() and result.testsRun == 5, stream.getvalue()
    assert not loaded and not any(AUDIT.values()) and before == {name:checks.identity(HERE/name) for name in BASE}
    assert pins == after
    export('SOURCE_TEST_LOG.txt', 'ONLY FIVE NEW AST/COMPILE/PINS TESTS; NO FIXTURE IMPORT/CALL, TORCH, OLD SUITE OR CPU EXECUTION\n'+stream.getvalue())
    receipt = dict(kind='TYPED_C2_CPU_FIXTURE_SOURCE_RECEIPT_V1', source_only=True, python=platform.python_version(), minus_B=True,
        capability_selection='catalog Office/ACL has no RL match; FS and existing Python314 stdlib',
        SOURCE_tests=dict(ran=result.testsRun, failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped), successful=result.wasSuccessful()),
        fixture_lines=len((HERE/'typed_c2_cpu_fixture.py').read_text(encoding='utf-8').splitlines()),
        injection_API='run_fixture(torch_module, PhysicsActionQueue, actuation_module, codec_module, observer_module, field_module)',
        full_runtime_files_pinned=6, readonly_upstream_seals=4, own_and_upstream_before_after_unchanged=True,
        design_references_used='full359 and full94 SOURCE read only; neither imported nor called',
        actual_run_fixture_calls=0, actual_Torch_imports=0, actual_real_tensors_created=0,
        actual_Queue_C2_codec_observer_or_Field_runtime_calls=0, actual_private_or_global_RNG_reads=0,
        actual_CPU_executions=0, actual_SDK_native_GPU_calls=0, actual_PT_raw_reads=0, actual_SSH=0,
        actual_original_CLI_main=0, actual_resource_EX_or_canonical_operations=0, actual_stage_dispatch=0,
        actual_old_tests_rerun=0, actual_old_source_edits=0, actual_reports_read=0, actual_Git=0,
        actual_CPU_passed=None, actual_controls=None, actual_retained_windows=None, actual_event_counts=None,
        actual_assertions_evaluated=None, actual_RNG_parity=None, actual_adoption_identity=None, actual_serde_result=None,
        planned=dict(n=80,controls=64,ticks=512,lag_legs=2,lag_wheels=1,own_partial_reset_ids=[78,79],retained_controls=[0,1,62,63]),
        unparented_setter_numeric_values='UNKNOWN_INTENTIONALLY_NOT_REPRESENTED_BY_FOUR_PUBLISHED_ROLES',
        unparented_scope='raw owned numeric payload kept in original event memory; typed keys/source/shape/dtype/device/scope/tick only; NOT numeric JSON preservation',
        JOINT_ID_role='METADATA_ONLY_UNKNOWN_NOT_ENV_IDS_FULL',
        adoption_clock='original stored_clock, control_slot UNKNOWN, no sim_time_us; NOT B4 normal slot',
        same_context_not_DOF_gas_or_physical_readback=True, verification_clones_are_fixture_only_not_producer_ownership=True,
        future_parent_CPU_run='DEFERRED_NEW_NAMESPACE_WITH_EXPLICIT_PARENT_ADMISSION',
        independent_of_old_B4_CPU_PASS=True, old9pair_proof_reused=False,
        forbidden_operation_audit=dict(AUDIT), native_modules_loaded=loaded,
        permitted_FS_before_receipt=dict(FS), expected_NEW_outputs=4,
        Gate1='UNKNOWN', exact=False, stage2_GO=False)
    export('SOURCE_RECEIPT.json', receipt)
    files = []
    for name in BASE+OUTPUTS[:-1]:
        row = checks.identity(HERE/name)
        files.append(dict(relative=name, bytes=row['bytes'], sha256=row['sha256']))
    root = hashlib.sha256(canonical(files)).hexdigest()
    export('SOURCE_SEAL.json', dict(kind='TYPED_C2_CPU_FIXTURE_SOURCE_SEAL_V1', frozen=True, source_only=True,
        files=files, member_count=len(files), content_root_sha256=root,
        tests_passed=5, actual_fixture_CPU_runs=0, actual_SDK=False, Gate1='UNKNOWN', exact=False, stage2_GO=False))
    print(json.dumps(dict(root=root,seal=checks.identity(HERE/'SOURCE_SEAL.json'),fixture=checks.identity(HERE/'typed_c2_cpu_fixture.py'),
                         source_tests=5,actual_CPU=0,audit=AUDIT,permitted_FS_final=FS),indent=2))


if __name__ == '__main__':
    main()
