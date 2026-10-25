"""Reviewable finite host72 CPU stages. No transport, installs, CUDA or training.

Root may exec this source in a namespace and call run_request(request). This
module never connects to hosts and never starts a stage at import time.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025')
COMPAT=Path('/home/lc01/Zonglin Li/zonglin2/compat/glibc240')
GUARD=25*1024**3
METHOD_INDEX_SHA='7f9c18f93b3bef98b664f0c0416e4579258dacd61884cf8ee1d8883f456cea49'
ENGINEERING_SHA={
    'scripts/download_required.py':'6e152345f2cb52033bcb48df1b538cddd457f84271cf0790711e167bff0becf2',
    'scripts/cpu_import_interface_check.py':'251feea3b0492b6b1b29105b47f04e9cb2e7f43f9f6fd7d3f0a42c2ccdfa4e20',
    'scripts/check_moe_registry.py':'315509ec7194ed97d0497eeebe8f785425dadc8633749982df29b801f9172bef',
    'WEIGHTS_MANIFEST.json':'4f9cf65f3f42dae7c8897ea571898f923e93ebc8522c97940ce69568d30c5ca7',
    'MOE_POLICY_REGISTRY.json':'d6a2e600e7150a1f069b3b2cd470d1e1ff42316bce23a3f7d2daa630417a876c'}

def _sha(path):
    # Called only on small source, JSON, method text or CPU logs, never weights.
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _guard(extra=0):
    if not ROOT.is_dir() or ROOT.resolve()!=ROOT:raise RuntimeError('Exact approved root missing or symlinked')
    free=shutil.disk_usage(ROOT).free
    if free-extra<=GUARD:raise RuntimeError('Own preparation refused at existing25GiB free guard')
    return free

def _write(path,data):
    with path.open('x',encoding='utf-8') as stream:json.dump(data,stream,indent=2)

def _safe_relative(value):
    p=Path(value)
    if p.is_absolute() or value.startswith('/') or '..' in p.parts or '\\' in value or not value or ':' in value or not p.parts:
        raise RuntimeError('Unsafe relative payload path')
    return p

def _env():
    allow=('PATH','HOME','USER','LANG','LC_ALL','SSL_CERT_FILE','SSL_CERT_DIR')
    env={k:os.environ[k] for k in allow if k in os.environ}
    env.update(CUDA_VISIBLE_DEVICES='',NVIDIA_VISIBLE_DEVICES='none',OMP_NUM_THREADS='1',
        MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',
        PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',
        TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1',HF_HUB_DISABLE_TELEMETRY='1',
        HF_HOME=str(ROOT/'cache/huggingface'),XDG_CACHE_HOME=str(ROOT/'cache/xdg'),
        TMPDIR=str(ROOT/'staging'),PIP_CONFIG_FILE='/dev/null',PIP_NO_INPUT='1')
    return env

def _py(*args):
    return [str(COMPAT/'ld-linux-x86-64.so.2'),'--library-path',
        f'{COMPAT}:{ROOT}/.venv/lib:{ROOT}/bootstrap311/lib',str(ROOT/'.venv/bin/python'),'-B',*args]

def _dependencies_ready():
    # Do not rerun any consumed installation phase, even after its failure.
    for phase in ('torch','requirements','check'):
        p=ROOT/'receipts'/('ROOT_'+phase.upper()+'_ACTUAL.json')
        if not p.is_file():raise RuntimeError('Required actual dependency phase receipt missing: '+phase)
        obj=json.loads(p.read_text())
        if not(obj.get('phase_passed') is True and obj.get('actual_returncode')==0 and obj.get('root')==str(ROOT)):
            raise RuntimeError('Dependency phase not successful; missing-only newphase required: '+phase)
    if not (ROOT/'.venv/bin/python').is_file():raise RuntimeError('Isolated venv missing')

def _engineering():
    base=ROOT/'engineering_bundle'
    if base.resolve()!=base:raise RuntimeError('Engineering bundle symlink refused')
    for rel,sha in ENGINEERING_SHA.items():
        p=base/rel
        if not p.is_file() or _sha(p)!=sha:raise RuntimeError('Frozen engineering source mismatch: '+rel)
    return base

def _method(base=None):
    base=base or ROOT/'method_bundle';idx=base/'reports/REPRODUCIBILITY_INDEX_V2.json'
    if base.resolve()!=base:raise RuntimeError('Method bundle symlink refused')
    if not idx.is_file() or _sha(idx)!=METHOD_INDEX_SHA:raise RuntimeError('Exact method index missing/mismatched')
    rows=json.loads(idx.read_text())['files']
    if len(rows)!=70:raise RuntimeError('Method index must include70 rows excluding itself')
    names={'reports/REPRODUCIBILITY_INDEX_V2.json'}
    for row in rows:
        rel=_safe_relative(row['relative_path']);p=base/rel
        if not p.resolve().is_relative_to(base.resolve()) or not p.is_file() or p.stat().st_size!=row['bytes'] or _sha(p)!=row['sha256']:
            raise RuntimeError('Method source bytes/hash mismatch')
        names.add(rel.as_posix())
    actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if names!=actual or len(names)!=71:raise RuntimeError('Method source file set mismatch')
    return base

def _stage_method(req,phase):
    payload=req['method_payload']
    if payload['root']!=str(ROOT) or payload['destination']!='method_bundle' or payload['file_count']!=71 or payload['index_sha256']!=METHOD_INDEX_SHA:
        raise RuntimeError('Exact71 method payload binding mismatch')
    rows=payload['files']
    if len(rows)!=71 or sum(row['bytes'] for row in rows)!=690537:raise RuntimeError('Method payload size mismatch')
    _guard(2*690537)
    target=ROOT/'method_bundle'
    if target.exists():
        _method()
        bundle_status='ALREADY_EXACT_NO_OVERWRITE'
    else:
        stage=ROOT/'staging'/(phase+'_method_bundle')
        stage.mkdir(exist_ok=False)
        seen=set()
        for row in rows:
            rel=_safe_relative(row['relative'])
            if rel.as_posix() in seen or '__pycache__' in rel.parts:raise RuntimeError('Duplicate or cache payload path')
            seen.add(rel.as_posix())
            raw=base64.b64decode(row['base64'],validate=True)
            if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise RuntimeError('Method payload content mismatch')
            p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as stream:stream.write(raw)
        if _sha(stage/'reports/REPRODUCIBILITY_INDEX_V2.json')!=METHOD_INDEX_SHA:raise RuntimeError('Final method index SHA mismatch')
        _method(stage)
        stage.rename(target)
        _method();bundle_status='STAGED_EXACT71_VERIFIED'
    # Root sends only reviewed helper source, not previousH1 packages/history.
    helper=req['cpu_runner']
    data=base64.b64decode(helper['base64'],validate=True)
    if len(data)!=helper['bytes'] or hashlib.sha256(data).hexdigest()!=helper['sha256']:raise RuntimeError('CPU runner source SHA mismatch')
    dest=ROOT/'preparation_helpers/weights_and_method_stage_v1';dest.mkdir(parents=True,exist_ok=True)
    runner=dest/'cpu_method_runner.py'
    if runner.exists():
        if _sha(runner)!=helper['sha256']:raise RuntimeError('Existing CPU runner differs; no overwrite')
    else:
        with runner.open('xb') as stream:stream.write(data)
    _write(ROOT/'receipts'/(phase+'_METHOD_SOURCE_BINDING.json'),dict(method_index_sha256=METHOD_INDEX_SHA,
        file_count=71,bytes=690537,cpu_runner_sha256=helper['sha256'],cpu_runner_path=str(runner),
        old_H1_directories_transferred=False,training_ready=False))
    return dict(status=bundle_status,method_files=71,method_bytes=690537,cpu_runner_sha256=helper['sha256'])

def _run(phase,label,argv,timeout):
    _guard()
    started=time.time()
    try:
        proc=subprocess.run(['nice','-n','19',*argv],env=_env(),cwd=ROOT,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
        rc=proc.returncode;raw=proc.stdout
    except subprocess.TimeoutExpired as exc:
        rc=124;raw=exc.stdout or b''
    log=ROOT/'receipts'/(phase+'_'+label+'_STDOUT_STDERR.log')
    with log.open('xb') as stream:stream.write(raw)
    return dict(label=label,returncode=rc,elapsed_seconds=time.time()-started,
                log=str(log),log_bytes=len(raw),log_sha256=_sha(log))

def run_request(req):
    action=req.get('action');phase=req.get('phase_id','')
    if action not in ('stage-method','cpu-imports','method-tests','download-batch','verify-weights'):
        raise RuntimeError('No installs/training or unspecified action in this helper')
    if req.get('root')!=str(ROOT) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}',phase):
        raise RuntimeError('Exactroot and unique safe phaseID required')
    _guard();receipts=ROOT/'receipts';receipts.mkdir(exist_ok=True)
    started=receipts/(phase+'_STARTED.json');final=receipts/(phase+'_FINAL.json')
    if started.exists() or final.exists():
        return dict(status='REFUSED_ALREADY_CONSUMED_PHASE_ID',phase_id=phase,action=action,training_ready=False)
    lock=ROOT/'staging/WEIGHTS_AND_METHOD_ACTIVE.lock'
    lock.parent.mkdir(exist_ok=True)
    try:
        with lock.open('x') as stream:stream.write(json.dumps(dict(phase_id=phase,pid=os.getpid(),epoch=time.time())))
    except FileExistsError:
        return dict(status='REFUSED_OWN_PREPARATION_LOCK_ACTIVE_REQUIRES_ROOT_RECONCILIATION',phase_id=phase,training_ready=False)
    result=dict(phase_id=phase,action=action,epoch=time.time(),training_started=False,training_ready=False,
        root=str(ROOT),GPU_queried=False,weights_loaded=False,archive_status='PENDING_ROOT_GIT')
    try:
        _write(started,dict(result,preparation_only=True,free_bytes=_guard()))
        if action=='stage-method':result.update(_stage_method(req,phase))
        else:
            _dependencies_ready();engineering=_engineering();_method()
            if action=='cpu-imports':
                runs=[_run(phase,'OFFICIAL_CPU_IMPORT',_py(str(engineering/'scripts/cpu_import_interface_check.py')),180),
                      _run(phase,'MOE_REGISTRY_JSON',_py(str(engineering/'scripts/check_moe_registry.py'),'--registry',str(engineering/'MOE_POLICY_REGISTRY.json'),'--outdir',str(receipts)),60)]
                result.update(runs=runs,status='PASS_CPU_IMPORTS_AND_REGISTRY' if all(x['returncode']==0 for x in runs) else 'CPU_IMPORT_FAILURE_PRESERVED_NO_AUTO_INSTALL')
            elif action=='method-tests':
                binding=Path(req['method_stage_binding'])
                if binding.parent!=receipts or not binding.name.endswith('_METHOD_SOURCE_BINDING.json'):raise RuntimeError('Exact own methodstage binding receipt required')
                bound=json.loads(binding.read_text());runner=Path(bound['cpu_runner_path'])
                if runner!=ROOT/'preparation_helpers/weights_and_method_stage_v1/cpu_method_runner.py' or _sha(runner)!=bound['cpu_runner_sha256']:
                    raise RuntimeError('Reviewed CPU method runner source changed')
                run=_run(phase,'METHOD_TESTS_AND_INSTALLED_BIND',_py(str(runner),'--phase-id',phase),600)
                result.update(runs=[run],status='PASS_METHOD_CPU_ONLY' if run['returncode']==0 else 'METHOD_CPU_FAILURE_PRESERVED_NO_AUTO_INSTALL')
            else:
                manifest=json.loads((engineering/'WEIGHTS_MANIFEST.json').read_text(encoding='utf-8-sig'))
                argv=_py(str(engineering/'scripts/download_required.py'),'--manifest',str(engineering/'WEIGHTS_MANIFEST.json'))
                if action=='download-batch':
                    seconds=int(req.get('max_seconds',180));files=int(req.get('max_files',1));amount=int(req.get('max_new_bytes',2*1024**3))
                    if not 10<=seconds<=900 or not 1<=files<=13 or not 1<=amount<=8*1024**3:raise RuntimeError('Explicit finite download bounds required')
                    argv+=['--max-seconds',str(seconds),'--max-files',str(files),'--max-new-bytes',str(amount)]
                    timeout=seconds+120
                else:
                    # Stat-only precheck avoids consuming an entire fullSHA scan
                    # before all13completefiles exist. No model-content read here.
                    if any(not (ROOT/x['destination']).is_file() or (ROOT/x['destination']).stat().st_size!=x['bytes'] for x in manifest['files']):
                        raise RuntimeError('Final fullSHA scan refused:13 complete files not yet present')
                    argv+=['--verify-only','--max-seconds','1800'];timeout=1920
                before={p.name for p in receipts.glob('*_download_*.json')}
                run=_run(phase,'WEIGHTS',argv,timeout)
                fresh=[p for p in receipts.glob('*_download_*.json') if p.name not in before]
                if len(fresh)!=1:raise RuntimeError('Expected exactly one own finite downloader receipt')
                report=json.loads(fresh[0].read_text())
                result.update(runs=[run],downloader_receipt=str(fresh[0]),
                    downloader_status=report['status'],new_bytes=report['new_bytes'],
                    all_required_verified_in_this_receipt=report.get('all_required_verified_in_this_receipt',False))
                if run['returncode']!=0:result['status']='DOWNLOAD_FAILURE_PRESERVED'
                elif action=='verify-weights':result['status']='PASS_ALL13_FULL_SHA_VERIFIED' if result['all_required_verified_in_this_receipt'] else 'FINAL_VERIFICATION_INCOMPLETE_PRESERVED'
                else:result['status']='FINITE_DOWNLOAD_BATCH_RETURNED'
        result['free_bytes_after']=_guard()
    except Exception as exc:
        result.update(status='FAILURE_PRESERVED',error_type=type(exc).__name__)
        if isinstance(exc,RuntimeError):result['reason']=str(exc)
    finally:
        result['finished_epoch']=time.time()
        if started.exists():_write(final,result)
        # This exact helper's own lock only; no process signals or external locks.
        if lock.is_file() and json.loads(lock.read_text()).get('phase_id')==phase:lock.unlink()
    # Small status only. Never rawlogs, environment, payloadbase64, signedURLs,
    # secrets or downloaded model content in stdout.
    return result
