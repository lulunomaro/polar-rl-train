"""CPU preparation only until root explicitly invokes this future target action."""
from pathlib import Path
import argparse,json,time,os
import second_root_owned_transport_common_v1 as t
def main():
    a=argparse.ArgumentParser();a.add_argument('--decision',required=True);a.add_argument('--execute-target-materialization',action='store_true');args=a.parse_args()
    assert args.execute_target_materialization,'Explicit root-owned future action required; no default connection'
    files,names=t.packet(args.decision)
    assert not (t.REPORTS/'SECOND_ROOT_TARGET_CPU_MATERIALIZE_INTENT.json').exists(),'Inspect prior actual outcome; do not replay'
    t.write_once(t.REPORTS/'SECOND_ROOT_TARGET_CPU_MATERIALIZE_INTENT.json',dict(epoch=time.time(),root=t.ROOT,stage=t.STAGE,files={n:dict(path=str(p),sha256=t.sha(p),bytes=p.stat().st_size) for n,p in files.items()},no_GPU_dispatch=True,no_budget_write=True))
    c=None;sftp=None
    try:
        c=t.connect()
        code="from pathlib import Path\nimport json,os\ns=Path(CONTEXT['stage']);r=Path(CONTEXT['proposed_root'])\nassert Path('/proc').is_dir() and not r.exists() and not s.exists()\nassert s.parent.is_dir()\ns.mkdir();print(json.dumps(dict(stage=str(s),GPU_dispatched=False)))\n"
        t.run(c,code,'SECOND_ROOT_NEW_CPU_STAGE_ACTUAL',dict(stage=t.STAGE,proposed_root=t.ROOT))
        sftp=c.open_sftp()
        for n,p in files.items():sftp.put(str(p),t.STAGE+'/'+n)
        sftp.close();sftp=None
        context=dict(stage=t.STAGE,proposed_root=t.ROOT,source_SHA=t.SOURCE_SHA,uploaded_SHA={n:t.sha(p) for n,p in files.items()},evidence_uploaded_names=names)
        out=t.run(c,(t.P/'second_source_target_materialize_CPU_v1.py').read_text(),'SECOND_ROOT_TARGET_CPU_MATERIALIZE_ACTUAL',context)
        assert out['passed'] is True and out['targetCPU_complete_GPU_not_dispatched'] is True
        target=t.REPORTS/'SECOND_ROOT_TARGET_CPU_MATERIALIZATION_COMPLETE.json';t.write_once(target,out)
        print(json.dumps(dict(actual_target_CPU_receipt=str(target),root=t.ROOT,manifest=out['manifest'],GPU_dispatched=False)))
    except BaseException:
        print(json.dumps(dict(original_error=str(t.original_error('SECOND_ROOT_TARGET_CPU_MATERIALIZE_ORIGINAL_ERROR')))));raise
    finally:
        if sftp:sftp.close()
        if c:c.close()
        os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
