"""Unique actual diagnostic stage. Retains prior annotated objects and all false."""
from pathlib import Path
import importlib, json, sys, subprocess, time
from datetime import datetime, timezone, timedelta

D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap

def main():
    ID='wave50-two-mean-factors-rejected-native-plane-metadata-reviewed'
    note=D/'LEFT_TWO_MEAN_FACTORS_REJECTED_AND_PLANE_QUERY_SOURCE_DIAGNOSIS_STAGE.md'
    dest=REPO/'history/evidence'/D.name/'two_mean_factors_rejected_plane_metadata_stage'
    assert note.exists() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
    decision=json.loads((D/'reports/TWO_MEAN_ONLY_FACTORS_COMPLETE_AND_PRODUCTION_REJECTED_ACTUAL.json').read_bytes())
    assert not decision['factors']['center']['production_adopted'] and not decision['factors']['near_lower']['production_adopted']
    meta=json.loads((W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014/reports/PLANE_METADATA_V7_INDEPENDENT_ACTUAL_CPU_REVIEW.json').read_bytes())
    assert meta['actual_new_metadata_query_consistency_review'] and meta['original_V6_fullcase_failed_unchanged']
    old=cap.a.gitio.refs()
    cap.a.FOLDERS=(D,W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014',W/'MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014',W/'MOD4_3060_LEFT_JOINT_MARGIN014_FACTOR_20261014',W/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014',W/'MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014',W/'MOD4_3060_FULL80_PARAMETER_BOUND_20261014',W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014',W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014',W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014',W/'MOD4_LEFT_REPAIR_RESIDUAL_CPU_20261014',W/'MOD4_LEFT_JOINT_CENTER_KEEPSTD_CPU_20261014',W/'MOD4_3060_LEFT_CENTER_KEEPSTD_FULL80_FACTOR_20261014',W/'MOD4_3060_LEFT_NEAR_LOWER_FULL80_FACTOR_20261014',W/'MOD4_LEFT_HEAD_FEATURE_RESPONSE_CPU_20261014')
    rows,files=cap.capture_streaming(dest)
    sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
    def wrapped(*args):
        if args[:2]==('add','--'):
            p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),capture_output=True,check=True)
            return p.stdout.decode().strip()
        return cap.g(*args)
    rec.git=wrapped
    sys.argv=['record_experiment.py','--id',ID,'--title','Reject both complete mean-only full80 factors and independently review actual native Plane numerical metadata','--kind','diagnosis','--note-file',str(note),'--files',*files,'--validation','Retained whole20k own2b best observed forward22of27/reverse25of27/ordinary0, no50or70 qualification. Complete center same-initial-state full80 factor4of27/0of27/ordinary179 and near-lower0.005rad factor11of27/13of27/ordinary1 rejected; source10799/std/otherheads/criticDRRNG CPU exact, raw/query/contactCOMhardware/6000cb/direct full prefixes independently reviewed. Shared hip-copy relative64feature gradient removal CPU verified, no unique causal claim or new source adopted. Original inherited flat V6 full1500 final ideal-Z1.907e-6 strictreject/EXIT1/missingCOMPLETE retained with independent fullraw salvage; finite batch stopped. New nativeV7 metadata160 zero requested controls/zeroPPO actual USD+actorgetter/source-pinned reference represented query max4.571e-7 under unchanged1e-6, ideal-Z22false retained, actualquery Rngunchanged/PIDout/sharedOSlockfree/EXIT0 plus independent missingEXIT_NATURAL closeout; no shape-local direct read or installedDLLbitexact proof. All original schema/API/reader/draft failures/source/errors/cost and priorstage receipt included, no GPU replay or budget transaction.','--push']
    rec.main()
    tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID
    head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag)
    cap.a.verify(rows,old,head,tag,obj)
    report=D/'reports/TWO_MEAN_REJECTIONS_PLANE_METADATA_STAGE_GIT_RECORDED.json'
    assert not report.exists()
    report.write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),later_receipt_ordinary_supplement_required=True),indent=2),encoding='utf8')
    print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,actual_saved_sources=len(rows))))

if __name__=='__main__':
    main()
