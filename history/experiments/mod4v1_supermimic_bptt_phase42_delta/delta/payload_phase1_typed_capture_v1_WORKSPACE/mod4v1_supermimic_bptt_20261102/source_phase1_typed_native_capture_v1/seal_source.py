"""One-shot stdlib SOURCE seal; reuses V4 audit/pins pattern, never native entrypoints."""
from pathlib import Path
import hashlib
import io
import json
import os
import platform
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
BASE_FILES = ['README.md', 'PRODUCER_ABI.json', 'CAPTURE_SOURCE_INDEX.json', 'FINITE_SOURCE_BUNDLE.json',
              'phase1_capture_contract.py', 'phase1_capture_observer.py', 'phase1_capture_runtime.py',
              'worker_passive_interface_v1.py', 'single_gpu_passive_capture_parent_v1.py',
              'prepare_sources.py', 'test_typed_native_source.py', 'seal_source.py']
OUTPUTS = ['FAKE_TEST_LOG.txt', 'SOURCE_PINS.json', 'SOURCE_RECEIPT.json', 'SOURCE_SEAL.json']
NATIVE_PREFIXES = ('torch', 'isaaclab', 'isaacsim', 'omni', 'pxr', 'warp', 'psutil', 'numpy', 'paramiko', 'genesis')
AUDIT = dict(forbidden_model_or_raw_open_attempts=0, forbidden_native_import_attempts=0,
             subprocess_attempts=0, network_attempts=0, escaped_write_attempts=0,
             canonical_or_lock_open_attempts=0, lock_operations=0, delete_or_move_attempts=0,
             directory_creation_attempts=0)
SOURCE_FS = dict(permitted_SOURCE_read_opens=0, declared_NEW_output_write_opens=0)


def audit(event, args):
    if event == 'import' and args and str(args[0]).split('.')[0] in NATIVE_PREFIXES:
        AUDIT['forbidden_native_import_attempts'] += 1
        raise RuntimeError('SOURCE seal blocks native/nonstdlib import')
    if event in ('subprocess.Popen', 'os.system', 'os.spawn', 'os.exec'):
        AUDIT['subprocess_attempts'] += 1
        raise RuntimeError('SOURCE seal blocks subprocess')
    if event.startswith('socket.'):
        AUDIT['network_attempts'] += 1
        raise RuntimeError('SOURCE seal blocks network')
    if event in ('fcntl.flock', 'fcntl.lockf', 'msvcrt.locking'):
        AUDIT['lock_operations'] += 1
        raise RuntimeError('SOURCE seal blocks lock operations')
    if event in ('os.remove', 'os.rmdir', 'os.rename', 'os.replace'):
        AUDIT['delete_or_move_attempts'] += 1
        raise RuntimeError('SOURCE seal blocks delete/move')
    if event == 'os.mkdir':
        AUDIT['directory_creation_attempts'] += 1
        raise RuntimeError('SOURCE seal blocks directory creation')
    if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).resolve()
        if path.suffix.lower() in ('.pt', '.pth', '.ckpt', '.safetensors', '.raw', '.bin', '.npy', '.npz', '.pkl', '.pickle', '.joblib', '.usd'):
            AUDIT['forbidden_model_or_raw_open_attempts'] += 1
            raise RuntimeError('SOURCE seal blocks model/raw/asset reads')
        if path.suffix.lower() == '.lock' or path.name.lower() == 'training_budget_10h.json':
            AUDIT['canonical_or_lock_open_attempts'] += 1
            raise RuntimeError('SOURCE seal blocks canonical/lock paths')
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else 0
        writing = ((isinstance(mode, str) and any(char in mode for char in 'wax+')) or
                   bool(isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)))
        if writing:
            if path.parent != HERE or path.name not in OUTPUTS:
                AUDIT['escaped_write_attempts'] += 1
                raise RuntimeError('SOURCE seal blocks writes outside four exclusive NEW outputs')
            SOURCE_FS['declared_NEW_output_write_opens'] += 1
        else:
            SOURCE_FS['permitted_SOURCE_read_opens'] += 1


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def identity(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(relative=path.name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def new_text(name, text):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)


def new_json(name, value):
    new_text(name, json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def main():
    if sys.version_info[:2] != (3, 14) or not sys.dont_write_bytecode:
        raise RuntimeError('Run the existing Python314 -B stdlib only')
    if any((HERE / name).exists() for name in OUTPUTS):
        raise RuntimeError('One-shot outputs already exist; frozen/new lineage required')
    sys.addaudithook(audit)
    import prepare_sources
    before = {name: identity(HERE / name) for name in BASE_FILES}
    index, bundle = prepare_sources.build_metadata()
    if index != json.loads((HERE / 'CAPTURE_SOURCE_INDEX.json').read_bytes()) or bundle != json.loads((HERE / 'FINITE_SOURCE_BUNDLE.json').read_bytes()):
        raise RuntimeError('Actual finite metadata differs from the full current SOURCE closure')
    import test_typed_native_source
    stream = io.StringIO()
    started = time.time()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(test_typed_native_source))
    elapsed = time.time() - started
    after_index, after_bundle = prepare_sources.build_metadata()
    native_loaded = sorted(name for name in sys.modules if name.split('.')[0] in NATIVE_PREFIXES)
    source_changed = [name for name in BASE_FILES if before[name] != identity(HERE / name)]
    if (not result.wasSuccessful() or result.testsRun != 10 or native_loaded or any(AUDIT.values())
            or source_changed or index != after_index or bundle != after_bundle):
        print(stream.getvalue())
        raise RuntimeError('SOURCE tests/audit/full before-after pins failed; seal not created')
    new_text('FAKE_TEST_LOG.txt', 'NEW TYPED-NATIVE SOURCE: 10 OWN FAKE/AST/METADATA CHECKS; NO OLD TESTS / TORCH CPU / SDK / HOOK INSTALL / NATIVE\nPython '
             + platform.python_version() + ' -B\n' + stream.getvalue())
    pins = dict(kind='PHASE1_TYPED_NATIVE_SOURCE_PINS_V1', source_only=True, source_files=list(before.values()),
        original17=index['original17'], candidate_sources=index['new_sources'], runtime_dependency_sources=index['dependency_sources'],
        bootstrap_original_sources=index['bootstrap_original_sources'], producer_abi=index['producer_abi'],
        source_derivation=index['source_derivation'], dependency_seals=index['dependency_seals'],
        original_B2_reference_seal=index['original_B2_reference_seal'],
        sensor_source_manifest=index['sensor_source_manifest'], all_actuation_original_sources=index['all_actuation_original_sources'],
        full_static_tree_reference=index['full_original_static_tree_banks_and_vendor7_preservation'],
        actual_native_or_resource_qualification=False)
    new_json('SOURCE_PINS.json', pins)
    receipt = dict(kind='PHASE1_TYPED_NATIVE_SOURCE_RECEIPT_V1', source_only=True,
        python_version=platform.python_version(), python_minus_B=True,
        capability_selection=dict(catalog='Office/ACL; no RL-specific skill', selected='FS + existing Python314 stdlib CLI'),
        tests=dict(scope='10 NEW own-fake/AST/full SOURCE closure/default22+3 metadata checks; no old suites or real Torch tensors',
                   ran=result.testsRun, failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
                   successful=result.wasSuccessful(), elapsed_seconds=elapsed),
        source_preparation=dict(full_finite_file_mappings=34, original17=17, candidate_files=5, runtime_dependencies=9,
            bootstrap_files=2, ABI_files=1, frozen_members=dict(V4=13,B4=21,codec=7,C2=5),
            original_sensor_full_sources=155, original_sensor_pin_references=435, original_actuation_full_sources=182,
            original_B2_missing_root_preserved_as_null=True, full_static_tree_independent_provenance='PENDING_PARENT_REVIEW',
            materialized_files=0, all_source_and_upstream_before_after_unchanged=True),
        minimal_diff=index['source_derivation']['minimal_diff'], actual_sensor_native_install=False,
        actual_actuation_native_install=False, actual_native_worker_main=False,
        actual_Torch_CPU_executed=False, actual_Torch_tensors_created=0, actual_B4_native_MRO_preflight=False,
        actual_PT_reads=0, actual_raw_reads=0, actual_SDK_imports=0, actual_native_runs=0, actual_GPU_calls=0,
        actual_resource_gate_calls=0, actual_EX_lock_operations=0, actual_canonical_reads=0, actual_canonical_writes=0,
        actual_stage=0, actual_dispatch=0, actual_SSH=0, Git_operations=0, original_sealed_source_edits=0,
        actual_reports_read=False, old_tests_reexecuted=False,
        permitted_metadata_execution=dict(full_published_module_imports=['typed_capture_codec','source_api','field_snapshot','dependency_contract'],
            default_function_proofs=22, default_codec_class_proofs=3, real_B4_hook_install=False, real_C2_hook_install=False,
            own_FakeTensor_adopt_and_materialize=True, int64_above_2pow53_and_bool_preserved=True),
        audit=dict(AUDIT), audit_scope='FORBIDDEN_OPERATIONS_ONLY; local SOURCE reads/four NEW artifact writes are separate',
        permitted_SOURCE_FS_before_receipt=dict(SOURCE_FS), expected_final_NEW_outputs=4,
        native_modules_loaded=native_loaded, own_source_changed_during_test=source_changed,
        E3_controls=[64,128], num_envs=80, model_PT_reads_by_candidate=0, teacher=None,
        learner_created=False, optimizer_created=False, replay_created=False,
        original_formal_reset_place_publish_compute_order=[53,55,66], initial_clean0='UNKNOWN_SAME_TICK_CACHE_MAY_BE_REUSED',
        all_controls_sensor_ledger=True, C2_retention='FIRST2_LAST2_MIDDLE_UNKNOWN',
        private_RNG_state_equality='UNKNOWN', DOF_target_pipeline_join='UNKNOWN', physical_readback='UNKNOWN',
        original_private_GPU_EX_finiteEX_actual_Popen_wait_and_full_AppV6_Base_closure_preserved=True,
        outer_controller_actual_parent_Popen_wait='PENDING_REQUIRED_SEPARATE_RECEIPT',
        artificial_approval_gate_added=False, new_budget_writer_added=False,
        pending=['parent NEW purpose/sourcehardpin review and independent full eight-runtime/static-bank/vendor7 baseline',
                 'parent separately admitted original CPU/resource/SDK/native probe and typed consumer actual payload review',
                 'actual same-instance MRO/callback/return identity/clean-noise-delay/reset-clock and untapped comparison evidence',
                 'actual parent wait/all-child waits/AppV6->Base close/both EX release and existing-protocol cost settlement',
                 'private RNG equality/fullMID35/nonwitness samples/middle C2/SDK physical readback/DOF pipeline remain UNKNOWN'],
        science_consistency_status='UNKNOWN_PENDING_TYPED_CONSUMER', capture_interface_passed=False,
        gate1='UNKNOWN', exact=False, paper_ready=False, stage2_GO=False)
    new_json('SOURCE_RECEIPT.json', receipt)
    files = [identity(HERE / name) for name in BASE_FILES + OUTPUTS[:-1]]
    root = hashlib.sha256(canonical(files)).hexdigest()
    seal = dict(kind='PHASE1_TYPED_NATIVE_SOURCE_SEAL_V1', frozen=True, source_only=True,
        content_root_sha256=root, files=files, tests_passed=10, typed_producer_schema=index['typed_producer_schema'],
        original_parent_SHA256='d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41',
        V4_content_root_sha256=index['source_derivation']['v4_frozen_seal']['content_root_sha256'],
        B4_content_root_sha256=index['dependency_seals']['sensor']['content_root_sha256'],
        codec_content_root_sha256=index['dependency_seals']['codec']['content_root_sha256'],
        C2_content_root_sha256=index['dependency_seals']['actuation_clock_scope_v2']['content_root_sha256'],
        actual_SDK_or_native=False, actual_PT_reads=0, actual_Torch_CPU=False, actual_resource_or_canonical_operations=0,
        capture_interface_passed=False, science_consistency_status='UNKNOWN_PENDING_TYPED_CONSUMER',
        gate1='UNKNOWN', exact=False, stage2_GO=False)
    new_json('SOURCE_SEAL.json', seal)
    print(json.dumps(dict(content_root_sha256=root, seal_file=identity(HERE/'SOURCE_SEAL.json'),
        source_members=len(files), tests=result.testsRun, forbidden_operation_audit=AUDIT,
        permitted_SOURCE_FS_final=SOURCE_FS, actual_native=0, actual_SDK=0, actual_PT=0,
        actual_Torch_CPU=0, actual_resources=0), indent=2))


if __name__ == '__main__':
    main()
