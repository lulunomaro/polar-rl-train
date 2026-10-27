"""One actual CPU admission; externally pinned immutable proof reuse at node start."""
from pathlib import Path
import json,subprocess,time
from native87_protocol_v1 import validate_spec,native87_valid_ready,digest
PROOF_RELATIVE='job0/NATIVE87_PREINSTALLED_CPU_PROOF_ACTUAL.json'
REPORT_RELATIVE='job0/NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL.json'
STARTED_RELATIVE='job0/native87_SOURCE_CPU_STARTED_ACTUAL.json'
WAITED_RELATIVE='job0/native87_SOURCE_CPU_WAITED_EXIT_ACTUAL.json'

def _argv(spec,B):
    return [spec['python'],'-u','-B',str(Path(B)/spec['closed_source_CPU_script']),
        '--slot',spec['key'],'--num-envs','4096','--seed',str(spec['seed']),
        '--source-scope','policy_only_fresh_environment']

def validate_proof_data(proof,spec,*,manifest_SHA,script_SHA,report_SHA,started_SHA,waited_SHA,expected_argv,expected_exe):
    assert proof['schema']=='mod4.native87.actual_waited_preinstalled_CPU.v1' and proof['not_synthetic'] is True
    assert proof['actual_CPU_waited_EXIT0'] is True and proof['returncode']==0
    assert proof['manifest_SHA']==manifest_SHA==spec['manifest_SHA']
    assert proof['script_relative']==spec['closed_source_CPU_script'] and proof['script_SHA']==script_SHA==spec['candidate_pins'][spec['closed_source_CPU_script']]
    assert proof['source_SHA']==spec['source_SHA']==spec['bootstrap_source_SHA']
    assert proof['report_relative']==REPORT_RELATIVE and proof['report_SHA']==report_SHA
    assert proof['started_receipt_SHA']==started_SHA and proof['waited_receipt_SHA']==waited_SHA
    identity=proof['actual_identity'];assert isinstance(identity['pid'],int) and identity['pid']>0 and identity['creation']>0
    assert identity['argv']==expected_argv and identity['exe']==expected_exe and proof['waited_epoch']>=proof['started_epoch']
    envelope=proof['ready_envelope'];assert envelope['actual_CPU_waited_EXIT0'] is True and envelope['SHA']==report_SHA==digest(envelope['value'])
    assert native87_valid_ready(dict(key=spec['key'],phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=envelope,original_error=False),spec)
    return envelope

def load(spec,B):
    import three_slot_common_v1 as b
    validate_spec(spec);B=Path(B).resolve();script=B/spec['closed_source_CPU_script'];proof_path=B/PROOF_RELATIVE
    assert script.resolve().is_relative_to(B) and script.is_file() and not script.is_symlink()
    assert b.H(script)==spec['candidate_pins'][spec['closed_source_CPU_script']]
    args=_argv(spec,B)
    if spec.get('preinstalled_CPU_proof_SHA'):
        assert proof_path.is_file() and not proof_path.is_symlink() and b.H(proof_path)==spec['preinstalled_CPU_proof_SHA']
        proof=b.read(proof_path);started=b.read(B/STARTED_RELATIVE);waited=b.read(B/WAITED_RELATIVE)
        assert started==proof['actual_identity'] and waited['pid']==started['pid'] and waited['actual_waited'] is True and waited['returncode']==0
        # Reuse no model load and no target script execution. Node's unchanged
        # validate_payload already rechecked all manifest file bytes, including source.
        envelope=validate_proof_data(proof,spec,manifest_SHA=b.H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),script_SHA=b.H(script),
            report_SHA=b.H(B/REPORT_RELATIVE),started_SHA=b.H(B/STARTED_RELATIVE),waited_SHA=b.H(B/WAITED_RELATIVE),
            expected_argv=args,expected_exe=str(Path(spec['python']).resolve()))
        assert envelope['value']==b.read(B/REPORT_RELATIVE)
        return envelope
    assert not proof_path.exists() and not (B/REPORT_RELATIVE).exists(),'No rearm/retry after an actual CPU attempt'
    import psutil
    started_epoch=time.time();p=subprocess.Popen(args,cwd=B,env=b.environment(spec,True),stdout=(B/'job0/native87_SOURCE_CPU.log').open('xb'),stderr=subprocess.STDOUT,close_fds=True)
    try:
        identity=b.ident(p.pid);assert identity is not None
        identity['exe']=str(Path(psutil.Process(p.pid).exe()).resolve());assert identity['argv']==args
        b.put(B/STARTED_RELATIVE,identity)
    finally:rc=p.wait()
    waited_epoch=time.time();b.put(B/WAITED_RELATIVE,dict(pid=p.pid,returncode=rc,actual_waited=True,waited_epoch=waited_epoch));assert rc==0
    report=B/REPORT_RELATIVE;value=b.read(report);envelope=dict(value=value,path=str(report),SHA=b.H(report),actual_CPU_waited_EXIT0=True)
    assert envelope['SHA']==digest(value)
    assert native87_valid_ready(dict(key=spec['key'],phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=envelope,original_error=False),spec)
    proof=dict(schema='mod4.native87.actual_waited_preinstalled_CPU.v1',not_synthetic=True,actual_CPU_waited_EXIT0=True,returncode=0,
        manifest_SHA=b.H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),script_relative=spec['closed_source_CPU_script'],script_SHA=b.H(script),
        source_SHA=spec['source_SHA'],report_relative=REPORT_RELATIVE,report_SHA=b.H(report),ready_envelope=envelope,
        actual_identity=identity,started_epoch=started_epoch,waited_epoch=waited_epoch,
        started_receipt_SHA=b.H(B/STARTED_RELATIVE),waited_receipt_SHA=b.H(B/WAITED_RELATIVE),
        no_actual_GPU_precontrol_claim=True)
    validate_proof_data(proof,spec,manifest_SHA=spec['manifest_SHA'],script_SHA=b.H(script),report_SHA=b.H(report),
        started_SHA=b.H(B/STARTED_RELATIVE),waited_SHA=b.H(B/WAITED_RELATIVE),expected_argv=args,expected_exe=str(Path(spec['python']).resolve()))
    with proof_path.open('x',encoding='utf8') as stream:json.dump(proof,stream,indent=2,allow_nan=False)
    return envelope
