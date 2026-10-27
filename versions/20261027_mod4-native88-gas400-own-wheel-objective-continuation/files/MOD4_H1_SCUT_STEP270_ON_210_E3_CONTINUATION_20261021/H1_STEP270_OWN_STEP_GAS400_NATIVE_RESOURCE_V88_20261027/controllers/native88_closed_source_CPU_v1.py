"""One actual CPU admission; externally pinned immutable proof reuse at node start."""
from pathlib import Path
import json,subprocess,time
from native88_protocol_v1 import validate_spec,native88_valid_ready,digest
PROOF_RELATIVE='job0/NATIVE88_PREINSTALLED_CPU_PROOF_ACTUAL.json'
REPORT_RELATIVE='job0/NATIVE88_CHANGED_PLANT_SOURCE_SDK_CPU_ACTUAL.json'
STARTED_RELATIVE='job0/native88_SOURCE_CPU_STARTED_ACTUAL.json'
WAITED_RELATIVE='job0/native88_SOURCE_CPU_WAITED_EXIT_ACTUAL.json'

def _argv(spec,B):
    return [spec['python'],'-u','-B',str(Path(B)/spec['closed_source_CPU_script']),
        '--slot',spec['key'],'--num-envs','4096','--seed',str(spec['seed']),
        '--source-scope','native_models_only_fresh400N_environment']

PY210='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
EXE210='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'
WRAPPER72='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
LOADER72='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2'
LIBRARY72='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib'
PYTHON72='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python'

def expected_exec_identity(spec,logical_argv,root):
    """Exact approved interpreter recipe; usable by metadata observers too."""
    assert logical_argv[0]==spec['python']
    if spec['execution_backend']=='source210':
        assert spec['key']=='h1' and spec['python']==PY210
        return dict(exe=EXE210,argv=list(logical_argv),root=str(root),recipe='direct210_approved_python3.12')
    assert spec['execution_backend']=='target72' and spec['key'] in ('e2','recovery') and spec['python']==WRAPPER72
    return dict(exe=LOADER72,argv=[LOADER72,'--library-path',LIBRARY72,PYTHON72,'-B',*logical_argv[1:]],root='/home/lc01/Zonglin Li/zonglin2',recipe='approved72_glibc240_exact_wrapper')

class ExecIdentityError(AssertionError):
    def __init__(self,reason,expected,lastrow,pid,creation,last_observation_error=None):
        self.details=dict(reason=reason,expected=expected,lastrow=lastrow,pid=pid,
            expected_creation=creation,last_observation_error=last_observation_error,
            mismatch={k:dict(expected=expected[k],actual=None if lastrow is None else lastrow.get(k))
                for k in ('exe','argv','root') if lastrow is None or lastrow.get(k)!=expected[k]})
        super().__init__(json.dumps(self.details,sort_keys=True))

def wait_exact_exec_identity(p,B,spec,args,timeout_s=5.):
    import psutil
    expected=expected_exec_identity(spec,args,B);until=time.monotonic()+timeout_s
    creation=None;previous=None;lastrow=None;last_observation_error=None
    while True:
        if p.poll() is not None:
            raise ExecIdentityError('child_exited_before_stable_exact_exec',expected,lastrow,p.pid,creation,last_observation_error)
        try:
            # psutil.Process.exe() caches per instance. A wrapper exec requires a
            # fresh instance on EVERY observation; retain pid/create separately.
            process=psutil.Process(p.pid)
            row=dict(pid=p.pid,creation=process.create_time(),argv=process.cmdline(),root=process.cwd(),exe=process.exe())
            lastrow=row;last_observation_error=None
            if creation is None:creation=row['creation']
            if row['creation']!=creation:
                raise ExecIdentityError('pid_creation_changed_during_exec',expected,row,p.pid,creation)
            exact=all(row[k]==expected[k] for k in ('exe','argv','root'))
            if exact and row==previous:return row
            previous=row if exact else None
        except (psutil.NoSuchProcess,psutil.AccessDenied) as exc:
            last_observation_error=dict(type=type(exc).__name__,error=str(exc));previous=None
        if time.monotonic()>=until:
            raise ExecIdentityError('exact_exec_identity_timeout',expected,lastrow,p.pid,creation,last_observation_error)
        time.sleep(.05)

def validate_proof_data(proof,spec,*,manifest_SHA,script_SHA,report_SHA,started_SHA,waited_SHA,expected_argv,expected_exe,expected_root):
    assert proof['schema']=='mod4.native88.actual_waited_preinstalled_CPU.v1' and proof['not_synthetic'] is True
    assert proof['actual_CPU_waited_EXIT0'] is True and proof['returncode']==0
    assert proof['manifest_SHA']==manifest_SHA==spec['manifest_SHA']
    assert proof['script_relative']==spec['closed_source_CPU_script'] and proof['script_SHA']==script_SHA==spec['candidate_pins'][spec['closed_source_CPU_script']]
    assert proof['source_SHA']==spec['source_SHA'] and proof['bootstrap_SHA']==spec['bootstrap_source_SHA']
    assert proof['report_relative']==REPORT_RELATIVE and proof['report_SHA']==report_SHA
    assert proof['started_receipt_SHA']==started_SHA and proof['waited_receipt_SHA']==waited_SHA
    identity=proof['actual_identity'];assert isinstance(identity['pid'],int) and identity['pid']>0 and identity['creation']>0
    assert identity['argv']==expected_argv and identity['exe']==expected_exe and identity['root']==expected_root and proof['waited_epoch']>=proof['started_epoch']
    envelope=proof['ready_envelope'];assert envelope['actual_CPU_waited_EXIT0'] is True and envelope['SHA']==report_SHA==digest(envelope['value'])
    assert native88_valid_ready(dict(key=spec['key'],phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=envelope,original_error=False),spec)
    return envelope

def load(spec,B):
    import three_slot_common_v1 as b
    validate_spec(spec);B=Path(B).resolve();script=B/spec['closed_source_CPU_script'];proof_path=B/PROOF_RELATIVE
    assert script.resolve().is_relative_to(B) and script.is_file() and not script.is_symlink()
    assert b.H(script)==spec['candidate_pins'][spec['closed_source_CPU_script']]
    args=_argv(spec,B);expected=expected_exec_identity(spec,args,B)
    if spec.get('preinstalled_CPU_proof_SHA'):
        assert proof_path.is_file() and not proof_path.is_symlink() and b.H(proof_path)==spec['preinstalled_CPU_proof_SHA']
        proof=b.read(proof_path);started=b.read(B/STARTED_RELATIVE);waited=b.read(B/WAITED_RELATIVE)
        assert started==proof['actual_identity'] and waited['pid']==started['pid'] and waited['actual_waited'] is True and waited['returncode']==0
        # Reuse no model load and no target script execution. Node's unchanged
        # validate_payload already rechecked all manifest file bytes, including source.
        envelope=validate_proof_data(proof,spec,manifest_SHA=b.H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),script_SHA=b.H(script),
            report_SHA=b.H(B/REPORT_RELATIVE),started_SHA=b.H(B/STARTED_RELATIVE),waited_SHA=b.H(B/WAITED_RELATIVE),
            expected_argv=expected['argv'],expected_exe=expected['exe'],expected_root=expected['root'])
        assert envelope['value']==b.read(B/REPORT_RELATIVE)
        return envelope
    assert not proof_path.exists() and not (B/REPORT_RELATIVE).exists(),'No rearm/retry after an actual CPU attempt'
    import psutil
    started_epoch=time.time();p=subprocess.Popen(args,cwd=B,env=b.environment(spec,True),stdout=(B/'job0/native88_SOURCE_CPU.log').open('xb'),stderr=subprocess.STDOUT,close_fds=True)
    try:
        identity=wait_exact_exec_identity(p,B,spec,args)
        b.put(B/STARTED_RELATIVE,identity)
    except BaseException as exc:
        import traceback
        error=dict(epoch=time.time(),pid=p.pid,type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc(),
            details=getattr(exc,'details',None),no_ready_or_proof_claim=True)
        with (B/'job0/native88_SOURCE_CPU_IDENTITY_ERROR_ACTUAL.json').open('x',encoding='utf8') as stream:
            json.dump(error,stream,indent=2,allow_nan=False)
        raise
    finally:
        # Persist the genuine wait result even if identity capture raised. A
        # waited EXIT0 alone never creates a ready envelope or admission proof.
        rc=p.wait();waited_epoch=time.time()
        b.put(B/WAITED_RELATIVE,dict(pid=p.pid,returncode=rc,actual_waited=True,waited_epoch=waited_epoch))
    assert rc==0
    report=B/REPORT_RELATIVE;value=b.read(report);envelope=dict(value=value,path=str(report),SHA=b.H(report),actual_CPU_waited_EXIT0=True)
    assert envelope['SHA']==digest(value)
    assert native88_valid_ready(dict(key=spec['key'],phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=envelope,original_error=False),spec)
    proof=dict(schema='mod4.native88.actual_waited_preinstalled_CPU.v1',not_synthetic=True,actual_CPU_waited_EXIT0=True,returncode=0,
        manifest_SHA=b.H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),script_relative=spec['closed_source_CPU_script'],script_SHA=b.H(script),
        source_SHA=spec['source_SHA'],bootstrap_SHA=spec['bootstrap_source_SHA'],report_relative=REPORT_RELATIVE,report_SHA=b.H(report),ready_envelope=envelope,
        actual_identity=identity,started_epoch=started_epoch,waited_epoch=waited_epoch,
        started_receipt_SHA=b.H(B/STARTED_RELATIVE),waited_receipt_SHA=b.H(B/WAITED_RELATIVE),
        no_actual_GPU_precontrol_claim=True)
    validate_proof_data(proof,spec,manifest_SHA=spec['manifest_SHA'],script_SHA=b.H(script),report_SHA=b.H(report),
        started_SHA=b.H(B/STARTED_RELATIVE),waited_SHA=b.H(B/WAITED_RELATIVE),expected_argv=expected['argv'],expected_exe=expected['exe'],expected_root=expected['root'])
    with proof_path.open('x',encoding='utf8') as stream:json.dump(proof,stream,indent=2,allow_nan=False)
    return envelope
