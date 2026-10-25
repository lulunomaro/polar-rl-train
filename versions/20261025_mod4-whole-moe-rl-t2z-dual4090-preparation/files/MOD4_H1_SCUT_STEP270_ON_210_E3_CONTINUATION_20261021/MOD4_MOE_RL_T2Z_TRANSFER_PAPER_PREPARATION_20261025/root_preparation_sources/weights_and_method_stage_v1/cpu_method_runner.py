"""Installed CPU checks only; never invokes model/main constructors or training."""
import argparse
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025')
COMPAT=Path('/home/lc01/Zonglin Li/zonglin2/compat/glibc240')

def pycmd(*args):
    return [str(COMPAT/'ld-linux-x86-64.so.2'),'--library-path',
            f'{COMPAT}:{ROOT}/.venv/lib:{ROOT}/bootstrap311/lib',str(ROOT/'.venv/bin/python'),'-B',*args]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase-id',required=True)
    args=p.parse_args()
    assert ROOT.resolve()==ROOT
    method=ROOT/'method_bundle';source=ROOT/'source'
    out=ROOT/'receipts'/args.phase_id
    out.mkdir(exist_ok=False)
    os.environ.update(CUDA_VISIBLE_DEVICES='',NVIDIA_VISIBLE_DEVICES='none',
        OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
        PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',HF_HUB_OFFLINE='1',
        TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1')
    import torch
    torch.set_num_threads(1)
    torch.cuda.is_available=lambda:False
    torch.cuda.device_count=lambda:0
    def forbid(*a,**kw):raise RuntimeError('CUDA initialization forbidden in preparation')
    torch.cuda.init=forbid;torch.cuda._lazy_init=forbid
    sys.path.insert(0,str(method))
    from upstream_bridge import verify_fixed_sources,REQUIRED_HASHES
    verify_fixed_sources(source)
    views=out/'fixed_upstream_text_views';views.mkdir()
    for name in ('t2z/training/ours.py','scripts/train.py','wan_video_action/pipelines/wan_video_action.py'):
        data=(source/name).read_bytes()
        assert hashlib.sha256(data).hexdigest()==REQUIRED_HASHES[name]
        (views/(name.replace('/','__')+'.txt')).write_bytes(data)
    suite=importlib.import_module('test_moe_cpu')
    suite.OLD_SOURCES=views # Process-local source view binding, original71 files unchanged.
    log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(suite))
    (out/'TEST_LOG.txt').write_text(log.getvalue(),encoding='utf-8')
    raw,split=suite.fixture()
    manifest=out/'SYNTHETIC_MANIFEST_NOT_DATA.json';splits=out/'SYNTHETIC_SPLITS.json'
    manifest.write_text(json.dumps(raw),encoding='utf-8');splits.write_text(json.dumps(split),encoding='utf-8')
    missing=out/'MISSING_NATIVE_DATA_NOT_DATASET.json'
    missing.write_text(json.dumps(dict(raw,synthetic=False,episodes=[])),encoding='utf-8')
    cli=[]
    for name,which,flags,expected,marker in (
        ('synthetic_check',manifest,['--synthetic-contract-test'],0,'CHECKED_NOT_TRAINING_READY'),
        ('synthetic_rejected_real',manifest,[],1,'SYNTHETIC_NOT_TRAINING'),
        ('missing_real_rejected',missing,[],1,'DATASET_MISSING'),
        ('train_disabled',manifest,['--train'],1,'TRAINING_DISABLED_IN_PREPARATION'),
        ('installed_upstream_import_bind',manifest,['--synthetic-contract-test','--cpu-import-upstream',str(source)],0,'"actual_upstream_imported": true')):
        guard="import sys,runpy,torch; torch.cuda.is_available=lambda:False; torch.cuda.device_count=lambda:0; forbid=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('CUDA initialization forbidden')); torch.cuda.init=forbid; torch.cuda._lazy_init=forbid; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')"
        cmd=pycmd('-c',guard,str(method/'moe_train_entry.py'),'--manifest',str(which),'--splits',str(splits),*flags)
        proc=subprocess.run(cmd,cwd=method,env=os.environ.copy(),capture_output=True,timeout=60)
        # Offline imports and fixed synthetic errors contain no signed networkURLs.
        (out/(name+'_stdout.txt')).write_bytes(proc.stdout)
        (out/(name+'_stderr.txt')).write_bytes(proc.stderr)
        text=(proc.stdout+proc.stderr).decode(errors='replace')
        cli.append(dict(name=name,returncode=proc.returncode,expected_returncode=expected,
                        expected_marker=marker,passed=proc.returncode==expected and marker in text))
    passed=result.wasSuccessful() and result.testsRun>=12 and all(x['passed'] for x in cli) and not torch.cuda.is_initialized()
    report=dict(id=args.phase_id,epoch=time.time(),status='PASS_CPU_ONLY' if passed else 'FAIL_PRESERVED',
        tests_run=result.testsRun,tests_passed=result.wasSuccessful(),cli=cli,
        cuda_initialized=torch.cuda.is_initialized(),old_H1_files_transferred=False,
        test_source_binding='Process-local OLD_SOURCES points to SHA-verified installedsource text views',
        method_original_files_changed=False,weights_loaded=False,policy_inference=False,
        training_started=False,training_ready=False,native_RGB_data_available=False,
        full_model_4090_fit='NOT_TESTED',archive_status='PENDING_ROOT_GIT')
    with (out/'RESULT.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2)
    print(json.dumps(dict(result=str(out/'RESULT.json'),status=report['status'],tests_run=result.testsRun,cli_count=len(cli),training_ready=False)))
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
