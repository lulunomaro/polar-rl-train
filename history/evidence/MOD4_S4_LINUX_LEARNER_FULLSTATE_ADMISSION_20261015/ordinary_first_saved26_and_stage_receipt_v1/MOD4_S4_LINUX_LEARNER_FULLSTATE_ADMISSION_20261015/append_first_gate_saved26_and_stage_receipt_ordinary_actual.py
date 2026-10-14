"""Append actual positive save/readers/monitor; do not record/tag the stage again."""
from pathlib import Path
import sys,json,time,subprocess
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
cap.a.FOLDERS=(D,)
def main():
    stage=json.loads((D/'reports/S4_JOINT_GATE_FULLSTATE_FIRST_DISPATCH_STAGE_GIT_RECORDED_ACTUAL.json').read_bytes())
    positive=json.loads((D/'reports/S4_FIRST_GATE_OWN_POSITIVE_MODEL25_LOCAL_CPU_VERIFIED.json').read_bytes())
    assert stage['actual_remote_main_tag_peeled_verified'] and positive['passed'] and positive['updates']==26
    assert json.loads((D/'reports/S4_FIRST_GATE_SAVED26_MONITOR_TOML_BYTEEXACT_VERIFIED.json').read_bytes())['passed']
    assert not cap.g('status','--porcelain')
    dest=REPO/'history/evidence'/D.name/'ordinary_first_saved26_and_stage_receipt_v1';assert not dest.exists()
    old=cap.a.gitio.refs();rows,files=cap.capture_streaming(dest)
    subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in files),capture_output=True,check=True)
    cap.g('commit','-m','Append actual S4 gate saved26 PPO, reader phase correction and monitor receipts')
    cap.g('push','origin','HEAD')
    head=cap.g('rev-parse','HEAD');cap.a.verify(rows,old,head)
    print(json.dumps(dict(epoch=time.time(),ordinary_supplement_commit=head,actual_remote_main_verified=True,
        all_old_tag_objects_peeled_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),
        source_stage_tag=stage['tag'],source_stage_commit=stage['commit'],source_stage_tagobject=stage['tagobject'],
        own_saved_PPO_updates=positive['updates'],own_model25_SHA=positive['own_save']['sha256'],
        no_record_tag_training_budget_or_GPU_replay=True,final_verification_tool_output_only_no_infinite_receipt_loop=True)))
if __name__=='__main__':main()
