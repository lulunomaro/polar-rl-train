"""Separate future dispatch. Requires the genuinely completed target CPU receipt."""
from pathlib import Path
import argparse,json,time,os
import second_root_owned_transport_common_v1 as t
def main():
    a=argparse.ArgumentParser();a.add_argument('--target-cpu-receipt',required=True);a.add_argument('--execute-unique-formal-dispatch',action='store_true');args=a.parse_args()
    assert args.execute_unique_formal_dispatch,'Explicit root-owned future dispatch required; no default connection'
    receipt=json.loads(Path(args.target_cpu_receipt).read_bytes())
    assert receipt['passed'] is True and receipt['targetCPU_complete_GPU_not_dispatched'] is True and receipt['root']==t.ROOT
    assert receipt['source']['sha256']==t.SOURCE_SHA and receipt['actual_sourcefreeze_count']>=522
    assert receipt['manifest']['path']==t.ROOT+'/LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json'
    assert not (t.REPORTS/'SECOND_ROOT_FORMAL_DISPATCH_INTENT.json').exists(),'Prior unknown result must be inspected, never rerun'
    t.write_once(t.REPORTS/'SECOND_ROOT_FORMAL_DISPATCH_INTENT.json',dict(epoch=time.time(),target_CPU_receipt=dict(path=str(Path(args.target_cpu_receipt)),sha256=t.sha(args.target_cpu_receipt)),actual_manifest=receipt['manifest'],PPO_proof_pending=True))
    c=None
    try:
        c=t.connect()
        context=dict(proposed_root=t.ROOT,source_SHA=t.SOURCE_SHA,actual_manifest_SHA=receipt['manifest']['sha256'],python=t.PY)
        out=t.run(c,(t.P/'second_formal_target_dispatch_from_actualmanifest_v1.py').read_text(),'SECOND_ROOT_UNIQUE_FORMAL_DISPATCH_ACTUAL',context)
        target=t.REPORTS/'SECOND_ROOT_UNIQUE_FORMAL_DISPATCH_ACTUAL.json';t.write_once(target,out)
        print(json.dumps(dict(actual_dispatch_receipt=str(target),pid=out['pid'],start_ticks=out['start_ticks'],PPO_proof_pending=True)))
    except BaseException:
        print(json.dumps(dict(original_error=str(t.original_error('SECOND_ROOT_UNIQUE_FORMAL_DISPATCH_ORIGINAL_ERROR')))));raise
    finally:
        if c:c.close()
        os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
