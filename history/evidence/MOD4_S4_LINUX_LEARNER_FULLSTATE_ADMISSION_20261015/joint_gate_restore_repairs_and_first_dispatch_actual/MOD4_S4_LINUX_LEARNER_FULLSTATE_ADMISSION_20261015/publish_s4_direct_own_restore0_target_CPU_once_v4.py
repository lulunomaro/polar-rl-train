"""CPU materialization only. Independent namespace; never imports a once launcher."""
from pathlib import Path
import json,sys,hashlib,time,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
BASE='/mnt/mod4_linux_durable_20261013'
TARGET=BASE+'/MOD4_S4_E0_WAVE35_DIRECT_OWN_RESTORE_CACHE_V4_20261015'
STAGE=BASE+'/MOD4_S4_E0_WAVE35_DIRECT_OWN_RESTORE_UPLOAD_V4_20261015'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    r=D/'reports'
    assert json.loads((r/'S4_MIGRATION_ORIGINAL_TYPED8_AND_SHARED_STATE_CPU_ACTUAL.json').read_bytes())['passed'] is True
    p=sorted(r.glob('S4_ACTUAL_LINUX_RSL5_COMPONENT_TARGET_CPU_ADMITTED_*.json'))[-1]
    component=json.loads(p.read_bytes());assert component['target_actual']['passed_target_CPU_component'] is True
    files=[D/'s4_zero_control_state_integrity_v1.py']+[D/name for name in ('s4_rsl5_frozen_pair_learner_v1.py','s4_original_fullstate_migration_v2.py',
        's4_linux20k_direct_own_restore0_worker_v4.py','s4_missing_direct_own_restore0_parent_v4.py',
        'materialize_s4_direct_own_restore0_target_CPU_v4.py')]
    files += [W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015/s4_shared_feedback_hardtop1_v1.py',
        W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014/hard_top1_frozen_expert_CPU_component_v1.py',
        W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014/payload_v1/bodyframe_deferred_original_import_v1.py']
    payload=D/'direct_own_cache_payload_v4';assert not payload.exists();payload.mkdir()
    for source in files:
        compile(source.read_bytes(),str(source),'exec');(payload/source.name).write_bytes(source.read_bytes())
    refs=json.loads((D/'target_CPU_components_v1/CPU_COMPONENT_SOURCE_MANIFEST.json').read_bytes())['refs']
    ctx=dict(target_root=TARGET,upload_stage=STAGE,files={q.name:sha(q) for q in payload.iterdir()},refs=refs,
        original_W35_manifest_SHA=sha(D/'actual_original_W35_run_manifest.json'),actual_logger_source_SHA='d9822d8317724507a7c817e85399db0db9e56a4eae959435138e75cf92e44b8d',valid_prior_own_zero_source_path='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_HEALTH_V3_20261015/own_first_fullsave0_healthschema/attempt/S4_OWN_INTEGRATION_FULLSAVE.pt',valid_prior_own_zero_source_SHA='601455ca68fbabe8a89b9165ce83007fe6157333b1c6f770520b6890a061f19d')
    (payload/'LOCAL_TARGET_CONTEXT.json').write_text(json.dumps(ctx,indent=2))
    stamp=str(time.time_ns());c=None;sf=None
    def run(code,label):
        si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write()
        raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
        p=r/(label+'_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_retry=True),indent=2),encoding='utf8');assert rc==0,str(p)
        return json.loads(raw)
    try:
        c=t.connect()
        run('from pathlib import Path\nimport json\ns=Path('+repr(STAGE)+');r=Path('+repr(TARGET)+');assert not s.exists() and not r.exists();s.mkdir();print(json.dumps(dict(new_upload_stage_only=True)))','S4_NATIVE_FULLSTATE_UPLOAD_INTENT_ACTUAL')
        sf=c.open_sftp();sf.get_channel().settimeout(60)
        for p in payload.iterdir():sf.put(str(p),STAGE+'/'+p.name)
        code='CONTEXT='+repr(ctx)+'\n'+(payload/'materialize_s4_direct_own_restore0_target_CPU_v4.py').read_text()
        result=run(code,'S4_NATIVE_FULLSTATE_TARGET_CPU_TRANSPORT_ACTUAL')
        out=D/'S4_DIRECT_OWN_CACHE_V4_TARGET_CPU_ACTUAL.json';assert not out.exists()
        sf.get(TARGET+'/S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json',str(out),max_concurrent_prefetch_requests=16)
        assert sha(out)==result['receipt_SHA']
        p=r/('S4_DIRECT_OWN_CACHE_V4_TARGET_CPU_MATERIALIZED_ACTUAL_'+stamp+'.json')
        p.write_text(json.dumps(dict(epoch=time.time(),passed=True,result=result,actual_receipt=str(out),actual_receipt_SHA=sha(out),GPU_dispatched=False,source_files_all_uploaded_byteSHA_bound=True),indent=2),encoding='utf8')
        print(json.dumps(dict(passed=True,report=str(p),target_root=TARGET,GPU=False)))
    except BaseException:
        (r/('S4_NATIVE_FULLSTATE_PUBLISH_ORIGINAL_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_retry=True)),encoding='utf8');raise
    finally:
        if sf:sf.close()
        t.close(c)
if __name__=='__main__':main()
