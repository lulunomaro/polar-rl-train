"""Prepare the first approved gate branch only from the independently closed source."""
from pathlib import Path
import sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
TARGET='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_FIRST_SUPPORTED_GATE45M_V1_20261015'
STAGE=TARGET+'_CPU_UPLOAD'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    admission=json.loads((D/'reports/CLOSED_S4_ZERO_FULLSTATE_INDEPENDENT_CPU_ADMITTED.json').read_bytes());assert admission['passed'] and admission['no_PPO_updates']
    assert json.loads((D/'reports/S4_SUPPORTED_ACTUAL_PPO_GRADIENT_ONLY_CPU_ACTUAL.json').read_bytes())['passed_CPU'] is True
    payload=D/'first_supported_formal_payload_v1';assert not payload.exists();payload.mkdir()
    names=('s4_rsl5_frozen_pair_learner_v1.py','s4_original_fullstate_migration_v2.py','s4_supported_rollout_storage_v1.py',
        's4_supported_shared_feedback_adapter_v1.py','s4_owned_rollout_audit_v1.py','s4_portable_supported_shadow_CPU_v1.py',
        's4_first_supported_gate_formal_worker_v2.py','s4_first_supported_gate_formal_parent_v2.py','materialize_s4_first_supported_formal_target_CPU_v4.py')
    paths=[D/n for n in names]+[W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015/s4_shared_feedback_hardtop1_v1.py',
        W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014/hard_top1_frozen_expert_CPU_component_v1.py',
        W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014/payload_v1/bodyframe_deferred_original_import_v1.py']
    for p in paths:compile(p.read_bytes(),str(p),'exec');(payload/p.name).write_bytes(p.read_bytes())
    for src,name in ((D/'target_CPU_components_v1/actual_saved35_CPU_input_rows.json','actual_saved35_CPU_input_rows.json'),
        (D/'reports/CLOSED_S4_ZERO_FULLSTATE_INDEPENDENT_CPU_ADMITTED.json','CLOSED_S4_ZERO_FULLSTATE_INDEPENDENT_CPU_ADMITTED.json'),
        (D/'reports/S4_NATIVE120_PARTIAL_SAVE_FAILURE_AND_ZERO_CONTROL_LOGGER_REPAIR_CPU_ACTUAL.json','NATIVE120_SAVE_FAILURE_INDEPENDENT_CPU_CLASSIFICATION.json')):
        (payload/name).write_bytes(src.read_bytes())
    ctx=dict(target_root=TARGET,upload_stage=STAGE,source_SHA=admission['source_SHA'],
        closed_zero_root='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_DIRECT_OWN_RESTORE_CACHE_V4_20261015',
        files={p.name:sha(p) for p in payload.iterdir()})
    (payload/'LOCAL_FORMAL_TARGET_CONTEXT.json').write_text(json.dumps(ctx,indent=2))
    stamp=str(time.time_ns());c=None;sf=None
    def run(code,label):
        si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
        p=D/'reports'/(label+'_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_retry=True),indent=2));assert rc==0,str(p);return json.loads(raw)
    try:
        c=t.connect();run('from pathlib import Path\nimport json\ns=Path('+repr(STAGE)+');r=Path('+repr(TARGET)+');assert not s.exists() and not r.exists();s.mkdir();print(json.dumps(dict(created_upload_only=True)))','S4_FIRST_GATE_TARGET_UPLOAD_INTENT_ACTUAL')
        sf=c.open_sftp();sf.get_channel().settimeout(60)
        for p in payload.iterdir():sf.put(str(p),STAGE+'/'+p.name)
        result=run('CONTEXT='+repr(ctx)+'\n'+(payload/'materialize_s4_first_supported_formal_target_CPU_v4.py').read_text(),'S4_FIRST_GATE_TARGET_CPU_TRANSPORT_ACTUAL')
        out=D/'S4_FIRST_FORMAL_TARGET_CPU_ACTUAL.json';assert not out.exists();sf.get(TARGET+'/S4_FIRST_FORMAL_TARGET_CPU_ACTUAL.json',str(out),max_concurrent_prefetch_requests=16);assert sha(out)==result['receipt_SHA']
        p=D/'reports'/('S4_FIRST_GATE_TARGET_CPU_MATERIALIZED_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(dict(epoch=time.time(),passed=True,result=result,actual_receipt=str(out),actual_receipt_SHA=sha(out),GPU_dispatched=False),indent=2))
        print(json.dumps(dict(passed=True,report=str(p),target=TARGET,source_SHA=admission['source_SHA'],GPU=False)))
    except BaseException:
        (D/'reports'/('S4_FIRST_GATE_TARGET_CPU_PUBLISH_ORIGINAL_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_retry=True)),encoding='utf8');raise
    finally:
        if sf:sf.close()
        t.close(c)
if __name__=='__main__':main()
