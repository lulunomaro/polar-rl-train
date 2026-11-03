"""One-shot local SOURCE seal. stdlib/fake/AST only; never run native entrypoints."""
from pathlib import Path
import hashlib
import io
import json
import os
import platform
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent
BASE_FILES=['README.md','CAPTURE_SOURCE_INDEX.json','phase1_capture_contract.py','phase1_capture_observer.py',
            'phase1_capture_runtime.py','worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py',
            'prepare_sources.py','test_capture_worker_source.py','seal_source.py']
OUTPUTS=['FAKE_TEST_LOG.txt','SOURCE_PINS.json','SOURCE_RECEIPT.json','SOURCE_SEAL.json']
NATIVE_PREFIXES=('torch','isaaclab','isaacsim','omni','pxr','warp','psutil','numpy','paramiko')
AUDIT=dict(forbidden_model_open_attempts=0,forbidden_native_import_attempts=0,
           subprocess_attempts=0,network_attempts=0,escaped_write_attempts=0,
           canonical_or_lock_open_attempts=0,delete_or_move_attempts=0)


def audit(event,args):
    if event=='import' and args and str(args[0]).split('.')[0] in NATIVE_PREFIXES:
        AUDIT['forbidden_native_import_attempts']+=1;raise RuntimeError('SOURCE seal blocks native/nonstdlib import')
    if event in ('subprocess.Popen','os.system','os.spawn','os.exec'):
        AUDIT['subprocess_attempts']+=1;raise RuntimeError('SOURCE seal blocks subprocess')
    if event.startswith('socket.'):
        AUDIT['network_attempts']+=1;raise RuntimeError('SOURCE seal blocks network')
    if event in ('os.remove','os.rmdir','os.rename','os.replace'):
        AUDIT['delete_or_move_attempts']+=1;raise RuntimeError('SOURCE seal performs no delete or move')
    if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
        path=Path(os.fsdecode(args[0])).resolve()
        if path.suffix.lower() in ('.pt','.pth','.ckpt','.safetensors'):
            AUDIT['forbidden_model_open_attempts']+=1;raise RuntimeError('SOURCE seal blocks model files')
        if path.suffix.lower()=='.lock' or path.name.lower()=='training_budget_10h.json':
            AUDIT['canonical_or_lock_open_attempts']+=1;raise RuntimeError('SOURCE seal blocks canonical/lock paths')
        mode=args[1] if len(args)>1 else None;flags=args[2] if len(args)>2 else 0
        writing=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or bool(isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
        if writing and (path.parent!=HERE or path.name not in OUTPUTS+['CAPTURE_SOURCE_INDEX.json']):
            AUDIT['escaped_write_attempts']+=1;raise RuntimeError('SOURCE seal blocks writes outside declared NEW outputs')


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def identity(path):
    raw=Path(path).read_bytes();return dict(relative=Path(path).name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def new_text(name,text):
    path=HERE/name
    with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(text)


def new_json(name,value):
    new_text(name,json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def main():
    if not sys.dont_write_bytecode:raise RuntimeError('Run Python314 -B only')
    if any((HERE/name).exists() for name in OUTPUTS):raise RuntimeError('one-shot outputs already exist; frozen/new lineage required')
    sys.addaudithook(audit)
    sys.path.insert(0,str(HERE))
    import prepare_sources
    preparation=prepare_sources.build_index()
    import test_capture_worker_source
    stream=io.StringIO();started=time.time()
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_capture_worker_source)
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    elapsed=time.time()-started
    native_loaded=sorted(name for name in sys.modules if name.split('.')[0] in NATIVE_PREFIXES)
    if not result.wasSuccessful() or native_loaded or any(AUDIT.values()):
        print(stream.getvalue());raise RuntimeError('SOURCE tests/audit did not pass; seal not created')
    new_text('FAKE_TEST_LOG.txt','STDLIB FAKE / AST ONLY; NO NATIVE RUN\nPython '+platform.python_version()+' -B\n'+stream.getvalue())
    index=json.loads((HERE/'CAPTURE_SOURCE_INDEX.json').read_text(encoding='utf-8'))
    source_rows=[identity(HERE/name) for name in BASE_FILES]
    pins=dict(kind='PHASE1_CAPTURE_WORKER_SOURCE_PINS_V1',source_only=True,source_files=source_rows,
              original17=index['original17'],dependency_seals=index['dependency_seals'],
              all_actuation_original_sources=index['all_actuation_original_sources'],
              whole_static_tree_status=index['full_original_static_tree_banks_and_vendor7_preservation'],
              actual_native_or_resource_qualification=False)
    new_json('SOURCE_PINS.json',pins)
    receipt=dict(kind='PHASE1_CAPTURE_WORKER_SOURCE_RECEIPT_V1',source_only=True,
        python_version=platform.python_version(),python_minus_B=True,
        capability_selection=dict(catalog='Office/ACL only; no RL-specific skill',selected='filesystem + Python314 stdlib CLI'),
        tests=dict(scope='stdlib fake + AST; pure in-memory env/App/FS fixtures',ran=result.testsRun,
                   failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
                   successful=result.wasSuccessful(),elapsed_seconds=elapsed),
        actual_sensor_native_install=False,actual_actuation_native_install=False,actual_native_worker_main=False,
        actual_PT_reads=0,actual_SDK_imports=0,actual_native_runs=0,actual_GPU_calls=0,
        actual_resource_gate_calls=0,actual_EX_lock_operations=0,actual_canonical_reads=0,actual_canonical_writes=0,
        actual_stage=0,actual_dispatch=0,actual_SSH=0,actual_raw_reads=0,Git_operations=0,
        original_sealed_source_edits=0,native_worker_source_generated=True,
        audit=AUDIT,native_modules_loaded=native_loaded,source_preparation=preparation,
        E3_default_controls=64,optional_controls=128,num_envs=80,model_PT_reads_by_candidate=0,
        teacher=None,learner_created=False,optimizer_created=False,replay_created=False,
        original_formal_reset_place_publish_compute_order=[53,55,66],
        initial_clean0='UNKNOWN_SAME_TICK_CACHE_MAY_BE_REUSED',initial_sensor_memory_saved_in_trace=True,
        global100Hz_slot_counters_are_not_per_row_episode_freshness=True,
        original_parent_unchanged_line_blocks=[[17,44],[46,78]],
        original_evalclose_lines=[365,421],original_env_close_calls_in_source=1,original_App_close_calls_in_source=1,
        pre_SDK_root_GPU_deadline_fd_checks='SAME_INSTALLED_REMOTE_ROOT; GPU==CUDA_VISIBLE_DEVICES; future deadline; two nonnegative unique fstat only',
        original_private_GPU_EX_finiteEX_Popen_wait_finally_preserved=True,
        artificial_approval_gate_added=False,new_budget_writer_added=False,
        pending=['NEWpurpose original sourcehardpin/newkind entry review','independent full static baseline provenance/materializer',
                 'outer controller actual parent Popen.wait','actual original resource gate/SDK/native capture',
                 'untapped actor35 bitwise/per-row episode fresh samples/partial reset live verifier',
                 'SDK physical parameter readback and actual existing-protocol cost-settlement evidence'],
        capture_interface_passed=False,gate1='UNKNOWN',exact=False,paper_ready=False,stage2_GO=False)
    new_json('SOURCE_RECEIPT.json',receipt)
    files=[identity(HERE/name) for name in BASE_FILES+OUTPUTS[:-1]]
    root=hashlib.sha256(canonical(files)).hexdigest()
    seal=dict(kind='PHASE1_CAPTURE_WORKER_SOURCE_SEAL_V1',frozen=True,source_only=True,
              content_root_sha256=root,files=files,tests_passed=result.testsRun,
              actual_SDK_or_native=False,actual_PT_reads=0,actual_resource_or_canonical_operations=0,
              capture_interface_passed=False,gate1='UNKNOWN',exact=False,stage2_GO=False)
    new_json('SOURCE_SEAL.json',seal)
    print(json.dumps(dict(content_root_sha256=root,seal_file=identity(HERE/'SOURCE_SEAL.json'),
                         tests=result.testsRun,actual_native=0,actual_SDK=0,actual_PT=0,actual_resources=0),indent=2))


if __name__=='__main__':main()
